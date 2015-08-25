from django import template
from django.utils.safestring import mark_safe
import datetime
from core.utilities import get_availability, getOpenHours, time_until_unavailable, time_until_available

register = template.Library()


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
    return mark_safe(to_return)


@register.filter
def get_batch(room):
    avail = room['availability']
    if avail == 'availableNow':
        html_return = '<span class="badge check"><i class="fa fa-check avail"></i></span>'
    elif avail == 'notAvailable':
        html_return = '<span class="badge times"><i class="fa fa-times"></i></span>'
    elif avail == 'localAvailable':
        html_return = '<span class="badge minus"><i class="fa fa-minus avail"></i></span>'
    else:
        html_return = "Error - unknown type of availability"
    return mark_safe(html_return)


@register.filter
def get_availFor(room):
    avail = room['availability']

    if avail == 'availableNow':
        html_return = '<p><i class="fa fa-check-circle"></i></p>'
        html_return += '<div class="descriptionRoom"><p>Available for less than</p></div>'
        html_return += '<p>' + room['availableFor'] + '</p>'

    elif avail == 'notAvailable':
        if room['locally_allocated']:
            html_return = '<p><i class="fa fa-exclamation-triangle"></i></p>'
            html_return += '<div class="descriptionRoom"><p>Locally Allocated</p></div>'
            html_return += '<p>n/a</p>'
        else:
            html_return = '<p><i class="fa fa-hourglass"></i></p>'
            html_return += '<div class="descriptionRoom"><p>Will be available</p></div>'
            html_return += '<p>' + room['unavailableFor'] + '</p>'

    elif avail == 'localAvailable':
        html_return = '<p><i class="fa fa-exclamation-triangle"></i></p>'
        html_return += '<div class="descriptionRoom"><p>Locally Allocated</p></div>'
        html_return += '<p>n/a</p>'

    else:
        html_return = "Error - unknown type of availability"

    return mark_safe(html_return)


@register.filter
def facilitiesRoom(room):
    """
    this is facilities for history which takes dictionary rather than an object.
    :param room:
    :return:
    """
    # Returns an HTML list of all the facilities the room has
    to_return = ''
    if room['pc']:
        to_return += '<span class="custom-glyphicon glyphicon-computer" aria-hidden="true"></span> &nbsp; '
    if room['printer']:
        to_return += '<span class="custom-glyphicon glyphicon-printer" aria-hidden="true"></span> &nbsp; '
    if room['projector']:
        to_return += '<span class="custom-glyphicon glyphicon-projector" aria-hidden="true"></span>  &nbsp;'
    if room['blackboard']:
        to_return += '<span class="custom-glyphicon glyphicon-blackboard-custom" aria-hidden="true"></span> &nbsp; '
    if room['whiteboard']:
        to_return += '<span class="custom-glyphicon glyphicon-whiteboard" aria-hidden="true"></span> &nbsp; '
    return mark_safe(to_return)


@register.filter
def booked_at_time(room):
    """
    returns the historical booking time for the room in proper format.
    :param room:
    :return:
    """
    time = room.booked_at_time
    hour = time.hour
    minute = time.minute
    day = time.day
    month = time.month

    if minute < 10:
        minute = str(0) + str(minute)

    if hour < 10:
        hour = str(0) + str(hour)

    form_string = str(day) + '/' + str(month) + '/2015' + ' ' + str(hour) + ':' + str(minute)

    return form_string


@register.filter
def locally_allocated(room):
    return room.locally_allocated


@register.filter
def openTimeRoom(room):
    """
    returns the current opening time.
    :param room:
    :return:
    """
    # if no opening hours known, return unkown
    if not room['weekdayOpen']:
        return 'n/a'

    now = datetime.datetime.now()
    weekday = now.weekday()
    result = ''
    if 0 <= weekday <= 4:
        result = str(room['weekdayOpen'])[0:5]
    elif weekday == 5:
        result = str(room['saturdayOpen'])[0:5]
    elif weekday == 6:
        result = str(room['sundayOpen'])[0:5]
    return result


@register.filter
def closingTimeRoom(room):
    """
    returns the current closing time.
    :param room:
    :return:
    """
    # if no opening hours known, return unkown
    if not room['weekdayClosed']:
        return 'n/a'

    now = datetime.datetime.now()
    weekday = now.weekday()
    result = ''
    if 0 <= weekday <= 4:
        result = str(room['weekdayClosed'])[0:5]
    elif weekday == 5:
        result = str(room['saturdayClosed'])[0:5]
    elif weekday == 6:
        result = str(room['sundayClosed'])[0:5]
    return result


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
    if 0 <= weekday <= 4:
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
    if 0 <= weekday <= 4:
        result = str(place.weekdayClosed)[0:5]
    elif weekday == 5:
        result = str(place.saturdayClosed)[0:5]
    elif weekday == 6:
        result = str(place.sundayClosed)[0:5]
    return result


@register.filter
def inUse(lab):
    """
    returns how many PCs are in use
    :param lab:
    :return:
    """
    used = lab.seats - lab.free
    return used


@register.filter
def lab_badge_class(lab):
    """
    returns 'free', 'busyish' or 'full' depending on how full the lab is,
    or 'shut' if the lab is shut
    :param lab: the lab we're asking about
    :return: string: the class of the badge for this lab as decided by how busy it is
    """
    # Note the cutoff points are entirely arbitrary, simply what felt intuitive to me
    if lab.openInfo == 'closed':
        return 'shut'
    if lab.ratio > 0.75:
        return 'free'
    if lab.ratio > 0.5:
        return 'busyish'
    return 'full'


@register.filter
def room_badge_class(room):
    """
    returns 'free', 'unknown' or 'full' depending on the room's availability
    :param room: the room we're asking about
    :return: string: the class of the badge for this room as decided its availability
    """
    if get_availability(room) == 'available':
        return 'free'
    elif get_availability(room) == 'busy' or get_availability(room) == 'shut':
        return 'full'
    else:
        return 'unknown'


@register.filter
def room_badge_icon_class(room):
    """
    returns 'check', 'minus' or 'times' depending on the room's availability
    :param room: the room we're asking about
    :return: string: the class of the icon for the badge for this room as decided its availability
    """
    if get_availability(room) == 'available':
        return 'check'
    elif get_availability(room) == 'busy' or get_availability(room) == 'shut':
        return 'times'
    else:
        return 'minus'


@register.filter
def room_availability_icon_class(room):
    """
    returns the fa class of the icon for the availability display depending on the room's availability
    :param room: the room we're asking about
    :return: string: the class of the icon for the badge for this room as decided its availability
    """
    if get_availability(room) == 'busy' or get_availability(room) == 'shut':
        return 'hourglass'
    elif room.locally_allocated == 1 or (
        get_availability(room) == 'available' and getOpenHours(room)['closingHour'] is None):
        return 'exclamation-triangle'
    else:
        return 'check-circle'


@register.filter
def opening_hours(lab):
    """
    returns the lab's opening hours if known, or 'unknown' if not
    :param lab:
    :return: string: the opening hours of the lab as HTML
    """
    if openTime(lab) == 'n/a':
        return mark_safe("<p>Unknown</p>")
    else:
        return mark_safe(
            "<p class='openTimeP'>" + openTime(lab) + "</p> <p class='closingTimeP'>" + closingTime(lab) + "</p>")


@register.filter
def availability_text(room):
    """
    returns the availability of the room
    :param room:
    :return: string: the availability of the room as HTML
    """
    if get_availability(room) == 'available' and getOpenHours(room)['closingHour'] is not None:
        return mark_safe('<div class="descriptionRoom">Available for:</div><p>' + time_until_unavailable(room) + '</p>')
    elif get_availability(room) == 'busy' or get_availability(room) == 'shut':
        return mark_safe('<div class="descriptionRoom">Available' + (
            'in' if time_until_available(room) != 'Tomorrow' else ''
        ) + ':</div><p>' + time_until_available(room) + '</p>')
    else:
        return mark_safe('<div style="margin-bottom: -3px">' + (
            "Opening times" if get_availability(room) == 'available' else "Availability") + '</div><div>unknown</div>')


@register.filter
def maybe_disabled(room):
    """
    disables the book now button if the room is unavailable
    :param room:
    :return: string: disabled or empty
    """
    if get_availability(room) != 'available':
        return 'disabled'
    return ''


@register.filter
def get_id(room, type):
    """
    returns the location id or history id
    :param room:
    :param type: 'favourite' or 'history'
    :return: string: locatoin/history id
    """
    if type == 'history':
        return room.history_id
    else:
        return room.locationId
