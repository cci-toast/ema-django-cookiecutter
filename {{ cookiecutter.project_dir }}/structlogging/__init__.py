# -*- coding: utf-8 -*-

"""Top-level package for structlogging."""

from .configure import celery_configure, django_configure

__all__ = ["django_configure", "celery_configure"]
