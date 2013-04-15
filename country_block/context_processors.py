import csv
from django.core.exceptions import ImproperlyConfigured
from raven.contrib.django.models import client
import re
import requests
from django.conf import settings
import sys

try:
    from django.contrib.gis.geoip import GeoIP
except:
    from django.contrib.gis.utils.geoip import GeoIP

import logging

logger = logging.getLogger(__name__)


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
        return False

    if response.status_code != requests.codes.ok:
        message='FreeGeoIP request failed with status: %s' % response.status_code
        extra = {
            'url': url,
            'ip': ip,
            'response': response.text,
            }

        log_error(request, message=message, extra=extra)
        return False

    dict = response.json()
    if not dict:
        message = "FreeGeoIP JSON dictionary is empty."
        extra = {
            'url': url,
            'ip': ip,
            'response': response.text,
            }

        log_error(request, message=message, extra=extra)
        return False

    logger.info("FreeGeoIP JSON data for %s\n\n" % ip)
    for (key, val) in dict.items():
        logger.info("  %-20s  %s" % (key, val))
    logger.info("\n")
    return dict.get("country_code")

def get_info_from_maxmind(request, ip):

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

    LICENSE_KEY = getattr(settings, "MAXMIND_LICENSE_KEY", False)
    if not LICENSE_KEY:
        raise ImproperlyConfigured

    payload = {'l': LICENSE_KEY, 'i': ip}
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
        return False

    if response.status_code != requests.codes.ok:
        message = "Maxmind request failed with status %s" % response.status_code
        extra = {
            'url': url,
            'payload': payload,
            'ip': ip,
            'response': response.text,
            }

        log_error(request, message=message, extra=extra)
        return False
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
        return False

    logger.info("MaxMind Omni data for %s\n\n" % ip)
    for (key, val) in omni.items():
        logger.info("  %-20s  %s" % (key, val))
    logger.info("\n")
    return omni.get("country_code")

def addgeoip(request):
    """
    Context Processor based on Adam Fasts blog post "Where is my user Part 1"
    http://blog.adamfast.com/2011/11/where-is-my-user-part-1-geoip/
    adds users country and a boolean indicating whether or not the user is in a list of
    allowed countries
    """

    #what country should the server be set to
    server_location = getattr(settings, 'LOCATION', None)
    #countries that are allowed to see content
    allowed_countries = getattr(settings, 'COUNTRY_BLOCK_ALLOWED_COUNTRIES', server_location)

    if not server_location:
        raise ImproperlyConfigured

    if getattr(settings, 'COUNTRY_BLOCK_DEBUG_OUT_OF_COUNTRY', False):
        ret_dict = {'country': "DEBUG FAKE OUT OF COUNTRY",
                    'in_country': False}
        logger.info("(Debug) Returning: %s" % ret_dict)
        return ret_dict

    if getattr(settings, 'COUNTRY_BLOCK_DEBUG', False):
        ret_dict = {'country': "DEBUG",
                    'in_country': True}
        logger.info("(Debug) Returning: %s" % ret_dict)
        return ret_dict

    #if the visiting user has staff status, let them see everything
    if hasattr(request, "user") and request.user.is_staff:
        ret_dict = {'country': 'Staff Overwrite',
                    'in_country': True}
        logging.debug("(Staff Overwrite) Returning %s" % ret_dict)
        return ret_dict

    if hasattr(request, "session") and "country" in request.session:
        ret_dict = {'country': request.session['country'],
                    'in_country': bool(request.session['country'] in allowed_countries)
                                    or request.session['country'] == 'RD'}
        logger.info("(Cookie) Returning: %s" % ret_dict)
        return ret_dict

    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META.get('HTTP_X_FORWARDED_FOR').split(",")[0]
    else:
        ip = request.META.get('REMOTE_ADDR', False)

    logger.debug("User with IP: %s" % ip)

    if ip:
        if ip == "127.0.0.1":
            ret_dict = {'country': "LOCAL",
                        'in_country': True}
            logger.info("(Local) Returning: %s" % ret_dict)
            return ret_dict

        if re.match("^192.168.\d{1,3}\.\d{1,3}$", ip):
            ret_dict = {'country': "LOCAL_RESERVED_IP",
                        'in_country': True}
            logger.info("(Local Reserved) Returning: %s" % ret_dict)
            return ret_dict

        # Possible choices: FREEGEOIP, MAXMIND... default is just MAXMIND
        SERVICES = getattr(settings, "COUNTRY_BLOCK_SERVICES", ("MAXMIND",))
        user_country = None

        # Always try FREEGEOIP first if configured
        if 'FREEGEOIP' in SERVICES:
            user_country = get_info_from_freegeoip(request, ip)

        # If MAXMIND is configured and FREEGEOIP is not configured or failed, try MAXMIND
        if not user_country and 'MAXMIND' in SERVICES:
            if getattr(settings, "MAXMIND_USE_LOCAL_DB", False):
                user_country = GeoIP().country_code(ip)
            else:
                user_country = get_info_from_maxmind(request, ip)

        logger.info("User %s is in %s" % (ip, user_country))

        if user_country:
            user_country = user_country.upper()
        else:
            # an error should already be logged at this point
            user_country = "NO_COUNTRY_FOUND"

        ret_dict = {'country': user_country,
                    'in_country': bool(user_country in allowed_countries)
                                    or user_country == 'RD'}

        if hasattr(request, "session"):
            request.session['country'] = user_country
        logger.info("(Fetched) Returning: %s" % ret_dict)
        return ret_dict
    else:
        ret_dict = {'country': "NOIP",
                    'in_country': False}
        return ret_dict
