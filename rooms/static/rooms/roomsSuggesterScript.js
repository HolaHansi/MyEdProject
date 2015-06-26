var suggestions = []; //all suggestions provided by the server
var currentChoice = {}; //the suggestion currently on display

var userLatitude = 0; //current latitude of user
var userLongitude = 0; //current longitude of user

var roomLikedByUser = 'false'; // true if current suggestion is liked by user


$(document).ready(function () {
	//toggle buttons based on any parameters from the url
	if (location.href.indexOf('close=f') >= 0) {
		$('#nearbyBtn').removeClass('selected');
	}
	if (location.href.indexOf('empty=f') >= 0) {
		$('#emptyBtn').removeClass('selected');
	}
	if (location.href.indexOf('groups=') >= 0) {
		//extract the groups from the url
		groups = (location.href.substring(location.href.indexOf('groups=') + 7, location.href.length)).replace(/%20/g, ' ').split(',');
		groups[groups.length - 1] = groups[groups.length - 1].substring(0, (groups[groups.length - 1].indexOf('&') >= 0 ? groups[groups.length - 1].indexOf('&') : groups[groups.length - 1].length));
		//unselect the groups mentioned
		for (i = 0; i < groups.length; i++) {
			$('[id="' + groups[i] + '"').removeClass('selected');
		}
	}
	//get the user's location, then send a get request if that's successful and display the initial suggestion
	getLocation();
	//when the user clicks the next suggestion button, load the next suggestion
	$('#nextSuggestionBtn').click(function () {
		currentChoice = suggestions[currentChoice.index + 1];
		loadChoice();
	});

	$('#likeBtn').click(function () {
	var locationId = currentChoice.locationId;
	$.post('/like/', {
		'locationId': locationId,
		'roomLikedByUser': roomLikedByUser
	})
	.done(function(){
		if (roomLikedByUser=='false') {
			$('#likeBtn').html('<i class="fa fa-star"></i> liked').css({'opacity':0.5});
			roomLikedByUser = 'true';
		} else {
			$('#likeBtn').html('<i class="fa fa-star"></i> like').css({'opacity':1});
			roomLikedByUser = 'false';
		}
	});


    });




	//when the user starts a search...
	$('#retryBtn').click(function () {
		// if still searching for tutorial rooms
		if ($('#shutBtn').hasClass('selected')) {
			// get a new list of suggestions from the server based on the user's options
			//TODO: update for tut rooms
			getSuggestions($('#nearbyBtn').hasClass('selected'), $('#bookableBtn').hasClass('selected'), $('#computerBtn').hasClass('selected'), $('#whiteboardBtn').hasClass('selected'), $('#blackboardBtn').hasClass('selected'), $('#projectorBtn').hasClass('selected'), getUnselectedGroups());
			$('#nextSuggestionBtn').removeClass('disabled');
		} else {
			//TODO: work out what to do
			location.href = ('/bookable/#close=' + $('#nearbyBtn').hasClass('selected') + '&empty=' + $('#emptyBtn').hasClass('selected') + '&groups=' + getUnselectedGroups().join().replace(/ /g, '%20'));
		}
	});
});

/*
   Get the list of suggestions from the server
   Parameters:
   nearby (boolean): whether the user is filtering by nearby
   empty (boolean): whether the user is filtering by empty
   group (string): the campus that the user is searching in.
   One of: ‘Central’,‘ECA’,'Accommodation Services’, 'Holyrood and High School Yards’,‘KB Labs’
*/
//TODO: update
function getSuggestions(nearby, bookable, pc, whiteboard, blackboard, projector, groups) {
	//send the get request
	$.get('http://127.0.0.1:8000/bookable/filter', {
			'nearby': nearby,
			'pc': pc,
			'bookable': bookable,
			'whiteboard': whiteboard,
			'blackboard': blackboard,
			'projector': projector,
			'groupsUnselected[]': groups,
			'latitude': userLatitude,
			'longitude': userLongitude
		})
		.done(function (data) {
			//if successful, save the data received
			suggestions = data;
			//and an index to each of the JSONs
			for (var i = 0; i < suggestions.length; i++) {
				suggestions[i].index = i;
			}
			//load the first suggestion
			currentChoice = suggestions[0];
			loadChoice();
		});
}


/*
Liked returns true if the current suggestion is liked by the user, and false otherwise.
 */

function liked(locationId) {
    $.get('/like/', {
        'locationId': locationId
    })
    .done(function(data) {
        roomLikedByUser = data;
		if (roomLikedByUser=='true') {
			$('#likeBtn').html('<i class="fa fa-star"></i> liked').css({'opacity':0.5});
		}else{
			$('#likeBtn').html('<i class="fa fa-star"></i> like').css({'opacity':1});
		}
    });
};







/*
   Populate the website with the suggestion
   Parameters: none
*/
//TODO: update
function loadChoice() {
	//populate the html
	$('#roomName').html(currentChoice.room_name);
	$('#buildingName').html(currentChoice.building_name);
	$('#distance').html(': ' + (distanceBetweenCoordinates(userLatitude, userLongitude, currentChoice.latitude, currentChoice.longitude)).toFixed(2) + 'km');
	$('#computerTick').addClass(currentChoice.pc ? "tick" : "cross").removeClass(currentChoice.pc ? "cross" : "tick");
	$('#bookableTick').addClass(currentChoice.locally_allocated ? "cross" : "tick").removeClass(currentChoice.locally_allocated ? "tick" : "cross");
	$('#printerTick').addClass(currentChoice.pc ? "tick" : "cross").removeClass(currentChoice.pc ? "cross" : "tick"); //TODO: make printer
	$('#whiteboardTick').addClass(currentChoice.whiteboard ? "tick" : "cross").removeClass(currentChoice.whiteboard ? "cross" : "tick");
	$('#blackboardTick').addClass(currentChoice.blackboard ? "tick" : "cross").removeClass(currentChoice.blackboard ? "cross" : "tick");
	$('#projectorTick').addClass(currentChoice.projector ? "tick" : "cross").removeClass(currentChoice.projector ? "cross" : "tick");

	//if the user has reached the end of the list of suggestions, disable the 'next' button
	if (currentChoice.index == suggestions.length - 1) {
		$('#nextSuggestionBtn').addClass('disabled');
	}

	// check if current choice is liked by user. This updates the variable
    liked(currentChoice.locationId);
}

/*
   Returns a list of all campuses in the options menu which aren't currently selected
   Parameters: none
*/
function getUnselectedGroups() {
	ids = [];
	$('#campusGroup :not(.selected)').each(function () {
		ids.push(this.id);
	});
	return ids;
}

/*
   Takes a pair of coordinates and calculates the distance between them, taking into account the curvature of the earth
   A little overkill maybe, but you never know, someone might be using InternProject from back home in Australia!
   Parameters:
   lat1 (float): the latitude of the first point
   long1 (float): the longitude of the first point
   lat2 (float): the latitude of the second point
   long2 (float): the longitude of the second point
*/
function distanceBetweenCoordinates(lat1, long1, lat2, long2) {
	var R = 6371; // kilometres
	var t1 = toRadians(lat1);
	var t2 = toRadians(lat2);
	var dt = toRadians(lat2 - lat1);
	var dl = toRadians(long2 - long1);

	var a = Math.sin(dt / 2) * Math.sin(dt / 2) +
		Math.cos(t1) * Math.cos(t2) *
		Math.sin(dl / 2) * Math.sin(dl / 2);
	var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

	return R * c;
}

function toRadians(x) {
	return x * Math.PI / 180;
}


// Geolocation functions{

function getLocation() {
	//check that the browser is compatible
	if (navigator.geolocation) {
		//get the user's current coordinates or throw an error if that's not possible
		navigator.geolocation.getCurrentPosition(savePosition, showError);
	} else {
		alert('You browser does not support geolocation');
	}
}

//save the current positions, then get suggestions from the server
function savePosition(position) {
	userLatitude = position.coords.latitude;
	userLongitude = position.coords.longitude;
	//TODO: update
	getSuggestions($('#nearbyBtn').hasClass('selected'), $('#bookableBtn').hasClass('selected'), $('#computerBtn').hasClass('selected'), $('#whiteboardBtn').hasClass('selected'), $('#blackboardBtn').hasClass('selected'), $('#projectorBtn').hasClass('selected'), getUnselectedGroups());
}

//if impossible to get user's current coordinates, display a relevant error message
function showError(error) {
	switch (error.code) {
	case error.PERMISSION_DENIED:
		alert("Geolocation required for this app.")
		break;
	case error.POSITION_UNAVAILABLE:
		alert("Location information is unavailable.  Refresh the page or try again later.  ");
		break;
	case error.TIMEOUT:
		alert("The request to get user location timed out.  Refresh the page or try again later.  ");
		break;
	case error.UNKNOWN_ERROR:
		alert("An unknown error occurred when attempting to find your location.  Refresh the page or try again later.  ");
		break;
	}
}

// Geolocation functions}