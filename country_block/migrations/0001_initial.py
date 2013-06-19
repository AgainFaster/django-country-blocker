# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Country'
        db.create_table('country_block_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2)),
            ('country_name', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
        ))
        db.send_create_signal('country_block', ['Country'])

        # Adding model 'Settings'
        db.create_table('country_block_settings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2)),
            ('free_geo_ip_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('maxmind_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('maxmind_local_db_enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('staff_user_country', self.gf('django.db.models.fields.related.ForeignKey')(related_name='staff_user_settings', to=orm['country_block.Country'])),
            ('local_ip_user_country', self.gf('django.db.models.fields.related.ForeignKey')(related_name='local_ip_user_settings', to=orm['country_block.Country'])),
        ))
        db.send_create_signal('country_block', ['Settings'])

        # Adding M2M table for field allowed_countries on 'Settings'
        db.create_table('country_block_settings_allowed_countries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('settings', models.ForeignKey(orm['country_block.settings'], null=False)),
            ('country', models.ForeignKey(orm['country_block.country'], null=False))
        ))
        db.create_unique('country_block_settings_allowed_countries', ['settings_id', 'country_id'])


    def backwards(self, orm):
        # Deleting model 'Country'
        db.delete_table('country_block_country')

        # Deleting model 'Settings'
        db.delete_table('country_block_settings')

        # Removing M2M table for field allowed_countries on 'Settings'
        db.delete_table('country_block_settings_allowed_countries')


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
            'maxmind_local_db_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'staff_user_country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'staff_user_settings'", 'to': "orm['country_block.Country']"})
        }
    }

    complete_apps = ['country_block']