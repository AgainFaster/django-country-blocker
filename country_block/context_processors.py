import csv
from django.core.exceptions import ImproperlyConfigured
from raven.contrib.django.models import client
import re
import requests
from django.conf import settings
import sys
from country_block.models import Settings

try:
    from django.contrib.gis.geoip import GeoIP
except:
    from django.contrib.gis.utils.geoip import GeoIP

import logging

logger = logging.getLogger(__name__)
NO_COUNTRY = '00'

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

def get_info_from_freegeoip(request, ip):

    url = "http://freegeoip.net/json/%s" % ip

    try:
        response = requests.get(url=url)
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        message = "FreeGeoIP request exception: %s" % e
        extra = {'url': url,
                 'ip': ip,}

        log_error(request, message=message, extra=extra)
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

def get_info_from_maxmind(request, ip, license_key):

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
        response = requests.get(url, params=payload)
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

def create_dictionary(request, user_country, region_code, allowed_countries, message=None):
    if user_country:
        user_country = user_country.upper()
        # special case for reserved IP, e.g. 192.168.1.1
        if user_country == 'RD':
            user_country = allowed_countries[0]
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

    #what country should the server be set to
    server_location = getattr(settings, 'LOCATION', None)

    if not server_location:
        raise ImproperlyConfigured

    try:
        server_settings = Settings.objects.prefetch_related('allowed_countries').get(location=server_location)
    except Settings.DoesNotExist:
        raise ImproperlyConfigured

    #countries that are allowed to see content
    allowed_countries = server_settings.allowed_countries.all()

    if not allowed_countries:
        raise ImproperlyConfigured

    region_code = None

    if getattr(settings, 'COUNTRY_BLOCK_DEBUG_REGION', False):
        region_code = settings.COUNTRY_BLOCK_DEBUG_REGION

    if getattr(settings, 'COUNTRY_BLOCK_DEBUG_COUNTRY', False):
        return create_dictionary(request, settings.COUNTRY_BLOCK_DEBUG_COUNTRY, region_code, allowed_countries, 'COUNTRY_BLOCK_DEBUG_COUNTRY')

    #if the visiting user has staff status, let them see everything
    if hasattr(request, "user") and request.user.is_staff:
        return create_dictionary(request, server_settings.staff_user_country.country_code, region_code, allowed_countries, 'STAFF_USER')

    if hasattr(request, "session") and "country" in request.session and "region" in request.session:
        return create_dictionary(request, request.session['country'], request.session['region'], allowed_countries, 'IN_SESSION')

    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META.get('HTTP_X_FORWARDED_FOR').split(",")[0]
    else:
        ip = request.META.get('REMOTE_ADDR', False)

    logger.debug("User with IP: %s" % ip)

    if ip:
        if ip == "127.0.0.1" or re.match("^192.168.\d{1,3}\.\d{1,3}$", ip):
            return create_dictionary(request, server_settings.local_ip_user_country.country_code, region_code, allowed_countries, 'LOCAL_IP')

        user_country = None

        # Always try FREEGEOIP first if configured
        if server_settings.free_geo_ip_enabled:
            user_country, region_code = get_info_from_freegeoip(request, ip)

        # If MAXMIND is configured and FREEGEOIP is not configured or failed, try MAXMIND
        if not user_country and server_settings.maxmind_enabled:
            if server_settings.maxmind_local_db_enabled:
                user_country = GeoIP().country_code(ip)
                region_code = None
            else:
                user_country, region_code = get_info_from_maxmind(request, ip, server_settings.maxmind_license_key)

        logger.info("User %s is in %s / %s" % (ip, user_country, region_code))

        return create_dictionary(request, user_country, region_code, allowed_countries, 'FOUND_BY_SERVICE')
    else:
        return create_dictionary(request, NO_COUNTRY, None, allowed_countries, 'NO_IP')
