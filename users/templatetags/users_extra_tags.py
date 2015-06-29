from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()

@register.filter
def ratioToPercent(free,total):
    '''Divides free by total and returns the result as a percentage'''
    if (total==0):
        return 0
    else:
        return round(free/float(total)*100)

@register.filter
@stringfilter
def processPCName(name,campus):
    '''Processes the name of the open access study space to make it more human readable'''
    regex = re.compile(campus + '( - )? ?', re.IGNORECASE)
    return re.sub(regex,'',name)

