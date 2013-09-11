from django.utils import simplejson
from django.template import Library

register = Library()

@register.filter
def jsonify(obj):
    return simplejson.dumps(obj, separators=(',', ':'))
