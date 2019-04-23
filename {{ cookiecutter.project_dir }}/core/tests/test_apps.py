from django.apps import apps
from django.test import TestCase

from core.apps import CoreConfig


class CoreConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual('core', CoreConfig.name)
        self.assertEqual('core', apps.get_app_config('core').name)
