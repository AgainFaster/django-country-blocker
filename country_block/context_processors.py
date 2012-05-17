import settings
from django.contrib.gis.utils.geoip import GeoIP

def addgeoip(request):
    """
    Context Processor based on Adam Fasts blog post "Where is my user Part 1"
    http://blog.adamfast.com/2011/11/where-is-my-user-part-1-geoip/
    adds users country and a boolean indicating whether or not the user is in a list of
    allowed countries
    """
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META.get('REMOTE_ADDR', False)

    server_location  = getattr(settings, 'LOCATION', None)
    allowed_countries = getattr(settings, 'COUNTRY_BLOCK_ALLOWED_COUNTRIES', server_location)

    if ip or not server_location:
        user_country = GeoIP().country_code(ip)

        if user_country:
            user_country = user_country.upper()

        if getattr(settings, 'COUNTRY_BLOCK_DEBUG', False):
            user_country = allowed_countries[0]

        return {'country': user_country,
                'in_country' : bool(user_country in allowed_countries)}
    else:
        return {}