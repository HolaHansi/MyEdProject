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

	//when the user clicks the like button, like or unlike the room as appropriate
	$('#likeBtn').click(function () {
		var locationId = currentChoice.locationId;
		$.post('/like/', {
				'locationId': locationId,
				'roomLikedByUser': roomLikedByUser
			})
			.done(function () {
				if (roomLikedByUser == 'false') {
					$('#likeBtn').html('<i class="fa fa-star"></i> liked').css({
						'opacity': 0.5
					});
					roomLikedByUser = 'true';
				} else {
					$('#likeBtn').html('<i class="fa fa-star"></i> like').css({
						'opacity': 1
					});
					roomLikedByUser = 'false';
				}
			});
	});

	//when the user starts a search...
	$('#retryBtn').click(function () {
		getSuggestions($('#nearbyBtn').hasClass('selected'), $('#bookableBtn').hasClass('selected'), $('#computerBtn').hasClass('selected'), $('#printerBtn').hasClass('selected'), $('#whiteboardBtn').hasClass('selected'), $('#blackboardBtn').hasClass('selected'), $('#projectorBtn').hasClass('selected'), getUnselectedGroups());
	});
	$('#switchBtn').click(function () {
		location.href = ('/open');
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
function getSuggestions(nearby, bookable, pc, printer, whiteboard, blackboard, projector, groups) {
	//send the get request
	$.get('http://127.0.0.1:8000/bookable/filter', {
			'type': 'room',
			'nearby': nearby,
			'pc': pc,
			'bookable': bookable,
			'printer': printer,
			'whiteboard': whiteboard,
			'blackboard': blackboard,
			'projector': projector,
			'groupsUnselected[]': groups,
			'latitude': userLatitude,
			'longitude': userLongitude
		})
		.done(function (data) {
			console.log(data);
			//if successful, save the data received
			suggestions = data;
			//if at least one room fits the criteria
			if (suggestions.length > 0) {
				$('#nextSuggestionBtn').removeClass('disabled');
				//and an index to each of the JSONs
				for (var i = 0; i < suggestions.length; i++) {
					suggestions[i].index = i;
				}

				//load the first suggestion
				currentChoice = suggestions[0];
				loadChoice();
			} else {
				$('#optionsTriangle').click();
				$('#roomName').html('n/a');
				$('#buildingName').html('');
				$('#nextSuggestionBtn').addClass('disabled');
				$('#distance').html(': ' + ('0km'));
				alert('No rooms available fit that criteria.  Try again.  ');
			}
		});
}

/*
	Check if the current suggestion is liked by the user and change the style of the like button as appropriate
	Parameters: locationId (string) - the id of the suggestion to be checked
 */
function liked(locationId) {
	$.get('/like/', {
			'locationId': locationId
		})
		.done(function (data) {
			roomLikedByUser = data;
			if (roomLikedByUser == 'true') {
				$('#likeBtn').html('<i class="fa fa-star"></i> liked').css({
					'opacity': 0.5
				});
			} else {
				$('#likeBtn').html('<i class="fa fa-star"></i> like').css({
					'opacity': 1
				});
			}
		});
};

/*
   Populate the website with the suggestion
   Parameters: none
*/
function loadChoice() {
	//populate the html
	$('#roomName').html(processRoomName(currentChoice.room_name));
	$('#buildingName').html(currentChoice.building_name);
	$('#distance').html(': ' + (distanceBetweenCoordinates(userLatitude, userLongitude, currentChoice.latitude, currentChoice.longitude)).toFixed(2) + 'km');
	$('#computerTick').addClass(currentChoice.pc ? "tick" : "cross").removeClass(currentChoice.pc ? "cross" : "tick");
	$('#bookableTick').addClass(currentChoice.locally_allocated ? "cross" : "tick").removeClass(currentChoice.locally_allocated ? "tick" : "cross");
	$('#printerTick').addClass(currentChoice.printer ? "tick" : "cross").removeClass(currentChoice.printer ? "cross" : "tick");
	$('#whiteboardTick').addClass(currentChoice.whiteboard ? "tick" : "cross").removeClass(currentChoice.whiteboard ? "cross" : "tick");
	$('#blackboardTick').addClass(currentChoice.blackboard ? "tick" : "cross").removeClass(currentChoice.blackboard ? "cross" : "tick");
	$('#projectorTick').addClass(currentChoice.projector ? "tick" : "cross").removeClass(currentChoice.projector ? "cross" : "tick");

	//if the user has reached the end of the list of suggestions, disable the 'next' button
	if (currentChoice.index == suggestions.length - 1) {
		$('#nextSuggestionBtn').addClass('disabled');
	}

	// check if current choice is liked by user. This updates the button.  
	liked(currentChoice.locationId);
}

/*
	Process the room name into a more human readable format
	Paramters: name (string) - the room name to be processed
	Output: string - the processed room name
*/
function processRoomName(name) {
	if (name.slice(0, 2) == 'zz') {
		return name.slice(2, name.length);
	}
	return name;
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
	getSuggestions($('#nearbyBtn').hasClass('selected'), $('#bookableBtn').hasClass('selected'), $('#computerBtn').hasClass('selected'), $('#printerBtn').hasClass('selected'), $('#whiteboardBtn').hasClass('selected'), $('#blackboardBtn').hasClass('selected'), $('#projectorBtn').hasClass('selected'), getUnselectedGroups());
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