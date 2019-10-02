# coding=utf-8
from __future__ import absolute_import
from functools import partial

from django.db import models, IntegrityError
from django.db.models import Q
from django.db.models.signals import pre_delete

class Defaultable(models.Model):
    class Meta:
        abstract = True

    is_default = models.BooleanField(default=False)

    @classmethod
    def default(cls):
        from .stuff import get_or_create_default
        return partial(get_or_create_default, cls.__name__, cls._meta.app_label)

    @classmethod
    def ForeignKey(cls, **kwargs):
        return models.ForeignKey(cls, default=cls.default(), on_delete=models.SET_DEFAULT, **kwargs)

    # take care of data integrity
    def __init__(self, *args, **kwargs):
        super(Defaultable, self).__init__(*args, **kwargs)

        # noinspection PyShadowingNames,PyUnusedLocal
        def pre_delete_defaultable(instance, **kwargs):
            # type: (Defaultable, ...)-> None
            if instance.is_default:
                raise IntegrityError, "Can not delete default object {}".format(instance.__class__.__name__)

        pre_delete.connect(pre_delete_defaultable, self.__class__, weak=False, dispatch_uid=self._meta.db_table)

    def save(self, *args, **kwargs):
        super(Defaultable, self).save(*args, **kwargs)
        if self.is_default:  # Ensure only one default, so make all others non default
            self.__class__.objects.filter(~Q(id=self.id), is_default=True).update(is_default=False)
        else:  # Ensure at least one default exists
            if not self.__class__.objects.filter(is_default=True).exists():
                self.__class__.objects.filter(id=self.id).update(is_default=True)

    @property
    def mark(self):
        # noinspection PyTypeChecker
        return ['', '*'][self.is_default]


# ===========================================


class MultiDefaultable(models.Model):
    class Meta:
        abstract = True


    # В одной модели может быть больше одного объекта по умолчанию
    # Для идентификации используется метка label, в ссылающемся объекте надо явно указывать
    # на какой default объект должно ссылаться поле.
    # Если default объект с такой меткой не найден - во время миграции будет создан
    # специальный dummy объект с такой же меткой.
    # На этапе инициализации базы необходимо создать настоящие default объекты (с установленной label)
    # со всей инфраструктурой а dummy объекты удалить - тогда ссылки на dummy автоматически заменятся
    # на настоящие. Как вариант - можно преобразовать dummy объекты в настоящие сняв флаг
    # dummy (впрочем, этот флаг никому не мешает вроде).
    # Для экономии поля в базе можно для dummy сделать метку отрицательной, но это лишний гемор.

    label = models.IntegerField(default=0)
    dummy = models.BooleanField(default=False)

    # auto_generated = models.BooleanField(default=False, editable=False)

    @classmethod
    def default(cls, label):
        assert label
        from .stuff import get_or_create_multi_default
        return partial(get_or_create_multi_default, cls.__name__, cls._meta.app_label, label)

    @classmethod
    def ForeignKey(cls, label, **kwargs):
        return models.ForeignKey(cls, default=cls.default(label), on_delete=models.SET_DEFAULT, **kwargs)

    # take care of data integrity
    def __init__(self, *args, **kwargs):
        super(MultiDefaultable, self).__init__(*args, **kwargs)

        # noinspection PyShadowingNames,PyUnusedLocal
        def pre_delete_defaultable(instance, **kwargs):
            # type: (MultiDefaultable, ...)-> None

            if instance.label:
                raise IntegrityError, "Can not delete default object {}".format(instance.__class__.__name__)

        pre_delete.connect(pre_delete_defaultable, self.__class__, weak=False, dispatch_uid=self._meta.db_table)

    def save(self, *args, **kwargs):
        super(MultiDefaultable, self).save(*args, **kwargs)
        if self.label:  # Ensure only one default with given label, so make all others non default
            self.__class__.objects.filter(~Q(id=self.id), label=self.label).update(label=0)

    @property
    def mark(self):
        # noinspection PyTypeChecker
        return '{}>'.format(self.label) if self.label else ''
