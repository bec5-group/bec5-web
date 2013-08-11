from django.utils import simplejson
from django.template import Library

register = Library()

@register.filter
def jsonify(object):
    return simplejson.dumps(object, separators=(',', ':'))
