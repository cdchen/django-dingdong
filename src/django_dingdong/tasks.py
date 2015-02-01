# -*- coding: utf-8 -*-
#
# __author__ = 'cdchen'
#
from celery import shared_task, Task
from celery.utils.log import get_task_logger
from django.utils.timezone import now
from django_dingdong.backends import backend_manager

from .models import (
    NotificationUserSetting,
    NotificationStatus, NotificationSendTask)


logger = get_task_logger('django_dingdong.tasks')


class BaseSendTask(Task):
    ignore_result = True

    def get_backends(self):
        return backend_manager.all_backends

    def get_recipients(self, notification_task):
        return notification_task.get_recipients()

    def run(self, notification_task_id):
        notification_task = NotificationSendTask.objects.get(pk=notification_task_id)
        backend_manager.prepare()
        backends = self.get_backends()
        notification_class = notification_task.get_notification_class()

        recipients = self.get_recipients(notification_task)
        for recipient in recipients:
            notify_settings = NotificationUserSetting.objects.get_user_settings(recipient)
            if notify_settings.get('disable_all_notifications', False) is True:
                continue

            data = notification_task.notification_data or {}
            notification = notification_class(**data)
            notification.save()

            notification_type = notification.notification_type
            if notify_settings.get('disable_%s_notification' % notification_type, False) is True:
                notification.update_status(NotificationStatus.USER_DISABLED)
                continue

            notification.update_status(NotificationStatus.SENDING)
            for backend in backends:
                backend_id = backend.get_backend_id()
                if notify_settings.get('disable_%s_notification_backend' % backend_id, False) is True:
                    notification.update_status(NotificationStatus.USER_DISABLED)
                    continue

                if backend.is_support_notification(notification) is False:
                    continue

                status = backend.send_notification(notification=notification)
                notification.update_status(status)

            notification.update_status(NotificationStatus.SENT)

        # Force send all notifications for every backend.
        for backend in backends:
            backend.flush()

        backend_manager.done()

        # Update `finish_time` when done.
        notification_task.finish_time = now()
        notification_task.save()


@shared_task
class DefaultNotificationSendTask(BaseSendTask):
    pass

