# -*- coding: utf-8 -*-
import logging

from django.conf import settings

from apns import APNs, Payload, Frame
from gcm import GCM

from .bases import BulkBackend


logger = logging.getLogger('django_dingdong.backends.mobile')


# -------------------------------------------
# BaseMobileDeviceBackend
# -------------------------------------------

class BaseMobileDeviceBackend(BulkBackend):
    def get_recipient_devices(self, recipient):
        raise NotImplementedError()

    def send_anonymous_notification(self, notification, recipients):
        raise NotImplementedError()

    def flush(self):
        raise NotImplementedError()

    def is_support_notification(self, notification):
        return self.get_recipient_devices(notification.recipient).exists()

    def is_support_anonymous(self):
        return True

