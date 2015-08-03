from django import template
from django.utils.safestring import mark_safe
import datetime

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
        to_return += '<span class="custom-glyphicon glyphicon-computer" aria-hidden="true"></span> &nbsp; '
    if room.printer:
        to_return += '<span class="custom-glyphicon glyphicon-printer" aria-hidden="true"></span> &nbsp; '
    if room.projector:
        to_return += '<span class="custom-glyphicon glyphicon-projector" aria-hidden="true"></span>  &nbsp;'
    if room.blackboard:
        to_return += '<span class="custom-glyphicon glyphicon-blackboard-custom" aria-hidden="true"></span> &nbsp; '
    if room.whiteboard:
        to_return += '<span class="custom-glyphicon glyphicon-whiteboard" aria-hidden="true"></span> &nbsp; '
    if to_return == '':
        to_return = "No Suitabilities"
    return mark_safe(to_return)



@register.filter
def openTime(place):
    """
    returns the current opening time.
    :param place:
    :return:
    """
    # if no opening hours known, return unkown
    if not place.weekdayOpen:
        return 'n/a'

    now = datetime.datetime.now()
    weekday = now.weekday()
    result = ''
    if weekday >= 0 and weekday <= 4:
        result = str(place.weekdayOpen)[0:5]
    elif weekday == 5:
        result = str(place.saturdayOpen)[0:5]
    elif weekday == 6:
        result = str(place.sundayOpen)[0:5]
    return result

@register.filter
def closingTime(place):
    """
    returns the current opening and closing hours.
    :param place:
    :return:
    """
    # if no opening hours known, return unkown
    if not place.weekdayOpen:
        return 'n/a'

    now = datetime.datetime.now()
    weekday = now.weekday()
    result = ''
    if weekday >= 0 and weekday <= 4:
        result = str(place.weekdayClosed)[0:5]
    elif weekday == 5:
        result = str(place.saturdayClosed)[0:5]
    elif weekday == 6:
        result = str(place.sundayClosed)[0:5]
    return result

@register.filter
def inUse(pc):
    """
    returns how many PCs are in use
    :param pc:
    :return:
    """
    used = pc.seats - pc.free
    return used
