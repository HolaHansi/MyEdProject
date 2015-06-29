from django import template

register = template.Library()

@register.filter
def ratioToPercent(value,arg):
    '''Divides value by arg and returns the result as a percentage'''
    if (arg==0):
        return 0
    else:
        return round(value/float(arg)*100)

