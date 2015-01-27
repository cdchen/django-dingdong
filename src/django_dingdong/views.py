# -*- coding: utf-8 -*-
#
# __author__ = 'cdchen'
#
import logging

from django.core.exceptions import PermissionDenied
from django.views.generic import (
    ListView, DetailView)

from .models import User


logger = logging.getLevelName('django_dingdong.views')


class BaseNotificationViewMixin(object):
    def get_queryset(self):
        qs = super(BaseNotificationViewMixin, self).get_queryset()
        return qs.filter(recipient=self.user)

    def get_user(self):
        kwargs = {
            User.USERNAME_FIELD: self.kwargs.get('username'),
        }
        return User.objects.get(**kwargs)


class NotificationViewMixin(BaseNotificationViewMixin):
    def permission_denied(self, request):
        raise PermissionDenied()

    def check_permissions(self, request):
        user = request.user
        if user.is_authenticated is True:
            if user.is_superuser is True or user.pk == self.user.pk:
                return
        self.permission_denied(request)

    def check_object_permissions(self, request, obj):
        user = request.user
        if user.is_authenticated is True:
            if user.is_superuser is True or user == obj.recipient:
                return
        self.permission_denied(request)

    def initial(self, request, *args, **kwargs):
        self.user = self.get_user()
        self.check_permissions(request)

    def dispatch(self, request, *args, **kwargs):
        self.initial(request, *args, **kwargs)
        return super(NotificationViewMixin, self).dispatch(request, *args, **kwargs)


class NotificationListView(NotificationViewMixin,
                           ListView):
    template_name = 'django_dingdong/notification/list.html'


class NotificationDetailView(NotificationViewMixin,
                             DetailView):
    template_name = 'django_djngdone/notification/detail.html'
