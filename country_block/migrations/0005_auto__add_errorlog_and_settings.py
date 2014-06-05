# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ErrorLog'
        db.create_table('country_block_errorlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('country_block', ['ErrorLog'])

        # Adding field 'Settings.free_geo_ip_error_window'
        db.add_column('country_block_settings', 'free_geo_ip_error_window',
                      self.gf('django.db.models.fields.FloatField')(default=3600.0),
                      keep_default=False)

        # Adding field 'Settings.free_geo_ip_error_threshold'
        db.add_column('country_block_settings', 'free_geo_ip_error_threshold',
                      self.gf('django.db.models.fields.IntegerField')(default=10),
                      keep_default=False)

        # Adding field 'Settings.free_geo_ip_error_sleep'
        db.add_column('country_block_settings', 'free_geo_ip_error_sleep',
                      self.gf('django.db.models.fields.FloatField')(default=3600.0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ErrorLog'
        db.delete_table('country_block_errorlog')

        # Deleting field 'Settings.free_geo_ip_error_window'
        db.delete_column('country_block_settings', 'free_geo_ip_error_window')

        # Deleting field 'Settings.free_geo_ip_error_threshold'
        db.delete_column('country_block_settings', 'free_geo_ip_error_threshold')

        # Deleting field 'Settings.free_geo_ip_error_sleep'
        db.delete_column('country_block_settings', 'free_geo_ip_error_sleep')


    models = {
        'country_block.country': {
            'Meta': {'object_name': 'Country'},
            'country_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'country_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'country_block.errorlog': {
            'Meta': {'object_name': 'ErrorLog'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'country_block.settings': {
            'Meta': {'object_name': 'Settings'},
            'allowed_countries': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['country_block.Country']", 'symmetrical': 'False'}),
            'free_geo_ip_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'free_geo_ip_error_sleep': ('django.db.models.fields.FloatField', [], {'default': '3600.0'}),
            'free_geo_ip_error_threshold': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'free_geo_ip_error_window': ('django.db.models.fields.FloatField', [], {'default': '3600.0'}),
            'free_geo_ip_timeout': ('django.db.models.fields.FloatField', [], {'default': '2.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_ip_user_country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'local_ip_user_settings'", 'to': "orm['country_block.Country']"}),
            'location': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'maxmind_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'maxmind_license_key': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '25'}),
            'maxmind_local_db_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'maxmind_timeout': ('django.db.models.fields.FloatField', [], {'default': '6.0'}),
            'staff_user_country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'staff_user_settings'", 'to': "orm['country_block.Country']"})
        }
    }

    complete_apps = ['country_block']