from django.core.cache import cache
from django.db import models

class Country(models.Model):
    country_code = models.CharField(max_length=2, unique=True) # ISO standard
    country_name = models.CharField(max_length=100, default="")

    def save(self, *args, **kwargs):
        super(Country, self).save(*args, **kwargs)
        cache.delete('country_block_settings')
        cache.delete('country_block_allowed_countries')

    def __unicode__(self):
        return "(%s) %s" % (self.country_code, self.country_name)

class Settings(models.Model):
    location = models.CharField(max_length=2, unique=True)
    free_geo_ip_enabled = models.BooleanField(default=True)
    maxmind_enabled = models.BooleanField(default=True)
    maxmind_local_db_enabled = models.BooleanField(default=False)
    maxmind_license_key = models.CharField(max_length=25, default="")
    allowed_countries = models.ManyToManyField(Country)

    staff_user_country = models.ForeignKey(Country, related_name='staff_user_settings')
    local_ip_user_country = models.ForeignKey(Country, related_name='local_ip_user_settings')

    def save(self, *args, **kwargs):
        super(Settings, self).save(*args, **kwargs)
        cache.delete('country_block_settings')
        cache.delete('country_block_allowed_countries')

    def __unicode__(self):
        return "%s settings" % self.location