# -*- coding: utf-8 -*-
#
# __author__ = 'cdchen'
#
import logging

from rest_framework import serializers

from django_dingdong.models import (
    Notification,
    ActivityNotification,
    SimpleNotification, NotificationSendTask)


logger = logging.getLevelName("django_dingdong.api")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification


class SimpleNotificationSerializer(NotificationSerializer):
    class Meta(NotificationSerializer.Meta):
        model = SimpleNotification


class ActivityNotificationSerializer(NotificationSerializer):
    class Meta(NotificationSerializer.Meta):
        model = ActivityNotification


class NotificationSendTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSendTask
