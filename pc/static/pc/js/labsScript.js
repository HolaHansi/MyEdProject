var suggestions = []; //all suggestions provided by the server
var currentChoice = {}; //the suggestion currently on display

var userLatitude = 0; //current latitude of user
var userLongitude = 0; //current longitude of user

var pcLikedByUser = false; // whether current suggestion is liked by user

var map; // the Google Map object
var mapOptions; // the JSON of options for the map
var directionOptions; // the JSON of options for getting directions
var geocodingOptions; // the JSON of options for translating an address to its geolocation (geocoding)
var directionsService; // the Google directions service object, the bit that calculates the route
var directionsDisplay;  // the Google directions renderer object, the bit that displays the route
var geocoder; // the Google object for geocoding

//resize the JS styled elements if the window resizes
$(window).resize(resizeElements);

$(document).ready(function () {
    //Create the map
    makeMap();
    
    //get the user's location, then send a get request if that's successful and display the initial suggestion
	getLocation();
    
	//when the user clicks the next button, load the next suggestion
	$('.right-arrow').click(function () {
        loadNextSuggestion();
	});
    
	//when the user clicks the previous button, load the previous suggestion
	$('.left-arrow').click(function () {
        loadPreviousSuggestion();
	});
    
    //when the user clicks the like button, like or unlike the room as appropriate
	$('.fa-star').click(function () {
		var pc_id = currentChoice.id;
        // send the like request to the server
		$.post('/like/', {
				'pc_id': pc_id,
				'pcLikedByUser': (''+pcLikedByUser)
			})
			.fail(function () {
                alert('Failed to favourite location');
                // if the request failed, undo the star change
                $('.fa-star').toggleClass('unstarred');
                $('.fa-star').toggleClass('starred');
			});
        // toggle star colour
        $('.fa-star').toggleClass('unstarred');
        $('.fa-star').toggleClass('starred');
	});
    
    // Apply the JS styling
    resizeElements();
    
    // Enable swiping...
    $("#suggestion").swipe( {
        // Load the next suggestion if the user swipes left
        swipeLeft:function(event, direction, distance, duration, fingerCount) {
            loadNextSuggestion();
        },
        // Load the previous suggestion if the user swipes right
        swipeRight:function(event, direction, distance, duration, fingerCount) {
            loadPreviousSuggestion();
        },
        // Suggestion appears before the user lifts their finger
        triggerOnTouchEnd:false,
        // Ignore swipes on the map or the button
        excludedElements:'button, a, input, #currentMap'
    });
    
    // Set up location fixer
    $('#testGo').click(function(){
        // get the input from the user
        var newLocation=$('#testInput').val();
        // update the geocoding options
        geocodingOptions.address = newLocation;
        // get the coordinates from Google
        geocoder.geocode(geocodingOptions,function(results, status){
            // if successful, 
            if (status==google.maps.GeocoderStatus.OK){
                newCoordinates = results[0].geometry.location;
                userLatitude = newCoordinates.lat();
                userLongitude = newCoordinates.lng();
                getSuggestions(true, true, []);
            // otherwise, display an appropriate error message
            }else if (status==google.maps.GeocoderStatus.ZERO_RESULTS || status==google.maps.GeocoderStatus.INVALID_REQUEST){
                alert("Location not recognised - try again.");
            }else{
                alert("Lookup failed: " + status);
            }
        });
    });
    
});

// JS styling
function resizeElements(){
    // resize the arrows to take up the whole suggestion
    // set the height to 0 so the current height of the arrow isn't taken into account when calculating its new height
    $('.arrow').height(0);
    // if the window is big enough to display the whole page without scrolling, make the arrows take up the whole window (other than the navbar and height), otherwise make the arrows take up the whole suggestion but no more
    $('.arrow').height(Math.max((window.innerHeight - $('.navbar').outerHeight()-$('#optionsTitle').outerHeight()),($('body').height()-$('.navbar').outerHeight()-$('#optionsTitle').outerHeight())));
}

// populate the HTML with the previous suggestion's details
function loadPreviousSuggestion(){
    if(currentChoice.index>0){
        currentChoice = suggestions[currentChoice.index - 1];
        loadChoice();
    }
}
// populate the HTML with the next suggestion's details
function loadNextSuggestion(){
    if(currentChoice.index<suggestions.length-1){
        currentChoice = suggestions[currentChoice.index + 1];
        loadChoice();
    }
}

// Initialize Google settings, set fixed object properties and render the map:
// The JSON {lat:55.943655, lng:-3.188775} is dummy data and is overwritten as soon as the list of suggestions is received from the server
function makeMap(){
    //initialize Google objects
    directionsService = new google.maps.DirectionsService();
    directionsDisplay = new google.maps.DirectionsRenderer();
    geocoder = new google.maps.Geocoder();
    
    // initialise map options, hiding all controls other than a small zoom
    mapOptions = {
        panControl: false, 
        zoomControl: true,
        zoomControlOptions: {
            style: google.maps.ZoomControlStyle.SMALL
        },
        mapTypeControl: false,
        scaleControl: false,
        streetViewControl: false,
        overviewMapControl: false,
        rotateControl: false,
    };
    
    // initialise direction options
    directionOptions = {
      origin: {
          lat:55.943655,
          lng:-3.188775
      },
      destination: {
            lat:55.943655,
            lng:-3.188775
      },
      travelMode: google.maps.TravelMode.WALKING,
      provideRouteAlternatives: false,
      region: 'uk'
    }
    
    //initialise geocoding options
    geocodingOptions = {
        bounds: google.maps.LatLngBounds(google.maps.LatLng(55.913840,-3.243026),google.maps.LatLng(55.970666, -3.150412)),
        region: 'uk'
    };
    
    // create the map
    map = new google.maps.Map(document.getElementById("currentMap"), mapOptions);
    // bind the directions renderer to the map
    directionsDisplay.setMap(map);
}

// update the map with the new directions
function updateMap(){
    //update direction options
    directionOptions.origin= {
          lat:userLatitude,
          lng:userLongitude
      }
    directionOptions.destination= {
            lat:currentChoice.latitude, 
            lng:currentChoice.longitude
      }
    // calculate and display the route
    directionsService.route(directionOptions, function(result, status) {
        // if the route was successfully caluclated, display it
        if (status == google.maps.DirectionsStatus.OK) {
            directionsDisplay.setDirections(result);
        }
    });
}

/*
	Check if the current suggestion is liked by the user and color the star appropriately
	Parameters: locationId (string) - the id of the suggestion to be checked
 */
function liked(pc_id) {
    // send the request to the server to find out if this room is liked or not
	$.get('/like/', {
			'pc_id': pc_id
		})
		.done(function (data) {
			pcLikedByUser = (data==='true');
			if (pcLikedByUser) {
                $('.fa-star').removeClass('unstarred');
                $('.fa-star').addClass('starred');
			} else {
                $('.fa-star').addClass('unstarred');
                $('.fa-star').removeClass('starred');
			}
		});
};


/* 
   Get the list of suggestions from the server
   Parameters:
   nearby (boolean): whether the user is filtering by nearby
   empty (boolean): whether the user is filtering by empty
   campuses (array of strings): the campuses that the user doesn't want, a subset of [‘Central’,‘Lauriston’,"King's Buildings", 'Holyrood', 'Other']
*/
function getSuggestions(nearby, empty, campuses) {
	//send the get request
	$.get('filter', {
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
				//and an index to each of the JSONs
				for (var i = 0; i < suggestions.length; i++) {
					suggestions[i].index = i;
				}

				//load the first suggestion
				currentChoice = suggestions[0];
				loadChoice();
			} else {
				$('#roomName').html('n/a');
				$('.right-arrow').addClass('disabled');
				$('.left-arrow').addClass('disabled');
				alert('No rooms available fit that criteria.  Try again.  ');
			}
		})
        .fail(function(data){
            alert('Unable to get suggestions.  \n\nCheck your internet connection and refresh the page.  ');
        });
}

/* 
   Populate the website with the suggestion
   Parameters: none
*/
function loadChoice() {
	//populate the html
	$('#roomName').html(currentChoice.name);
	$('#computersFreeNumber').html(currentChoice.free);
    makepie("computersFreeGraph", currentChoice.free, (currentChoice.seats-currentChoice.free));
    
	//if the user has reached the end of the list of suggestions, disable the 'next' button
	if (currentChoice.index == suggestions.length - 1) {
		$('.right-arrow').addClass('disabled');
	}
	//if the user has reached the end of the list of suggestions, disable the 'next' button
	if (currentChoice.index == 0) {
		$('.left-arrow').addClass('disabled');
	}
    if (currentChoice.index != suggestions.length - 1 && currentChoice.index != 0) {
		$('.right-arrow').removeClass('disabled');
		$('.left-arrow').removeClass('disabled');
    }
	// check if current choice is liked by user and toggle the star icon appropriately
	liked(currentChoice.id);
    // update the map to the new coordinates
    updateMap();
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
	getSuggestions(true, true, []);
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