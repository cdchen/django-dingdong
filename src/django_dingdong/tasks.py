# -*- coding: utf-8 -*-
#
# __author__ = 'cdchen'
#
from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils.timezone import now
from django_dingdong.backends import backend_manager

from .models import (
    NotificationUserSetting,
    NotificationStatus, NotificationSendTask)


logger = get_task_logger('django_dingdong.tasks')


@shared_task(bind=True, ignore_result=True)
def task_start_notification_send_task(notification_task_id):
    notification_task = NotificationSendTask.objects.get(pk=notification_task_id)

    backend_manager.prepare()
    backends = backend_manager.all_backends
    notification_class = notification_task.get_notification_class()

    recipients = notification_task.get_recipients()
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

            status = backend.send_notification(
                notification=notification)
            notification.status = status

    backend_manager.done()

    # Update `finish_time` when done.
    notification_task.finish_time = now()
    notification_task.save()
