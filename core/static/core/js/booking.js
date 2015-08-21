// saves that this user has booked a room to the database
// then navigates to the room booking website
// TODO: automatically book the room for them (I hope!)
// parameters:
// id (string): the id of the location to be booked
function bookRoom(id){
    $.post('/history/',{
        'locationId': id,
        'clearAll': false
    }).done(function(data){
        window.location.href = 'https://www.ted.is.ed.ac.uk/UOE1415STU_WRB/default.aspx';
    });
}
