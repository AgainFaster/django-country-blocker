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
COUNTRY_BLOCK_DEBUG : sets the user_country equal to an allowed country,
letting you test as if you are in the allowed country. False by default