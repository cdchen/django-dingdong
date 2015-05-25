# -*- coding: utf-8 -*-
#
# __author__ = 'cdchen'
#
import logging

from actstream.models import Action
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import (
    models,
    transaction)
from django.utils.timezone import now
from django_extensions.db.fields import (
    ShortUUIDField,
    UUIDField,
    CreationDateTimeField)
from jsonfield import JSONField
from picklefield import PickledObjectField
from django_enumfield import enum
from polymorphic import PolymorphicModel, PolymorphicManager


logger = logging.getLevelName("django_dingdong.models")


# -------------------------------------------
# Notification Task
# -------------------------------------------

class NotificationTaskError(Exception):
    pass


class NotificationTaskStatus(enum.Enum):
    NEW = 0
    PENDING = 1
    START = 64
    FINISH = 65


class NotificationTaskManager(models.Manager):
    def create_task(self, notification_class, notification_data, recipients, notification_type=None,
                    include_anonymous=False, eta_time=None):
        if not issubclass(notification_class, Notification):
            raise ValueError("'notification_class' must be sub class of 'Notification'")

        content_type = ContentType.objects.get_for_model(notification_class)

        recipient_list = [recipient.pk for recipient in recipients]
        if not recipient_list:
            raise ValueError("'recipients' can not be empty.")

        notification_data = notification_data or {}
        if notification_type:
            notification_data['notification_type'] = notification_type

        instance = self.model(
            notification_class=content_type,
            notification_data=notification_data,
            recipient_list=recipient_list,
            include_anonymous=include_anonymous,
            eta_time=eta_time)

        instance.save()
        return instance


class NotificationTask(models.Model):
    id = UUIDField(
        primary_key=True,
    )

    notification_class = models.ForeignKey(
        ContentType,
    )

    notification_data = JSONField(
        default={},
        null=True,
        blank=True,
    )

    recipient_list = JSONField(
        default=[],
    )

    include_anonymous = models.BooleanField(
        default=False,
        db_index=True,
    )

    status = enum.EnumField(
        NotificationTaskStatus,
        db_index=True,
    )

    create_time = CreationDateTimeField(
        db_index=True,
    )

    eta_time = models.DateTimeField(
        null=True,
        blank=True,
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

    objects = NotificationTaskManager()

    def create_notification(self, save=True, **kwargs):
        klass = self.notification_class.model_class()
        data = self.notification_data or {}
        data.update(kwargs)
        instance = klass(**data)
        if save:
            instance.save()
        return instance


# -------------------------------------------
# Notification
# -------------------------------------------

class NotificationStatus(enum.Enum):
    NEW = 0
    PREPARE = 1
    NOT_SUPPORT = 2
    USER_DISABLE = 3
    SENDING = 32
    SENT = 64
    UNREAD = 255
    READ = 256


class NotificationManager(PolymorphicManager):
    def for_user(self, user):
        if user.is_anonymous():
            return self.get_queryset().filter(recipient=None)
        return self.get_queryset().filter(recipient=user)


class Notification(PolymorphicModel):
    id = UUIDField(
        primary_key=True,
    )

    task = models.ForeignKey(
        NotificationTask,
    )

    notification_type = models.CharField(
        max_length=255,
        db_index=True,
        default='default',
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_index=True,
        null=True,
        blank=True,
    )

    create_time = CreationDateTimeField(
        db_index=True,
    )

    sent_time = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    read_time = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    result = JSONField(
        null=True,
        blank=True,
    )

    objects = NotificationManager()

    def set_status(self, status, save=True):
        if self.status != status:
            self.status = status
            if save:
                self.save(update_fields=['status'])

    def mark_unread(self):
        if self.status == NotificationStatus.READ:
            self.read_time = None
            self.set_status(NotificationStatus.UNREAD)

    def mark_read(self):
        if self.recipient and self.status != NotificationStatus.READ:
            self.read_time = now()
            self.set_status(NotificationStatus.READ)

    def get_display_content(self):
        return self.__unicode__()

    def render_display_content(self, **context):
        context.update({
            'recipient': self.recipient
        })
        display_content = self.get_display_content()
        if display_content:
            return display_content.format(**context)
        return display_content


class SimpleNotification(Notification):
    display_content = models.TextField(
        null=True,
        blank=True,
    )

    def get_display_content(self):
        return self.display_content or ''


class ActionNotification(Notification):
    action = models.ForeignKey(
        Action,
    )

    def get_display_content(self):
        return self.action.__unicode__() if self.action else ''


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
        settings.AUTH_USER_MODEL,
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
