# coding=utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

from abc import abstractmethod

from django.core.files.storage import get_storage_class
from django.db import models
from .shared import *
from django.conf import settings



# ===========================================

class OverwriteStorage(get_storage_class()):

    def _save(self, name, content):
        self.delete(name)
        return super(OverwriteStorage, self)._save(name, content)

    def get_available_name(self, name, max_length=None):
        return name


# ===========================================

def upload_to(self, fn):
    return self.upload_to(fn)


class WithFileFields(models.Model):
    class Meta:
        abstract = True

    # Set to True if need to transfer files in new directory
    # Set to False after transver to avoid productivity loss
    relocate_files = False

    @abstractmethod
    def upload_to(self, fn):
        pass

    def prepare_path(self, fn):
        fn = self.upload_to(fn)
        path = os.path.join(settings.MEDIA_ROOT, fn)
        ensure_dir(path)
        return fn, path

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        if self.id is None:
            saved = []
            for f in self.__class__._meta.get_fields():
                if isinstance(f, models.FileField):
                    saved.append((f.name, getattr(self, f.name)))
                    setattr(self, f.name, None)

            super(WithFileFields, self).save(force_insert, force_update, using, update_fields)

            for name, val in saved:
                setattr(self, name, val)

        super(WithFileFields, self).save(False, force_update, using, update_fields)

        if self.relocate_files:  # чтобы переносить файлы при записи надо добавить это поле

            for f in [f for f in self.__class__._meta.get_fields() if isinstance(f, models.FileField)]:

                upload_to = f.upload_to

                f = getattr(self, f.name)  # f is FileField now

                if f and callable(upload_to):
                    _, fn = os.path.split(f.name)
                    old_name = os.path.normpath(f.name)
                    new_name = os.path.normpath(upload_to(self, fn))

                    if old_name != new_name:

                        old_path = os.path.join(settings.MEDIA_ROOT, old_name)
                        new_path = os.path.join(settings.MEDIA_ROOT, new_name)

                        new_dir, _ = os.path.split(new_path)
                        if not os.path.exists(new_dir):
                            print "Making  dir {}", new_dir
                            os.makedirs(new_dir)

                        print "Moving {} to {}".format(old_path, new_path)
                        try:
                            os.rename(old_path, new_path)
                            f.name = new_name

                        except WindowsError as e:
                            print "Can not move file, WindowsError: {}".format(e)
            super(WithFileFields, self).save(False, force_update, using, update_fields)


