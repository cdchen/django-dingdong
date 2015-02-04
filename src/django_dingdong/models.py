# -*- coding: utf-8 -*-
#
# __author__ = 'cdchen'
#
import logging
import copy

import six
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import (
    models,
    transaction)
from django.utils.importlib import import_module
from django.utils.timezone import now
from django_extensions.db.fields import (
    ShortUUIDField,
    UUIDField,
    CreationDateTimeField)
from picklefield import PickledObjectField
from django_enumfield import enum
from polymorphic import PolymorphicModel


logger = logging.getLevelName("django_dingdong")
User = get_user_model()

# -------------------------------------------
# NotificationTask
# -------------------------------------------

class NotificationTask(models.Model):
    id = UUIDField(
        primary_key=True,
    )

    notification_class = models.CharField(
        max_length=255,
        db_index=True,
    )

    notification_data = PickledObjectField(
        null=True,
        blank=True,
    )

    recipients_id_list = PickledObjectField(

    )

    include_anonymous = models.BooleanField(
        default=False,
        db_index=True,
    )

    create_time = CreationDateTimeField(
        db_index=True,
    )

    start_time = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    finish_time = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    def get_notification_class(self):
        if self.notification_class:
            module_name, klass_name = self.notification_class.split(':')
            module = import_module(module_name)
            return getattr(module, klass_name)
        return None

    def get_recipients(self):
        if self.recipients_id_list:
            recipients = self.recipients_id_list
            if isinstance(self.recipients_id_list, six.string_types):
                recipients = self.recipients_id_list.split()
            return User.objects.filter(pk__in=recipients)
        return User.objects.none()

    def create_notification(self, recipient):
        notification_class = self.get_notification_class()
        assert notification_class is not None

        data = copy.copy(self.notification_data or {})
        data.update({
            'recipient': recipient,
            'task': self,
        })
        return notification_class(**data)


# ----------------------------------------------
# Notification
# ----------------------------------------------

class NotificationLevel(enum.Enum):
    DEBUG = 0
    INFO = 1
    NOTICE = 2
    WARNING = 3
    ERROR = 4


class NotificationStatus(enum.Enum):
    NEW = 0
    USER_DISABLED = 1
    SENDING = 64
    PENDING = 65
    SENT = 128
    READ = 256


class Notification(PolymorphicModel):
    id = ShortUUIDField(
        primary_key=True,
    )

    task = models.ForeignKey(
        NotificationTask,
        related_name='notifications',
    )

    level = enum.EnumField(
        NotificationLevel,
    )

    notification_type = models.CharField(
        max_length=255,
        db_index=True,
        default='default',
    )

    recipient = models.ForeignKey(
        User,
        related_name='notifications',
        null=True,
        blank=True,
    )

    display_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    status = enum.EnumField(
        NotificationStatus,
        db_index=True,
    )

    create_time = CreationDateTimeField(
        db_index=True,
    )

    read_time = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    public = models.BooleanField(
        default=True,
        db_index=True,
    )

    extra_data = PickledObjectField(
        null=True,
        blank=True,
    )

    priority = models.SmallIntegerField(
        default=0,
        db_index=True,
        blank=True,
        null=True,
    )

    def update_status(self, new_status, save=True):
        if self.status != new_status:
            self.status = new_status
            if save is True:
                self.save()

    def save(self, *args, **kwargs):
        if self.status == NotificationStatus.READ:
            if self.read_time is None:
                self.read_time = now()
        else:
            self.read_time = None
        return super(Notification, self).save(*args, **kwargs)

    def get_display_content(self):
        return self.__unicode__()


class SimpleNotification(Notification):
    display_content = models.TextField(
        null=True,
        blank=True,
    )

    def __unicode__(self):
        return self.display_content


class ActivityNotification(Notification):
    actor_content_type = models.ForeignKey(
        ContentType,
        related_name='notify_actors'
    )

    actor_object_id = models.CharField(
        max_length=255
    )

    actor = generic.GenericForeignKey(
        'actor_content_type',
        'actor_object_id'
    )

    verb = models.CharField(
        max_length=255
    )

    target_content_type = models.ForeignKey(
        ContentType,
        related_name='notify_targets',
        blank=True,
        null=True
    )

    target_object_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    target = generic.GenericForeignKey(
        'target_content_type',
        'target_object_id'
    )

    action_object_content_type = models.ForeignKey(
        ContentType,
        related_name='notify_action_objects',
        blank=True,
        null=True
    )

    action_object_object_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    action_object = generic.GenericForeignKey(
        'action_object_content_type',
        'action_object_object_id'
    )


# ----------------------------------------------
# NotificationUserSetting
# ----------------------------------------------

class NotificationUserSettingManager(models.Manager):
    def get_user_settings(self, user):
        '''
        取得指定的使用者所有的設定值。

        :param user: 使用者。
        :type user: User
        :return: 指定的使用者所有的設定值。
        :rtype: dict
        '''
        results = {}
        for instance in self.get_queryset().filter(user=user):
            results[instance.name] = instance.value
        return results

    def clean_user_settings(self, user):
        with transaction.atomic():
            self.get_queryset().filter(user=user).delete()

    def set_user_settings(self, user, settings):
        with transaction.atomic():
            self.get_queryset().filter(user=user).delete()
            for name, value in settings.items():
                self.create(user=user, name=name, value=value)

    def set_user_value(self, user, name, value):
        kwargs = {
            'user': user,
            'name': name,
        }
        try:
            instance = self.get_queryset().get(**kwargs)
        except:
            instance = self.model(**kwargs)
        instance.value = value
        instance.save()

    def get_user_value(self, user, name):
        instance = self.get_queryset().get(user=user, name=name)
        return instance.value


class NotificationUserSetting(models.Model):
    class Meta:
        unique_together = (
            ('user', 'name',),
        )

    id = ShortUUIDField(
        primary_key=True,
    )

    user = models.ForeignKey(
        User,
        related_name='notification_settings',
    )

    name = models.CharField(
        max_length=256,
        db_index=True,
    )

    value = PickledObjectField(
        null=True,
        blank=True,
    )

    objects = NotificationUserSettingManager()

