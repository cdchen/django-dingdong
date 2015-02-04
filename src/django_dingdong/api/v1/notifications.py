# -*- coding: utf-8 -*-
#
# __author__ = 'cdchen'
#
import logging

from rest_framework.generics import (
    ListAPIView, RetrieveUpdateAPIView)

from django_dingdong.api.v1.serializers import (
    NotificationSerializer,
    ActivityNotificationSerializer,
    SimpleNotificationSerializer,
    NotificationTaskSerializer)
from django_dingdong.models import (
    ActivityNotification,
    SimpleNotification)
from django_dingdong.views import BaseNotificationViewMixin


logger = logging.getLevelName("django_dingdong.api")


# -------------------------------------------
# Notification API views.
# -------------------------------------------

class NotificationAPIViewMixin(BaseNotificationViewMixin):
    serializer_class = NotificationSerializer

    def initial(self, request, *args, **kwargs):
        self.user = self.get_user()
        super(NotificationAPIViewMixin, self).initial(request, *args, **kwargs)

    def get_serializer(self, instance=None, *args, **kwargs):
        serializer_class = {
            SimpleNotification: SimpleNotificationSerializer,
            ActivityNotification: ActivityNotificationSerializer,
        }.get(instance.__class__, NotificationSerializer)
        context = self.get_serializer_context()
        return serializer_class(
            instance=instance, context=context, *args, **kwargs)


class NotificationListAPIView(NotificationAPIViewMixin,
                              ListAPIView):
    pass


class NotificationRetrieveAPIView(NotificationAPIViewMixin,
                                  RetrieveUpdateAPIView):
    pass


# -------------------------------------------
# NotificationTaskSerializer API Views
# -------------------------------------------

class NotificationTaskAPIViewMixin(object):
    serializer_class = NotificationTaskSerializer


class NotificationTaskListAPIView(NotificationTaskAPIViewMixin,
                                  ListAPIView):
    pass


class NotificationTaskRetrieveAPIView(NotificationTaskAPIViewMixin,
                                      RetrieveUpdateAPIView):
    pass
