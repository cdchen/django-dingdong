# -*- coding: utf-8 -*-
#
# __author__ = 'cdchen'
#
import logging
import six
import copy

from django.utils.importlib import import_module
from django.utils.translation import ugettext as _
from django_dingdong.models import NotificationStatus


logger = logging.getLevelName("django_dingdong")


class BackendMeta(type):
    def __new__(S, name, bases, attrs):
        backend_id = attrs.pop('backend_id', None)
        if not backend_id:
            backend_id = name
        display_name = attrs.pop('display_name', None)
        if not display_name:
            display_name = name
        attrs.update({
            'backend_id': backend_id.lower(),
            'display_name': display_name,
        })
        return type.__new__(S, name, bases, attrs)


class Backend(six.with_metaclass(BackendMeta)):

    def __init__(self, backend_manager):
        self._backend_manager = backend_manager

    def send_notification(self, notification):
        raise NotImplementedError()

    def get_backend_id(self):
        if not self.backend_id:
            raise NotImplementedError(
                _("You must set the 'backend_id' attribute or override this method."))
        return self.backend_id

    def is_support_notification(self, notification):
        return True

    def initial(self):
        pass

    def finish(self):
        pass

    def flush(self):
        pass


class SimpleBackend(Backend):
    pass


class BulkBackend(Backend):
    notifications = []

    def send_notification(self, notification):
        self.notifications.append(notification)
        return NotificationStatus.PENDING

    def flush(self):
        raise NotImplementedError()


class DummyBackend(BulkBackend):
    def flush(self):
        for notification in self.notifications:
            logger.info("notification=%s", notification)


class BackendManager(object):
    def __init__(self):
        from django.conf import settings

        backends = []
        def add_backend(name):
            module_name, klass_name = name.split(':')
            module = import_module(module_name)
            klass = getattr(module, klass_name)
            if klass not in backends:
                backends.append(klass)

        for name in getattr(settings, 'DJANGO_DINGDONG_BACKENDS', []):
            add_backend(name)

        name = getattr(settings, 'DJANGO_DINGDONG_DEFAULT_BACKEND', None)
        if name:
            add_backend(name)

        self._backend_classes = backends
        self._backends = [cls(self) for cls in backends]

    @property
    def all_backends(self):
        return copy.copy(self._backends)

    @property
    def all_backend_id(self):
        return [b.backend_id for b in self._backends]

    @property
    def all_backend_choices(self):
        return ((b.backend_id, b.display_name) for b in self._backends)

    def prepare(self):
        for backend in self._backends:
            backend.initial()

    def done(self):
        for backend in self._backends:
            backend.finish()

