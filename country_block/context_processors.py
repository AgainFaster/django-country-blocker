from django.conf import settings
try:
    from django.contrib.gis.geoip import GeoIP
except:
    from django.contrib.gis.utils.geoip import GeoIP

import logging

logger = logging.getLogger(__name__)
def addgeoip(request):
    """
    Context Processor based on Adam Fasts blog post "Where is my user Part 1"
    http://blog.adamfast.com/2011/11/where-is-my-user-part-1-geoip/
    adds users country and a boolean indicating whether or not the user is in a list of
    allowed countries
    """
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR'].split(",")[0]
    else:
        ip = request.META.get('REMOTE_ADDR', False)


    #what country should the server be set to
    server_location  = getattr(settings, 'LOCATION', None)
    #countries that are allowed to see content
    allowed_countries = getattr(settings, 'COUNTRY_BLOCK_ALLOWED_COUNTRIES', server_location)

    #if the visiting user has staff status, let them see everything
    if hasattr(request, 'user'):
        if request.user.is_staff:
            return {'country' : 'Staff Overwrite',
                    'in_country' : True}

    if ip or not server_location:
        user_country = GeoIP().country_code(ip)
        logger.info("User %s is in %s" % (ip, user_country))

        if user_country:
            user_country = user_country.upper()

        if getattr(settings, 'COUNTRY_BLOCK_DEBUG', False):
            user_country = allowed_countries[0]

        ret_dict = {'country': user_country,
                    'in_country' : bool(user_country in allowed_countries)}
        logger.info("Returning: %s" % ret_dict)
        return ret_dict
    else:
        return {}
