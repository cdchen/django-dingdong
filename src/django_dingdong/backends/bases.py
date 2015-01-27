# -*- coding: utf-8 -*-
#
# __author__ = 'cdchen'
#
import logging
import six

from django.utils.importlib import import_module


logger = logging.getLevelName("django_dingdong")

class BackendMeta(type):
    def __init__(cls, what, bases=None, dict=None):
        backend_id = dict.get('backend_id', None)
        if not backend_id:
            dict['backend_id'] = what
        return super(BackendMeta, cls).__init__(what, bases, dict)


class Backend(six.with_metaclass(BackendMeta, object)):
    backend_id = None
    display_title = None

    def __init__(self, backend_manager):
        self._backend_manager = backend_manager

    def send_notification(self, notification):
        raise NotImplementedError()

    def get_backend_id(self):
        return self.backend_id

    def is_support_notification(self, notification):
        return True

    def prepare(self):
        pass

    def done(self):
        pass


class SimpleBackend(Backend):
    pass


class BulkBackend(Backend):
    notifications = []

    def send_notification(self, notification):
        self.notifications.append(notification)
        return 'Queued, waiting for send.'

    def send_all(self):
        raise NotImplementedError()

    def done(self):
        self.send_all()


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

    def get_all_backends(self):
        return self._backends

    def initial(self):
        for backend in self.get_all_backends():
            backend.prepare()

    def finish(self):
        for backend in self.get_all_backends():
            backend.done()

