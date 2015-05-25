# -*- coding: utf-8 -*-
#
# __author__ = 'cdchen'
#
import logging

from rest_framework import serializers

from django_dingdong.models import (
    Notification,
    SimpleNotification,
    NotificationTask,
    ActionNotification)


logger = logging.getLevelName("django_dingdong.api")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification


class SimpleNotificationSerializer(NotificationSerializer):
    class Meta(NotificationSerializer.Meta):
        model = SimpleNotification


class ActionNotificationSerializer(NotificationSerializer):
    class Meta(NotificationSerializer.Meta):
        model = ActionNotification


class NotificationTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTask
