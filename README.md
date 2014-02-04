[![Latest Version](https://pypip.in/v/django-country-blocker/badge.png)](https://pypi.python.org/pypi/django-country-blocker/)
[![Downloads](https://pypip.in/d/django-country-blocker/badge.png)](https://pypi.python.org/pypi/django-country-blocker/)

django-country-blocker
======================

Django app introducing a Context Processor that adds users location information to the context.

To activate, add country_block.context_processors.addgeoip to your CONTEXT_MODIFIERS.
This will give you a user_country variable in your context and a country variable in the user's session
with the user's 2 character ISO country code, and an in_country boolean set to True is the country matches one of
the allowed countries.

==========================================================
Local Settings options
==========================================================

LOCATION : a unique 2 char string that identifies the server's location

COUNTRY_BLOCK_DEBUG_COUNTRY : sets the user_country equal to this value for all users, letting you test as if you are in
this country. False by default.

COUNTRY_BLOCK_DEBUG_REGION : sets the region_code equal to this value for all users, letting you test as if you are in
this region. False by default.

==========================================================
Database Settings options (country_block.Settings model)
==========================================================

location : This is a unique 2 char value that corresponds to the LOCATION value in the local settings

free_geo_ip_enabled : Use the freegeoip.net to determine the geography of the user's IP

free_geo_ip_timeout : freegeoip.net request timeout in seconds (default is 2 seconds)

maxmind_enabled : Use the https://geoip.maxmind.com/a service to determine the geography of the user's IP.
If this is True and free_geo_ip_enabled is also True, the context processor will try the freegeoip.net service first
and will only try the Maxmind service if freegeoip.net fails.

maxmind_timeout : maxmind.com request timeout in seconds (default is 6 seconds)

maxmind_local_db_enabled : Use a local Maxmind database instead of the https://geoip.maxmind.com/a service. Must also
have maxmind_enabled set to True.

allowed_countries : A M2M relationship of all Countrys that are allowed for the server's location

staff_user_country : The Country that all django staff users will be assigned

local_ip_user_country : The Country that all local IP users will be assigned

maxmind_license_key : The license key for the Maxmind service. A value is required if maxmind_enabled is True
and maxmind_local_db_enabled is False. This gets sent over as the 'l' parameter in the payload to the
https://geoip.maxmind.com/a service.
