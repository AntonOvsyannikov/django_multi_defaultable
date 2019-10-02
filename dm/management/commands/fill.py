from __future__ import absolute_import
from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from typing import Tuple, Type, List

from dm.models import *

from .cleardummy import clear_dummy

# model, id_like (can be used to init foregin keys), fields
registry_type = List[Tuple[Type[models.Model], int, dict]]

registry = [
    (ModelY, 1, dict(name='file1', f='test1.txt')),
    (ModelY, 2, dict(name='file2', f='test2.txt')),
    (ModelX, 0, dict(y=1, label=1)),
    (ModelX, 0, dict(y=2, label=2)),
    (ModelX, 0, dict(y=1, label=3)),
]  # type: registry_type


def fill_from_registry(registry):
    # type: (registry_type) -> None

    ids = {}

    for model, id_like, d in registry:
        dd = {}
        files = {}
        for field_name, value in d.iteritems():
            field = model._meta.get_field(field_name)
            if isinstance(field, models.ForeignKey):
                dd[field_name + '_id'] = ids[value]
            elif isinstance(field, models.FileField):
                dd[field_name] = ''
                files[field_name] = value
            else:
                dd[field_name] = value

        o = model.objects.create(**dd)
        o.save()
        ids[id_like] = o.id

        for field_name in files:
            file_name = files[field_name]
            with open(os.path.join(settings.CONTENT_ROOT, file_name), 'r') as f:
                getattr(o, field_name).delete()
                getattr(o, field_name).save(file_name, File(f))


class Command(BaseCommand):
    def handle(self, *args, **options):
        fill_from_registry(registry)
        clear_dummy()
