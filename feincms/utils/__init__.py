# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------

try:
    from hashlib import md5
except ImportError:
    import md5

from django.conf import settings as django_settings
from django.db.models import AutoField
from django.utils.importlib import import_module
from django.utils import six


# ------------------------------------------------------------------------
def get_object(path, fail_silently=False):
    # Return early if path isn't a string (might already be an callable or
    # a class or whatever)
    if not isinstance(path, six.string_types):
        return path

    try:
        return import_module(path)
    except ImportError:
        try:
            dot = path.rindex('.')
            mod, fn = path[:dot], path[dot+1:]

            return getattr(import_module(mod), fn)
        except (AttributeError, ImportError):
            if not fail_silently:
                raise

# ------------------------------------------------------------------------
def collect_dict_values(data):
    dic = {}
    for key, value in data:
        dic.setdefault(key, []).append(value)
    return dic

# ------------------------------------------------------------------------
def copy_model_instance(obj, exclude=None):
    """
    Copy a model instance, excluding primary key and optionally a list
    of specified fields.
    """

    exclude = exclude or ()
    initial = dict([(f.name, getattr(obj, f.name))
                    for f in obj._meta.fields
                    if not isinstance(f, AutoField) and
                       not f.name in exclude and
                       not f in obj._meta.parents.values()])
    return obj.__class__(**initial)

# ------------------------------------------------------------------------
def shorten_string(str, max_length=50, ellipsis=u' … '):
    """
    Shorten a string for display, truncate it intelligently when too long.
    Try to cut it in 2/3 + ellipsis + 1/3 of the original title. Also try to
    cut the first part off at a white space boundary instead of in mid-word.

    >>> s = shorten_string("Der Wolf und die Grossmutter assen im Wald zu mittag", 15, ellipsis="_")
    >>> s
    'Der Wolf und_ag'
    >>> len(s)
    15

    >>> s = shorten_string(u"Haenschen-Klein, ging allein, in den tiefen Wald hinein", 15)
    >>> s
    u'Haenschen \u2026 ein'
    >>> len(s)
    15

    >>> shorten_string(u"Badgerbadgerbadgerbadgerbadger", 10, ellipsis="-")
    u'Badger-ger'
    """

    if len(str) >= max_length:
        first_part = int(max_length * 0.6)
        next_space = str[first_part:(max_length // 2 - first_part)].find(' ')
        if next_space >= 0 and first_part + next_space + len(ellipsis) < max_length:
            first_part += next_space
        return str[:first_part] + ellipsis + str[-(max_length - first_part - len(ellipsis)):]
    return str

# ------------------------------------------------------------------------
def path_to_cache_key(path, max_length=200, prefix=""):
    """
    Convert a string (path) into something that can be fed to django's
    cache mechanism as cache key. Ensure the string stays below the
    max key size, so if too long, hash it and use that instead.
    """

    from django.utils.encoding import iri_to_uri
    path = iri_to_uri(path)

    # logic below borrowed from http://richwklein.com/2009/08/04/improving-django-cache-part-ii/
    # via acdha's django-sugar
    if len(path) > max_length:
        m = md5()
        m.update(path)
        path = m.hexdigest() + '-' + path[:max_length - 20]

    cache_key = 'FEINCMS:%d:%s:%s' % (
        getattr(django_settings, 'SITE_ID', 0),
            prefix,
            path,
    )
    return cache_key

# ------------------------------------------------------------------------
