import json
from django.template import Library

register = Library()

@register.filter
def jsonify(obj):
    return json.dumps(obj, separators=(',', ':'))
