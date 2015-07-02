from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
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


@register.filter
@stringfilter
def processRoomName(name):
    '''Processes the name of the tutorial room to make it more human readable'''
    if name[0:2]=='zz':
        return name[2:]
    return name

@register.filter
def facilities(room):
    '''Returns an HTML list of all the facilities the room has'''
    toReturn=''
    if room.pc:
        toReturn+='<span class="custom-glyphicon glyphicon-computer" aria-hidden="true"></span> '
    if room.printer:
        toReturn+='<span class="custom-glyphicon glyphicon-printer" aria-hidden="true"></span> '
    if room.projector:
        toReturn+='<span class="custom-glyphicon glyphicon-projector" aria-hidden="true"></span> '
    if room.blackboard:
        toReturn+='<span class="custom-glyphicon glyphicon-blackboard-custom" aria-hidden="true"></span> '
    if room.whiteboard:
        toReturn+='<span class="custom-glyphicon glyphicon-whiteboard" aria-hidden="true"></span> '
    if toReturn=='':
        toReturn="<div id='blackboardTick' class='tickOrCross cross'></div>"
    return mark_safe(toReturn)
