from __future__ import absolute_import
from __future__ import unicode_literals

from django.apps import apps
from django.core.management.base import BaseCommand

from dm.models import *


def clear_dummy():
    for model in apps.get_models():
        if issubclass(model, MultiDefaultable):
            model.objects.filter(dummy=True).delete()

class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_dummy()
