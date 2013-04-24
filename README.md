django-country-blocker
======================

Django app introducing a Context Processor that adds users location information to the context.

To activate, add country_block.context_processors.addgeoip to your CONTEXT_MODIFIERS.
This will give you a user_country variable in your context with the users country code,
and a in_country boolean set to True is the country matches one of the allowed countries.

Settings options
================
COUNTRY_BLOCK_ALLOWED_COUNTRIES : list of country codes that will trigger in_country == True if it contains
the user's country code

COUNTRY_BLOCK_DEBUG_COUNTRY : sets the user_country equal to this value for all users, letting you test as if you are in
this country. False by default.

COUNTRY_BLOCK_DEBUG_REGION : sets the region_code equal to this value for all users, letting you test as if you are in
this region. False by default.

COUNTRY_BLOCK_DEBUG : sets the user_country equal to the first allowed country in the list,
letting you test as if you are in the first allowed country. False by default.

COUNTRY_BLOCK_DEBUG_OUT_OF_COUNTRY : sets the user_country to a non-allowed (non-existent) country,
letting you test as if you are in the non-allowed country. False by default.

COUNTRY_BLOCK_SERVICES : list of services which can contain "MAXMIND" and/or "FREEGEOIP". If both "MAXMIND" and
"FREEGEOIP" are configured, the processor will try using the freegeoip.net service first and fall back on executing the
Maxmind code if freegeoip fails for some reason. The COUNTRY_BLOCK_SERVICES list contains only "MAXMIND" by default.

MAXMIND_USE_LOCAL_DB : If this is True, use the django.contrib.gis.geoip.GeoIP module instead of the
https://geoip.maxmind.com/a service which requires a local Maxmind database. True is required if COUNTRY_BLOCK_SERVICES
contains "MAXMIND" and you do not wish to use the https://geoip.maxmind.com/a service. False by default.

MAXMIND_LICENSE_KEY : The license key for Maxmind. A value is required if COUNTRY_BLOCK_SERVICES contains "MAXMIND"
and MAXMIND_USE_LOCAL_DB is False. This gets sent over as the 'l' parameter in the payload to
https://geoip.maxmind.com/a
