// add triggers to all the room specific objects within the inputted room panel
// input: panelDiv (object): the room panel which we're applying functionality to
function addFunctionalityToRoomPanel(panelDiv){
    
    // book this room when the 'Book Now' button is selected
    $('.bookNow', panelDiv).click(function(){
        id = $(this).parents('.panel-default').attr('data-locationId');
        bookRoom(id);
    })
    
    // display the calendar when the calendar button is selected
    $(".calBtn", panelDiv).click(function() {
        
        // get the location id from the parent div
        locationId = $(this).parents('.panel-default').attr('data-locationId');

        // get the room name from the the div with class roomName + locationId.
        // the id of this div is the name of the room.
        var roomName = $(".roomName." + locationId).attr('id');

        // change the heading label for the modal to the room name.
        $('#myModalLabel').html(roomName);

        // get all activities on this room.
        $.get(rootURL + 'calendar/', {
                'locationId': locationId
        })
        .done(function(activities){
            // convert all activities to a format that FullCalendar understands
            // get current time
            var dateNow = moment().format("YYYY-MM-DD");

            var events = [];
            for (var i=0; i<=activities.length - 1; i++) {
                var act = activities[i];
                var title = act.name;
                var start = act.startTime;
                var end = act.endTime;
                var dict = [{title: title, start: start, end: end}];
                events = events.concat(dict);
            };

            // initialize a calendar in the modal with the activities as events.
            $('#calendar').fullCalendar({
                header: {
                    left: 'prev,next',
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
            });
        });

    });
}
