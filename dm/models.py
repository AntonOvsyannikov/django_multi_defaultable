# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from dm.defaultable.models import MultiDefaultable
from models_shared import WithFileFields, upload_to, OverwriteStorage


class ModelX(MultiDefaultable, WithFileFields):
    name = models.CharField(default='', max_length=255, blank=True)
    value = models.IntegerField(default=0)

    # f = models.FileField(upload_to=upload_to, default='', blank=True, storage=OverwriteStorage())
    # i = models.ImageField(upload_to=upload_to, default='', blank=True, storage=OverwriteStorage())
    f = models.FileField(upload_to=upload_to, default='', blank=True)
    i = models.ImageField(upload_to=upload_to, default='', blank=True)

    def __unicode__(self):
        return "[{}X{} {} {}]".format(self.mark, self.id, self.name, self.value)

    def upload_to(self, fn):
        return "modelx/{}/{}".format(self.id, fn)


# -------------------------------------------
#
class MyModel(models.Model):
    x1 = ModelX.ForeignKey(1, related_name='x1')
    x2 = ModelX.ForeignKey(2, related_name='x2')

    # y = ModelY.ForeignKey()

    def __unicode__(self):
        return "M{}:x1={} x2={}".format(self.id, self.x1, self.x2)
#
