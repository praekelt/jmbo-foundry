# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        connection = db._get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute('select raw_field_order from preferences_registrationpreferences')
            connection.close()
        except:
            connection.close()
            # Adding field 'RegistrationPreferences.raw_field_order'
            db.add_column('preferences_registrationpreferences', 'raw_field_order',
                        self.gf('django.db.models.fields.CharField')(default='{}', max_length=1024, blank=True),
                        keep_default=False)


    def backwards(self, orm):
        # Deleting field 'RegistrationPreferences.raw_field_order'
        db.delete_column('preferences_registrationpreferences', 'raw_field_order')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'preferences.bannerpreferences': {
            'Meta': {'object_name': 'BannerPreferences', '_ormbases': ['preferences.Preferences']},
            'preferences_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preferences.Preferences']", 'unique': 'True', 'primary_key': 'True'})
        },
        'preferences.competitionpreferences': {
            'Meta': {'object_name': 'CompetitionPreferences', '_ormbases': ['preferences.Preferences']},
            'preferences_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preferences.Preferences']", 'unique': 'True', 'primary_key': 'True'}),
            'rules': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'})
        },
        'preferences.contactpreferences': {
            'Meta': {'object_name': 'ContactPreferences', '_ormbases': ['preferences.Preferences']},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'email_recipients': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '24', 'null': 'True', 'blank': 'True'}),
            'physical_address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'postal_address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'preferences_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preferences.Preferences']", 'unique': 'True', 'primary_key': 'True'}),
            'sms': ('django.db.models.fields.CharField', [], {'max_length': '24', 'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '24', 'null': 'True', 'blank': 'True'})
        },
        'preferences.gallerypreferences': {
            'Meta': {'object_name': 'GalleryPreferences', '_ormbases': ['preferences.Preferences']},
            'preferences_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preferences.Preferences']", 'unique': 'True', 'primary_key': 'True'}),
            'video_play_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        'preferences.generalpreferences': {
            'Meta': {'object_name': 'GeneralPreferences', '_ormbases': ['preferences.Preferences']},
            'about_us': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'analytics_tags': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'exempted_ips': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'exempted_urls': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'exempted_user_agents': ('django.db.models.fields.TextField', [], {'default': "'Googlebot\\nTwitterbot\\nfacebookexternalhit\\n'", 'blank': 'True'}),
            'preferences_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preferences.Preferences']", 'unique': 'True', 'primary_key': 'True'}),
            'privacy_policy': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'private_site': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_age_gateway': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'terms_and_conditions': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'})
        },
        'preferences.loginpreferences': {
            'Meta': {'object_name': 'LoginPreferences', '_ormbases': ['preferences.Preferences']},
            'preferences_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preferences.Preferences']", 'unique': 'True', 'primary_key': 'True'}),
            'raw_login_fields': ('django.db.models.fields.CharField', [], {'default': "'username'", 'max_length': '32'})
        },
        'preferences.naughtywordpreferences': {
            'Meta': {'object_name': 'NaughtyWordPreferences', '_ormbases': ['preferences.Preferences']},
            'email_recipients': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'entries': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'preferences_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preferences.Preferences']", 'unique': 'True', 'primary_key': 'True'}),
            'threshold': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5'})
        },
        'preferences.passwordresetpreferences': {
            'Meta': {'object_name': 'PasswordResetPreferences', '_ormbases': ['preferences.Preferences']},
            'lookup_field': ('django.db.models.fields.CharField', [], {'default': "'email'", 'max_length': '32'}),
            'preferences_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preferences.Preferences']", 'unique': 'True', 'primary_key': 'True'})
        },
        'preferences.preferences': {
            'Meta': {'object_name': 'Preferences'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sites.Site']", 'null': 'True', 'blank': 'True'})
        },
        'preferences.registrationpreferences': {
            'Meta': {'object_name': 'RegistrationPreferences', '_ormbases': ['preferences.Preferences']},
            'preferences_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preferences.Preferences']", 'unique': 'True', 'primary_key': 'True'}),
            'raw_display_fields': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            'raw_field_order': ('django.db.models.fields.CharField', [], {'default': "'{}'", 'max_length': '512', 'blank': 'True'}),
            'raw_required_fields': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'raw_unique_fields': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'})
        },
        'preferences.smirnoffpreferences': {
            'Meta': {'object_name': 'SmirnoffPreferences', '_ormbases': ['preferences.Preferences']},
            'drink_disclaimer': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'preferences_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['preferences.Preferences']", 'unique': 'True', 'primary_key': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['preferences']