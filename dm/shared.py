from __future__ import unicode_literals

import errno
import os
import time

from django.conf import settings

# -------------------------------------------

def image_save_to_model(image, model, field_name, file_name_wo_ext, img_type ='jpg', random_tag = True):
    if not model.id: model.save()

    file_name = '{}{}.{}'.format(file_name_wo_ext, '_'+now() if random_tag else '', img_type)

    fld = model.__class__._meta.get_field(field_name)

    name = fld.upload_to(model, file_name) if callable(fld.upload_to) else os.path.join(fld.upload_to, file_name)
    path = os.path.join(settings.MEDIA_ROOT, name)

    ensure_dir(path)

    image.convert('RGB').save(path)
    getattr(model,field_name).name = name
    #model.save()

def save_to_filefield(s, model, field_name, file_name):

    fld = model.__class__._meta.get_field(field_name)
    name = fld.upload_to(model, file_name) if callable(fld.upload_to) else os.path.join(fld.upload_to, file_name)
    path = os.path.join(settings.MEDIA_ROOT, name)
    ensure_dir(path)

    with open(path, "wb") as f:
        f.write(s)

    getattr(model,field_name).name = name
    model.save()




# def image_save_to_model(image, model, field_name, file_name_wo_ext, img_type ='png', random_tag = True):
#     fn = '{}{}.{}'.format(file_name_wo_ext, '_'+now() if random_tag else '', img_type)
#
#     f = StringIO()
#     image.save(f, img_type)
#     f.seek(0)
#     model.__dict__[field_name] = InMemoryUploadedFile(
#         f, None, fn, 'image/{}'.format(img_type), f.len, None
#     )
#     model.save()
#     f.close()
# -------------------------------------------

# def save_to_filefield(s, model, field_name, file_name):
#     f = StringIO(s)
#     model.__dict__[field_name] = InMemoryUploadedFile(
#         f, None, file_name, 'application/octet-stream', f.len, None
#     )
#     model.save()
#     f.close()


# -------------------------------------------

def now():
    return "{}".format(int(time.time()*1000))

# -------------------------------------------

def exists(fn):
    return os.path.isfile(fn)

def filename(path, withext = True):
    fn = os.path.split(path)[1]
    f, e = os.path.splitext(fn)
    return fn if withext else f

def ensure_dir(filename):

    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


# -------------------------------------------

def reversedict(d): return {v: k for k, v in d.items()}

# -------------------------------------------

def get_or_getattr(o, attrname):
    try:
        return o[attrname]
    except (TypeError, KeyError, AttributeError):
        return getattr(o, attrname)

# -------------------------------------------
def uprint(*args):
    for a in args:
        print repr(a).decode("unicode_escape"),
    print


# -------------------------------------------

def stdrepr(c):
    def __repr__(self):
        fields = self._fields if hasattr(self, "_fields") else self.__dict__.keys()
        vals = [getattr(self, f) for f in fields]
        return repr("{}({})".format(
            self.__class__.__name__,
            ','.join(["{}={}".format(f, v) for f, v in zip(fields, vals)])
        ))
    c.__repr__ = __repr__
    return c

# ===========================================

def tostr(o):
    if not isinstance(o, str):
        return str(unicode(o).encode('utf-8'))
    return o
