# -*- coding: utf-8 -*-
#
# __author__ = 'cdchen'
#
import logging

from django.core.mail import send_mail, send_mass_mail
from django.conf import settings

from .bases import BulkBackend


logger = logging.get('django_dingdong.backends.email')

email_field = getattr(settings, 'DJANGO_DINGDONE_EMAIL_FIELD', 'email')
email_from = getattr(settings, 'DJANGO_DINGDONE_EMAIL_ADDRESS', None)

if not email_from:
    email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', None)


# -------------------------------------------
# EmailBackend
# -------------------------------------------

class EmailBackend(BulkBackend):
    def is_support_notification(self, notification):
        if not email_from:
            return False

        if notification.recipient:
            email = getattr(notification.recipient, email_field, None)
            return email is not None
        return False

    def convert_to_email_tuple(self, notification):
        return (
            notification.display_title,  # subject
            unicode(notification),  # body
            email_from,  # from
            notification.recipient.email,  # to
        )

    def flush(self):
        notification_count = len(self.notifications)

        if notification_count == 1:
            data = self.convert_to_email_tuple(self.notifications[0])
            send_mail(*data)
        else:
            data = []
            for notification in self.notifications:
                data.append(self.convert_to_email_tuple(notification))
            send_mass_mail(data)
