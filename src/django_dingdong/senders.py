# -*- coding: utf-8 -*-
#
# echbuy-server
# 
# All rights reserved by niceStudio, Inc.
#
import logging

import six

from apns import Payload, APNs
from django.conf import settings
from django.utils.importlib import import_module
from django_dingdong.models import NotificationStatus
from gcm import GCM
from django.core.mail import send_mail

logger = logging.getLogger('django_dingdong.senders')

EMAIL_SENDER = getattr(settings, 'DINGDONG_SENDER_EMAIL_SENDER', '')
EMAIL_FIELD = getattr(settings, 'DINGDONG_SENDER_EMAIL_FIELD', 'email')

GCM_API_KEY = getattr(settings, 'DINGDONG_SENDER_GCM_API_KEY', '')
APNS_USE_SANDBOX = getattr(settings, 'DINGDONG_SENDER_APNS_USE_SANDBOX', False)
APNS_CERT_FILE = getattr(settings, 'DINGDONG_SENDER_APNS_CERT_FILE', '')
APNS_KEY_FILE = getattr(settings, 'DINGDONG_SENDER_APNS_KEY_FILE', '')


class NotificationSenderMetaclass(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super(NotificationSenderMetaclass, cls).__new__(cls, name, bases, attrs)
        sender_id = getattr(new_cls, 'sender_id', None)
        if not sender_id:
            sender_id = name.lower()
        new_cls.sender_id = sender_id
        return new_cls


class NotificationSender(six.with_metaclass(NotificationSenderMetaclass)):
    def send(self, notification):
        raise NotImplementedError()

    def initial(self):
        pass

    def finish(self):
        pass

    def is_support(self, notification):
        return True

    def support_anonymous(self):
        return True


class DummyNotificationSender(NotificationSender):
    def send(self, notification):
        logger.debug("Notification sent. notification=%s, recipient=%s",
                     notification, notification.recipient)


class EmailNotificationSender(NotificationSender):
    def is_support(self, notification):
        recipient = notification.recipient
        return all([EMAIL_SENDER, recipient, getattr(recipient, EMAIL_FIELD, None)])

    def support_anonymous(self):
        return False

    def convert_to_email_tuple(self, notification):
        return (
            notification.display_title,  # subject
            unicode(notification),  # body
            EMAIL_SENDER,  # from
            getattr(notification.recipient, EMAIL_FIELD)  # to
        )

    def send(self, notification):
        data = self.convert_to_email_tuple(notification)
        send_mail(*data)
        return NotificationStatus.SENT


class MobileDeviceNotificationSender(NotificationSender):
    def get_devices_of_recipient(self, recipient):
        raise NotImplementedError()

    def get_notification_token(self, device):
        raise NotImplementedError()

    def is_support(self, notification):
        return True


class BaseAndroidDeviceNotificationSender(MobileDeviceNotificationSender):
    sender_id = 'android_device'

    def initial(self):
        self._gcm = GCM(GCM_API_KEY)

    @property
    def gcm(self):
        if not hasattr(self, '_gcm'):
            self.initial()
        return self._gcm

    def render_notification_data(self, notification):
        return notification.render_display_content()

    def send(self, notification):
        for device in self.get_devices_of_recipient(notification.recipient):
            self.gcm.plaintext_request(
                registration_id=self.get_notification_token(device),
                data=self.render_notification_data(notification),
            )
        return NotificationStatus.SENT

    def finish(self):
        del self._gcm


class BaseIOSDeviceNotificationSender(MobileDeviceNotificationSender):
    sender_id = 'ios_device'

    def initial(self):
        self._apns = APNs(
            use_sandbox=APNS_USE_SANDBOX,
            cert_file=APNS_CERT_FILE,
            key_file=APNS_KEY_FILE,
        )

    @property
    def apns(self):
        if not hasattr(self, '_apns'):
            self.initial()
        return self._apns

    def create_payload(self, notification):
        return Payload(alert=notification.render_display_context())

    def send(self, notification):
        for device in self.get_devices_of_recipient(notification.recipient):
            payload = self.create_payload(notification)
            self.apns.gateway_server.send_notification(
                self.get_notification_token(device), payload)
        return NotificationStatus.SENT

    def finish(self):
        del self._apns


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SenderFactory(six.with_metaclass(Singleton)):
    def __init__(self):
        sender_classes = getattr(settings, 'DINGDONG_SENDER_CLASSES', [])
        senders = []
        for klass in sender_classes:
            module_name, klass = klass.split(":")
            module_name = import_module(module_name)
            klass = getattr(module_name, klass)
            senders.append(klass)
        self.sender_classes = senders

    def get_all_senders(self):
        return [klass() for klass in self.sender_classes]
