from __future__ import absolute_import
from __future__ import unicode_literals

import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.management.base import BaseCommand
from typing import Mapping, Tuple, Type, Dict

from dm.models import *
from dm.defaultable.models import MultiDefaultable

registry = {
    (ModelX, 1): (dict(name='Name1', value=100), dict(f='test1.txt', i='dsp.bmp')),
    (ModelX, 2): (dict(name='Name2', value=200), dict(f='test2.txt', i='dsp.bmp')),
}  # type: Mapping[Tuple[Type[MultiDefaultable], int], Tuple[Dict, Dict]]


class Command(BaseCommand):
    def handle(self, *args, **options):

        if not User.objects.filter(username='admin').exists():
            print 'Creating superuser "admin": OK'
            user = User.objects.create_user('admin', password='adminadmin')
            user.is_superuser = True
            user.is_staff = True
            user.save()

        if not MyModel.objects.all().exists():
            o = MyModel.objects.create()
            print 'Creating initial Model instance: OK {}'.format(vars(o))

        for (model, label), (d, files) in registry.iteritems():
            try:
                o = model.objects.get(label=label, init=True)
                # do not update init=False, to ensure model init after model change
                for k, v in d.iteritems():
                    setattr(o, k, v)
                for field_name in files:
                    file_name = files[field_name]
                    with open(os.path.join(settings.CONTENT_ROOT, file_name), 'r') as f:
                        getattr(o, field_name).delete()
                        getattr(o, field_name).save(file_name, File(f))
                o.save()

            except model.DoesNotExist:
                pass
