// saves that this user has booked a room to the database
// then navigates to the room booking website
// TODO: automatically book the room for them (I hope!)
// parameters:
// id (string): the id of the location to be booked
function bookRoom(id){
    $.post(rootURL + '/history/',{
        'locationId': id,
        'clearAll': false
    }).done(function(data){
        // TODO: Book the room
        // until we have that functionality ourselves, just navigate to TED's booking page
        window.location.href = 'https://www.ted.is.ed.ac.uk/UOE1415STU_WRB/default.aspx';
    });
}
