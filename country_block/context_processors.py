import csv
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from raven.contrib.django.models import client
import re
import requests
from django.conf import settings
import sys
from country_block.models import Settings as CountryBlockSettings, ErrorLog
from datetime import datetime, timedelta

try:
    from django.contrib.gis.geoip import GeoIP
except:
    from django.contrib.gis.utils.geoip import GeoIP

import logging

logger = logging.getLogger(__name__)
NO_COUNTRY = '00'
COUNTRY_BLOCK_SETTINGS_KEY = 'country_block_settings'
COUNTRY_BLOCK_ALLOWED_COUNTRIES_KEY = 'country_block_allowed_countries'

def get_settings():
    server_location = getattr(settings, 'LOCATION', None)

    if not server_location:
        raise ImproperlyConfigured

    cb_settings = cache.get(COUNTRY_BLOCK_SETTINGS_KEY)
    if not cb_settings:
        try:
            cb_settings = CountryBlockSettings.objects.prefetch_related('allowed_countries').get(location=server_location)
        except CountryBlockSettings.DoesNotExist:
            raise ImproperlyConfigured

        cache.set(COUNTRY_BLOCK_SETTINGS_KEY, cb_settings, 60*60*24*7)

    allowed_countries = cache.get(COUNTRY_BLOCK_ALLOWED_COUNTRIES_KEY)
    if not allowed_countries:
        allowed_countries = cb_settings.allowed_countries.all()
        cache.set(COUNTRY_BLOCK_ALLOWED_COUNTRIES_KEY, allowed_countries, 60*60*24*7)

    if not allowed_countries:
        raise ImproperlyConfigured

    return cb_settings, allowed_countries

def log_error(request, message, extra=None):
    logger.info("(Error) %s\n" % message)
    data = client.get_data_from_request(request)
    data.update({
        'level': logging.ERROR,
        })

    client.capture('Message',
                   message=message,
                   data=data,
                   extra=extra)


def manage_freegeoip_error():

    cb_settings, allowed_countries = get_settings()

    # default these values in case they are not already in the cached cb_settings
    free_geo_ip_error_window = getattr(cb_settings, 'free_geo_ip_error_window', 3600.00)
    free_geo_ip_error_threshold = getattr(cb_settings, 'free_geo_ip_error_threshold', 10)
    free_geo_ip_error_sleep = getattr(cb_settings, 'free_geo_ip_error_sleep', 3600.00)

    oldest_error = datetime.now() - timedelta(seconds=free_geo_ip_error_window)
    ErrorLog.objects.filter(type='freegeoip', created__lt=oldest_error).delete()
    ErrorLog.objects.create(type='freegeoip')

    if ErrorLog.objects.filter(type='freegeoip').count() > free_geo_ip_error_threshold:
        # disable freegeoip in cache for an hour
        cb_settings.free_geo_ip_enabled = False
        cache.set(COUNTRY_BLOCK_SETTINGS_KEY, cb_settings, free_geo_ip_error_sleep)
        logger.info("FreeGeoIP error threshold of %s has been reached. Service will sleep for %s seconds."
                    % (free_geo_ip_error_threshold, free_geo_ip_error_sleep))


def get_info_from_freegeoip(request, ip, timeout):

    url = "http://freegeoip.net/json/%s" % ip

    try:
        response = requests.get(url=url, timeout=timeout)
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        message = "FreeGeoIP request exception: %s" % e
        extra = {'url': url,
                 'ip': ip,}

        log_error(request, message=message, extra=extra)

        manage_freegeoip_error()

        return False, False

    if response.status_code != requests.codes.ok:
        message='FreeGeoIP request failed with status: %s' % response.status_code
        extra = {
            'url': url,
            'ip': ip,
            'response': response.text,
            }

        log_error(request, message=message, extra=extra)
        return False, False

    dict = response.json()
    if not dict:
        message = "FreeGeoIP JSON dictionary is empty."
        extra = {
            'url': url,
            'ip': ip,
            'response': response.text,
            }

        log_error(request, message=message, extra=extra)
        return False, False

    logger.info("FreeGeoIP JSON data for %s\n\n" % ip)
    for (key, val) in dict.items():
        logger.info("  %-20s  %s" % (key, val))
    logger.info("\n")
    return dict.get("country_code"), dict.get("region_code")

def get_info_from_maxmind(request, ip, license_key, timeout):

    fields = ['country_code',
              # 'country_name',
              # 'region_code',
              # 'region_name',
              # 'city_name',
              # 'latitude',
              # 'longitude',
              # 'metro_code',
              # 'area_code',
              # 'time_zone',
              # 'continent_code',
              # 'postal_code',
              # 'isp_name',
              # 'organization_name',
              # 'domain',
              # 'as_number',
              # 'netspeed',
              # 'user_type',
              # 'accuracy_radius',
              # 'country_confidence',
              # 'city_confidence',
              # 'region_confidence',
              # 'postal_confidence',
              'error']

    if not license_key:
        raise ImproperlyConfigured

    payload = {'l': license_key, 'i': ip}
    url = 'https://geoip.maxmind.com/a'

    try:
        response = requests.get(url, params=payload, timeout=timeout)
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        message = "Maxmind request exception: %s" % e
        extra = {'url': url,
                 'payload': payload,
                 'ip': ip,}

        log_error(request, message=message, extra=extra)
        return False, False

    if response.status_code != requests.codes.ok:
        message = "Maxmind request failed with status %s" % response.status_code
        extra = {
            'url': url,
            'payload': payload,
            'ip': ip,
            'response': response.text,
            }

        log_error(request, message=message, extra=extra)
        return False, False
    reader = csv.reader([response.content])

    omni = dict(zip(fields, [unicode(s, 'latin_1') for s in reader.next()]))
    if "error" in omni:
        message = "MaxMind returned an error code for the request: %s" % omni['error']
        extra ={
            'url': url,
            'payload': payload,
            'ip': ip,
            'response': response.text,
            'omni': omni,
            }

        log_error(request, message=message, extra=extra)
        return False, False

    logger.info("MaxMind Omni data for %s\n\n" % ip)
    for (key, val) in omni.items():
        logger.info("  %-20s  %s" % (key, val))
    logger.info("\n")
    return omni.get("country_code"), False

def create_dictionary(request, user_country, region_code, message=None):
    cb_settings, allowed_countries = get_settings()

    if user_country:
        user_country = user_country.upper()
        # special case for reserved IP, e.g. 192.168.1.1, 10.181.1.1
        if user_country == 'RD':
            user_country = cb_settings.local_ip_user_country.country_code
            message = 'LOCAL_RESERVED_IP'
    else:
        # an error should already be logged at this point
        user_country = NO_COUNTRY

    if region_code:
        region_code = region_code.upper()
    else:
        region_code = None

    ret_dict = {'country': user_country,
                'region': region_code,
                'in_country': allowed_countries.filter(country_code=user_country).exists()}

    if message:
        logger.info("(%s) Returning: %s" % (message, ret_dict))
    else:
        logger.info("Returning: %s" % ret_dict)

    if user_country != NO_COUNTRY and hasattr(request, "session"):
        request.session['country'] = user_country
        request.session['region'] = region_code

    return ret_dict

def addgeoip(request):
    """
    Context Processor based on Adam Fasts blog post "Where is my user Part 1"
    http://blog.adamfast.com/2011/11/where-is-my-user-part-1-geoip/
    adds users country and a boolean indicating whether or not the user is in a list of
    allowed countries
    """

    region_code = None

    try:
        cb_settings, allowed_countries = get_settings()
    except ImproperlyConfigured:
        ret_dict = {'country': NO_COUNTRY, 'region': None, 'in_country': False}
        logger.info("(IMPROPERLY_CONFIGURED) Returning: %s" % ret_dict)
        return ret_dict

    if getattr(settings, 'COUNTRY_BLOCK_DEBUG_REGION', False):
        region_code = settings.COUNTRY_BLOCK_DEBUG_REGION

    if getattr(settings, 'COUNTRY_BLOCK_DEBUG_COUNTRY', False):
        return create_dictionary(request, settings.COUNTRY_BLOCK_DEBUG_COUNTRY, region_code, 'COUNTRY_BLOCK_DEBUG_COUNTRY')

    #if the visiting user has staff status, let them see everything
    if hasattr(request, "user") and request.user.is_staff:
        return create_dictionary(request, cb_settings.staff_user_country.country_code, region_code, 'STAFF_USER')

    if hasattr(request, "session") and "country" in request.session and "region" in request.session:
        return create_dictionary(request, request.session['country'], request.session['region'], 'IN_SESSION')

    if 'HTTP_X_CLUSTER_CLIENT_IP' in request.META:
        ip = request.META.get('HTTP_X_CLUSTER_CLIENT_IP', False)
    elif 'HTTP_X_FORWARDED_FOR' in request.META:
        # get the last HTTP_X_FORWARDED_FOR ip address
        # the format is "client, proxy1, proxy2", so we want the last proxy because the client may be a reserved ip
        ip_addresses = request.META.get('HTTP_X_FORWARDED_FOR').split(",")
        ip = ip_addresses[len(ip_addresses)-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', False)

    logger.debug("User with IP: %s" % ip)

    if ip:
        if ip == "127.0.0.1" or re.match("^192.168.\d{1,3}\.\d{1,3}$", ip):
            return create_dictionary(request, cb_settings.local_ip_user_country.country_code, region_code, 'LOCAL_IP')

        user_country = None

        # Always try FREEGEOIP first if configured
        if cb_settings.free_geo_ip_enabled:
            user_country, region_code = get_info_from_freegeoip(request, ip, cb_settings.free_geo_ip_timeout)

        # If MAXMIND is configured and FREEGEOIP is not configured or failed, try MAXMIND
        if not user_country and cb_settings.maxmind_enabled:
            if cb_settings.maxmind_local_db_enabled:
                user_country = GeoIP().country_code(ip)
                region_code = None
            else:
                user_country, region_code = get_info_from_maxmind(request, ip, cb_settings.maxmind_license_key, cb_settings.maxmind_timeout)

        logger.info("User %s is in %s / %s" % (ip, user_country, region_code))

        return create_dictionary(request, user_country, region_code, 'FOUND_BY_SERVICE')
    else:
        return create_dictionary(request, NO_COUNTRY, None, 'NO_IP')
