# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
try:
    from django.contrib.auth import get_user_model
except ImportError: # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()

user_table_name = "%s.%s" % (User._meta.app_label, User._meta.object_name)

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NotificationSendTask'
        db.create_table(u'django_dingdong_notificationsendtask', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=64, primary_key=True)),
            ('notification_class', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('notification_data', self.gf('picklefield.fields.PickledObjectField')(null=True, blank=True)),
            ('recipients_id_list', self.gf('picklefield.fields.PickledObjectField')()),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True, blank=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('finish_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'django_dingdong', ['NotificationSendTask'])

        # Adding model 'Notification'
        db.create_table(u'django_dingdong_notification', (
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_django_dingdong.notification_set', null=True, to=orm['contenttypes.ContentType'])),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=22, primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notifications', to=orm['django_dingdong.NotificationSendTask'])),
            ('level', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('notification_type', self.gf('django.db.models.fields.CharField')(default='default', max_length=255, db_index=True)),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notifications', to=orm[user_table_name])),
            ('display_title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True, blank=True)),
            ('read_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('extra_data', self.gf('picklefield.fields.PickledObjectField')(null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.SmallIntegerField')(default=0, null=True, db_index=True, blank=True)),
        ))
        db.send_create_signal(u'django_dingdong', ['Notification'])

        # Adding model 'SimpleNotification'
        db.create_table(u'django_dingdong_simplenotification', (
            (u'notification_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['django_dingdong.Notification'], unique=True, primary_key=True)),
            ('display_content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'django_dingdong', ['SimpleNotification'])

        # Adding model 'ActivityNotification'
        db.create_table(u'django_dingdong_activitynotification', (
            (u'notification_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['django_dingdong.Notification'], unique=True, primary_key=True)),
            ('actor_content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notify_actors', to=orm['contenttypes.ContentType'])),
            ('actor_object_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('verb', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('target_content_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='notify_targets', null=True, to=orm['contenttypes.ContentType'])),
            ('target_object_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('action_object_content_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='notify_action_objects', null=True, to=orm['contenttypes.ContentType'])),
            ('action_object_object_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'django_dingdong', ['ActivityNotification'])

        # Adding model 'NotificationUserSetting'
        db.create_table(u'django_dingdong_notificationusersetting', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=22, primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notification_settings', to=orm[user_table_name])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, db_index=True)),
            ('value', self.gf('picklefield.fields.PickledObjectField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'django_dingdong', ['NotificationUserSetting'])

        # Adding unique constraint on 'NotificationUserSetting', fields ['user', 'name']
        db.create_unique(u'django_dingdong_notificationusersetting', ['user_id', 'name'])


    def backwards(self, orm):
        # Removing unique constraint on 'NotificationUserSetting', fields ['user', 'name']
        db.delete_unique(u'django_dingdong_notificationusersetting', ['user_id', 'name'])

        # Deleting model 'NotificationSendTask'
        db.delete_table(u'django_dingdong_notificationsendtask')

        # Deleting model 'Notification'
        db.delete_table(u'django_dingdong_notification')

        # Deleting model 'SimpleNotification'
        db.delete_table(u'django_dingdong_simplenotification')

        # Deleting model 'ActivityNotification'
        db.delete_table(u'django_dingdong_activitynotification')

        # Deleting model 'NotificationUserSetting'
        db.delete_table(u'django_dingdong_notificationusersetting')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'django_dingdong.activitynotification': {
            'Meta': {'object_name': 'ActivityNotification', '_ormbases': [u'django_dingdong.Notification']},
            'action_object_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'notify_action_objects'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'action_object_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'actor_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notify_actors'", 'to': u"orm['contenttypes.ContentType']"}),
            'actor_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'notification_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['django_dingdong.Notification']", 'unique': 'True', 'primary_key': 'True'}),
            'target_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'notify_targets'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'target_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'django_dingdong.notification': {
            'Meta': {'object_name': 'Notification'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'extra_data': ('picklefield.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '22', 'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'notification_type': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '255', 'db_index': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_django_dingdong.notification_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'priority': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'read_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications'", 'to': u"orm['ech_users.User']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications'", 'to': u"orm['django_dingdong.NotificationSendTask']"})
        },
        u'django_dingdong.notificationsendtask': {
            'Meta': {'object_name': 'NotificationSendTask'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'finish_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'notification_class': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'notification_data': ('picklefield.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'}),
            'recipients_id_list': ('picklefield.fields.PickledObjectField', [], {}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'django_dingdong.notificationusersetting': {
            'Meta': {'unique_together': "(('user', 'name'),)", 'object_name': 'NotificationUserSetting'},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '22', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notification_settings'", 'to': u"orm['ech_users.User']"}),
            'value': ('picklefield.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'})
        },
        u'django_dingdong.simplenotification': {
            'Meta': {'object_name': 'SimpleNotification', '_ormbases': [u'django_dingdong.Notification']},
            'display_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'notification_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['django_dingdong.Notification']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'ech_products.product': {
            'Meta': {'object_name': 'Product'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'products'", 'symmetrical': 'False', 'through': u"orm['ech_products.ProductCategoryMember']", 'to': u"orm['ech_products.ProductCategory']"}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'display_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'favorite_by_users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ech_users.User']", 'through': u"orm['ech_products.UserFavoriteProduct']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '22', 'primary_key': 'True'}),
            'is_promo': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'modify_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'orig_price': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'related_products': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ech_products.Product']", 'through': u"orm['ech_products.ProductRelationship']", 'symmetrical': 'False'}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        u'ech_products.productcategory': {
            'Meta': {'object_name': 'ProductCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': (u'django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_rectangle': (u'django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'is_promo': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['ech_products.ProductCategory']"}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'root_node': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ech_products.ProductCategory']", 'null': 'True', 'blank': 'True'}),
            'system_type': ('django.db.models.fields.IntegerField', [], {'default': '-2', 'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'})
        },
        u'ech_products.productcategorymember': {
            'Meta': {'ordering': "['category', 'weight', 'product__name']", 'unique_together': "(('category', 'product'),)", 'object_name': 'ProductCategoryMember'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ech_products.ProductCategory']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '22', 'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ech_products.Product']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'})
        },
        u'ech_products.productrelationship': {
            'Meta': {'ordering': "['product', 'weight', 'related_to']", 'unique_together': "(('product', 'related_to'),)", 'object_name': 'ProductRelationship'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '22', 'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ech_products.Product']"}),
            'related_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['ech_products.Product']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'})
        },
        u'ech_products.userfavoriteproduct': {
            'Meta': {'unique_together': "(('user', 'product'),)", 'object_name': 'UserFavoriteProduct'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '22', 'primary_key': 'True'}),
            'modify_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ech_products.Product']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ech_users.User']"})
        },
        u'ech_users.user': {
            'Meta': {'object_name': 'User'},
            'about_me': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'access_token': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'blog_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '30', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'facebook_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'facebook_open_graph': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_profile_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'favorite_products': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ech_products.Product']", 'through': u"orm['ech_products.UserFavoriteProduct']", 'symmetrical': 'False'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_customer': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'new_token_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'raw_data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'real_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'website_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['django_dingdong']