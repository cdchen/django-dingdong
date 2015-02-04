# -*- coding: utf-8 -*-
#
# echbuy-server
# 
# All rights reserved by niceStudio, Inc.
#
import logging

from django.conf import settings

from apns import APNs, Payload, Frame
from gcm import GCM

from .bases import BulkBackend
from django_dingdong.models import (
    Device,
    GCMDevice,
    APNSDevice)


logger = logging.getLogger('django_dingdone.backends.mobile')


# -------------------------------------------
# BaseMobileDeviceBackend
# -------------------------------------------

class BaseMobileDeviceBackend(BulkBackend):
    def get_recipient_devices(self, recipient):
        return Device.objects.filter(user=recipient)

    def is_support_notification(self, notification):
        return self.get_recipient_devices(notification.recipient).exists()

    def is_support_anonymous(self):
        return True

    def send_anonymous_notification(self, notification, recipients):
        super(BaseMobileDeviceBackend, self).send_anonymous_notification(notification, recipients)

    def flush(self):
        raise NotImplementedError()


# -------------------------------------------
# GCMDeviceBackend
# -------------------------------------------

class GCMDeviceBackend(BaseMobileDeviceBackend):
    def initial(self):
        backend_settings = settings.get('DJANGO_DINGDONG_BACKEND_SETTINGS', {})
        gcm_settings = backend_settings.get('GCMDeviceBackend', {})
        self.gcm = GCM(**gcm_settings.get('gcm'))

    def convert_to_data(self, notification):
        pass

    def flush(self):
        for notification in self.notifications:
            data = self.convert_to_data(notification)
            devices = GCMDevice.objects.filter(user=notification.recipient)
            for device in devices:
                self.gcm.json_request(device.notification_token, data)


# -------------------------------------------
# APNSDeviceBackend
# -------------------------------------------

class APNSDeviceBackend(BaseMobileDeviceBackend):
    def initial(self):
        backend_settings = settings.get('DJANGO_DINGDONG_BACKEND_SETTINGS', {})
        apns_settings = backend_settings.get('APNSDeviceBackend', {})
        self.frame_settings = apns_settings.get('frame', {})
        self.apns_settings = apns_settings.get('apns', {})
        self.apns = APNs(**self.apns_settings)

    def convert_to_payload(self, notification):
        kwargs = {
            'alert': notification.get_display_content(),
        }
        kwargs.update(notification.extra_data or {})
        return Payload(**kwargs)

    def flush(self):
        notification_count = len(self.notifications)
        if notification_count == 1:
            notification = self.notifications[0]
            payload = self.convert_to_payload(notification)
            devices = APNSDevice.objects.filter(user=notification.recipient)
            for device in devices:
                self.apns.gateway_server.send_notification(device.notification_token, payload)
        else:
            frame = Frame()
            identifier = 0
            for notification in self.notifications:
                payload = self.convert_to_payload(notification)
                devices = APNSDevice.objects.filter(user=notification.recipient)
                for device in devices:
                    identifier += 1
                    frame.add_item(device.notification_token, payload, identifier=identifier)
            self.apns.gateway_server.send_notification_multiple(frame)
