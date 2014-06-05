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

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"

class Settings(models.Model):
    location = models.CharField(max_length=2, unique=True)
    free_geo_ip_enabled = models.BooleanField(default=True)
    maxmind_enabled = models.BooleanField(default=True)
    maxmind_local_db_enabled = models.BooleanField(default=False)
    maxmind_license_key = models.CharField(max_length=25, default="")
    allowed_countries = models.ManyToManyField(Country)
    free_geo_ip_timeout = models.FloatField(default=2.00, help_text="Timeout for requests to freegeoip (in seconds)")
    free_geo_ip_error_window = models.FloatField(default=3600.00, help_text="Length of time (in seconds) in which to count freegeoip errors.")
    free_geo_ip_error_threshold = models.IntegerField(default=10, help_text="Temporarily disable freegeoip when the error count exceeds this number.")
    free_geo_ip_error_sleep = models.FloatField(default=3600.00, help_text="Length of time (in seconds) for which freegeoip will be disabled once the error threshold is hit.")
    maxmind_timeout = models.FloatField(default=6.00, help_text="Timeout for requests to maxmind")

    staff_user_country = models.ForeignKey(Country, related_name='staff_user_settings')
    local_ip_user_country = models.ForeignKey(Country, related_name='local_ip_user_settings')

    def save(self, *args, **kwargs):
        super(Settings, self).save(*args, **kwargs)
        cache.delete('country_block_settings')
        cache.delete('country_block_allowed_countries')

    def __unicode__(self):
        return "%s settings" % self.location

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"


class ErrorLog(models.Model):
    type = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s - %s" % (self.type, self.created)
