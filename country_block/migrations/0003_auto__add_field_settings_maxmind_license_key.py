# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Settings.maxmind_license_key'
        db.add_column('country_block_settings', 'maxmind_license_key',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=25),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Settings.maxmind_license_key'
        db.delete_column('country_block_settings', 'maxmind_license_key')


    models = {
        'country_block.country': {
            'Meta': {'object_name': 'Country'},
            'country_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'country_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'country_block.settings': {
            'Meta': {'object_name': 'Settings'},
            'allowed_countries': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['country_block.Country']", 'symmetrical': 'False'}),
            'free_geo_ip_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_ip_user_country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'local_ip_user_settings'", 'to': "orm['country_block.Country']"}),
            'location': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'maxmind_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'maxmind_license_key': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '25'}),
            'maxmind_local_db_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'staff_user_country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'staff_user_settings'", 'to': "orm['country_block.Country']"})
        }
    }

    complete_apps = ['country_block']