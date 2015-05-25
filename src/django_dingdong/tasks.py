# -*- coding: utf-8 -*-
#
# __author__ = 'cdchen'
#

from celery import shared_task, Task
from celery.utils.log import get_task_logger
from django.utils.timezone import now
from django_dingdong.senders import SenderFactory
from .models import (
    NotificationUserSetting,
    NotificationStatus,
    NotificationTask)

logger = get_task_logger('django_dingdong.tasks')

factory = SenderFactory()


class BaseSendTask(Task):
    ignore_result = True

    def get_senders(self):
        return factory.get_all_senders()

    def get_recipients(self, notification_task):
        return notification_task.get_recipients()

    def run(self, notification_task_id):
        notification_task = NotificationTask.objects.get(pk=notification_task_id)
        senders = self.get_senders()

        for sender in senders:
            sender.initial()

        recipients = self.get_recipients(notification_task)
        for recipient in recipients:

            notification = notification_task.create_notification()

            user_settings = NotificationUserSetting.objects.get_user_settings(recipient)
            if user_settings.get('disable_all_notifications', False):
                logger.info("User disable all notifications, skip. user=%s, notification=%s",
                            recipient, notification)
            else:
                notification_type = notification.notification_type

                if user_settings.get('disable_%s_notification' % notification_type, False):
                    notification.set_status(NotificationStatus.USER_DISABLED)
                    continue

                notification.update_status(NotificationStatus.SENDING)
                result = {}

                for sender in senders:
                    backend_id = sender.get_backend_id()
                    if sender.is_support_notification(notification) is False:
                        logger.info("Sender is not support notification, skip. sender=%s, notification=%s",
                                    sender, notification)
                        result[backend_id] = NotificationStatus.NOT_SUPPORT
                        continue

                    if user_settings.get('disable_%s_notification_backend' % backend_id, False):
                        logger.info(
                            "User disable notification with this backend, skip. user=%s, notification=%s, backend=%s",
                            recipient, notification, sender)
                        result[backend_id] = NotificationStatus.USER_DISABLED
                        continue

                    sender.send(notification=notification)
                    result[backend_id] = NotificationStatus.SENT

                notification.result = result

            notification.set_status(NotificationStatus.SENT)

        if notification_task.include_anonymuse:
            notification = notification_task.create_notification(recipient=None)
            for sender in senders:
                if sender.support_anonymous():
                    sender.send_anonymous(notification)
            notification.set_status(NotificationStatus.SENT)

        # Force flush all notifications for every sender.
        for sender in senders:
            sender.finish()

        # Update `finish_time` when done.
        notification_task.finish_time = now()
        notification_task.save()


@shared_task
class DefaultNotificationSendTask(BaseSendTask):
    pass
