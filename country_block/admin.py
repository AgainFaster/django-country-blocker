from django.contrib import admin
from country_block.models import Country, Settings, ErrorLog


class CountryAdmin(admin.ModelAdmin):
    ordering = ["country_code"]

class SettingsAdmin(admin.ModelAdmin):
    filter_horizontal = ('allowed_countries', )

class ErrorLogAdmin(admin.ModelAdmin):
    pass

admin.site.register(Country, CountryAdmin)
admin.site.register(Settings, SettingsAdmin)
admin.site.register(ErrorLog, ErrorLogAdmin)
