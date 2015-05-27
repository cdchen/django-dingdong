# -*- coding: utf-8 -*-
#
# echbuy-server
# 
# All rights reserved by niceStudio, Inc.
#


def import_object(s, sep=':', default=None):
    from django.utils.importlib import import_module

    module_name, obj_name = s.strip(sep)
    module = import_module(module_name)
    return getattr(module, obj_name, default)
