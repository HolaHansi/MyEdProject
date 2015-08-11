/**
 * Created by hanschristiangregersen on 07/08/15.
 */


// initialize some key variables
var locationId;
var dateNow = moment().format("YYYY-MM-DD");


$(document).ready(function(){
    // make sure calendar renders when modal shows.
    $('#myModal').on('shown.bs.modal', function () {
        $("#calendar").fullCalendar('render');
    });

    // when the modal closed - kill the calendar.
    $('#closeModal').click(function(){
       $('#calendar').fullCalendar('destroy');
    });

    // if the calBtn pressed, get all activities from the room whose locationId is in the
    // id of calBtn, and use them as events for a fullcalendar.
    $(".calBtn").click(function() {

    // locationId is the id of the calBtn button.
    locationId = $(this).attr('id');

    // ret the room name from the the div with class roomName + locationId.
    className = ".roomName." + locationId;
    roomNameClass = $(className);
    // the id of this div is the name of the room.
    roomName = roomNameClass.attr('id');

    // change the heading label for the modal to the room name.
    $('#myModalLabel').html(roomName);

    // initialize activities
    var activities = [];

    // initialize events and dict.
    var events = [];
    var dict = [];

    // get all activities on this room.
    $.get('/calendar/', {
            'locationId': locationId
    })
    .done(function(data){
            activities = data;

            // convert all activities to a format that FullCalendar understands
        for (var i=0; i<=activities.length - 1; i++) {
            var act = activities[i];
            var title = act.name;
            var start = act.startTime;
            var end = act.endTime;
            dict = [{title: title, start: start, end: end}];
            events = events.concat(dict);
        };

        // initialize a calendar in the modal with the activities as events.
        $('#calendar').fullCalendar({
        header: {left: 'prev,next',
            right: 'agendaWeek,agendaDay'
        },
        defaultDate: dateNow,
        // show week before day
        defaultView: 'agendaWeek',
        editable: false,
        businessHours: false,
        events: events,
        // unavailable red (from variables.less)
        eventColor: '#D9433B',
        allDaySlot: false,
        height: 400
		// end of calendar
        });
        // end of done function
        });

    // calBtb ends after
    });
});

