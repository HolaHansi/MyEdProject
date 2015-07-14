from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def ratioToPercent(free, total):
    # Divides free by total and returns the result as a percentage
    if total == 0:
        return 0
    else:
        return round(free / float(total) * 100)


@register.filter
def facilities(room):
    # Returns an HTML list of all the facilities the room has
    to_return = ''
    if room.pc:
        to_return += '<span class="custom-glyphicon glyphicon-computer" aria-hidden="true"></span> '
    if room.printer:
        to_return += '<span class="custom-glyphicon glyphicon-printer" aria-hidden="true"></span> '
    if room.projector:
        to_return += '<span class="custom-glyphicon glyphicon-projector" aria-hidden="true"></span> '
    if room.blackboard:
        to_return += '<span class="custom-glyphicon glyphicon-blackboard-custom" aria-hidden="true"></span> '
    if room.whiteboard:
        to_return += '<span class="custom-glyphicon glyphicon-whiteboard" aria-hidden="true"></span> '
    if to_return == '':
        to_return = "<div id='blackboardTick' class='tickOrCross cross'></div>"
    return mark_safe(to_return)
