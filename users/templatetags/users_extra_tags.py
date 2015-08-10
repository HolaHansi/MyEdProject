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
def get_batch(room):
    avail = room['availability']
    if avail == 'availableNow':
        htmlReturn = '<span class="badge check"><i class="fa fa-check avail"></i></span>'
    elif avail == 'notAvailable':
        htmlReturn = '<span class="badge times"><i class="fa fa-times"></i></span>'
    elif avail == 'localAvailable':
        htmlReturn = '<span class="badge minus"><i class="fa fa-minus avail"></i></span>'

    return mark_safe(htmlReturn)


@register.filter
def get_availFor(room):
    avail = room['availability']

    if avail == 'availableNow':
        htmlReturn = '<p><i class="fa fa-check-circle"></i></p>'
        htmlReturn += '<div class="descriptionRoom"><p>Available for less than</p></div>'
        htmlReturn += '<p>' + room['availableFor'] + '</p>'


    elif avail == 'notAvailable':
        if room['locally_allocated']:
            htmlReturn = '<p><i class="fa fa-exclamation-triangle"></i></p>'
            htmlReturn += '<div class="descriptionRoom"><p>Locally Allocated</p></div>'
            htmlReturn += '<p>n/a</p>'
        else:
            htmlReturn = '<p><i class="fa fa-hourglass"></i></p>'
            htmlReturn += '<div class="descriptionRoom"><p>Will be available</p></div>'
            htmlReturn += '<p>' + room['unavailableFor'] + '</p>'

    elif avail == 'localAvailable':
        htmlReturn = '<p><i class="fa fa-exclamation-triangle"></i></p>'
        htmlReturn += '<div class="descriptionRoom"><p>Locally Allocated</p></div>'
        htmlReturn += '<p>n/a</p>'

    return mark_safe(htmlReturn)

@register.filter
def get_bookBtn(room):
    if room['availability'] == 'availableNow':
        htmlReturn = '<a href="/" class="btn btn-default booknow roomBtn" role="button">Book Now</a>'
    else:
        htmlReturn = '<a href="/" class="btn btn-default booknow roomBtn disabled" role="button">Book Now</a>'

    return mark_safe(htmlReturn)

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
    if to_return == '':
        to_return = "No Suitabilities"
    return mark_safe(to_return)

@register.filter
def booked_at_time(room):
    """
    returns the historical booking time for the room in proper format.
    :param room:
    :return:
    """
    time = room['booked_at_time']
    hour = time.hour
    minute = time.minute
    day = time.day
    month = time.month

    if minute < 10:
        minute = str(0) + str(minute)

    if hour < 10:
        hour = str(0) + str(hour)

    formString = str(day) + '/' + str(month) + '/2015' + ' ' + str(hour) + ':' + str(minute)


    return formString





@register.filter
def locally_allocated(room):
    return room.locally_allocated


@register.filter
def openTimeRoom(room):
    """
    returns the current opening time.
    :param place:
    :return:
    """
    # if no opening hours known, return unkown
    if not room['weekdayOpen']:
        return 'n/a'

    now = datetime.datetime.now()
    weekday = now.weekday()
    result = ''
    if weekday >= 0 and weekday <= 4:
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
    :param place:
    :return:
    """
    # if no opening hours known, return unkown
    if not room['weekdayClosed']:
        return 'n/a'

    now = datetime.datetime.now()
    weekday = now.weekday()
    result = ''
    if weekday >= 0 and weekday <= 4:
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
