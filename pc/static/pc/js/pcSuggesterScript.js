var suggestions = []; //all suggestions provided by the server
var currentChoice = {}; //the suggestion currently on display

var userLatitude = 0; //current latitude of user
var userLongitude = 0; //current longitude of user

var pcLikedByUser = 'false'; // true if current suggestion is liked by user


$(document).ready(function () {
	//get the user's location, then send a get request if that's successful and display the initial suggestion
	getLocation();

	//when the user clicks the next suggestion button, load the next suggestion
	$('#nextSuggestionBtn').click(function () {
		currentChoice = suggestions[currentChoice.index + 1];
		loadChoice();
	});

	//when the user clicks the like button, like or unlike the room as appropriate
	$('#likeBtn').click(function () {
		var pc_id = currentChoice.id;
		$.post('/like/', {
				'pc_id': pc_id,
				'pcLikedByUser': pcLikedByUser
			})
			.done(function () {
				if (pcLikedByUser == 'false') {
					$('#likeBtn').html('<i class="fa fa-star"></i> liked').css({
						'opacity': 0.5
					});
					pcLikedByUser = 'true';
				} else {
					$('#likeBtn').html('<i class="fa fa-star"></i> like').css({
						'opacity': 1
					});
					pcLikedByUser = 'false';
				}
			});
	});

	//when the user starts a new search, get the appropriately filtered list of suggestions from the server
	$('#retryBtn').click(function () {
		getSuggestions($('#nearbyBtn').hasClass('selected'), $('#emptyBtn').hasClass('selected'), getUnselectedCampuses());
	});
	//switch to tutorial rooms when the switch button is pressed
	$('#switchBtn').click(function () {
		location.href='/bookable'
	});
});


/*
	Check if the current suggestion is liked by the user and change the style of the like button as appropriate
	Parameters: locationId (string) - the id of the suggestion to be checked
 */
function liked(pc_id) {
	$.get('/like/', {
			'pc_id': pc_id
		})
		.done(function (data) {
			pcLikedByUser = data;
			if (pcLikedByUser == 'true') {
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
   Get the list of suggestions from the server
   Parameters:
   nearby (boolean): whether the user is filtering by nearby
   empty (boolean): whether the user is filtering by empty
   campuses (string): the campuses that the user doesn't want
   One of: ‘Central’,‘ECA’,'Accommodation Services’, 'Holyrood and High School Yards’,‘KB Labs’
*/
function getSuggestions(nearby, empty, campuses) {
	//send the get request
	$.get('/open/filter', {
			'nearby': nearby,
			'empty': empty,
			'campusesUnselected[]': campuses,
			'latitude': userLatitude,
			'longitude': userLongitude
		})
		.done(function (data) {
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
   Populate the website with the suggestion
   Parameters: none
*/
function loadChoice() {
	//populate the html
	$('#roomName').html(currentChoice.name);
	$('#buildingName').html(currentChoice.campus);
	$('#distance').html(': ' + (distanceBetweenCoordinates(userLatitude, userLongitude, currentChoice.latitude, currentChoice.longitude)).toFixed(2) + 'km');
	$('#computersFree').html(': ' + currentChoice.free + '/' + currentChoice.seats);

	//if the user has reached the end of the list of suggestions, disable the 'next' button
	if (currentChoice.index == suggestions.length - 1) {
		$('#nextSuggestionBtn').addClass('disabled');
	}
	// check if current choice is liked by user. This updates the variable
	liked(currentChoice.id);
}

/* 
   Returns a list of all campuses in the options menu which aren't currently selected
   Parameters: none
*/
function getUnselectedCampuses() {
	ids = [];
	$('#campusGroup :not(.selected)').each(function () {
		ids.push(this.id);
	});
	return ids;
}


/* 
   Takes a pair of coordinates and calculates the distance between them, taking into account the curvature of the earth
   A little overkill maybe, but you never know, someone might be using core from back home in Australia!
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
	getSuggestions($('#nearbyBtn').hasClass('selected'), $('#emptyBtn').hasClass('selected'), getUnselectedCampuses());
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