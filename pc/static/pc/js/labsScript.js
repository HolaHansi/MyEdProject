var suggestions = []; //all suggestions provided by the server
var currentChoice = {}; //the suggestion currently on display

var userLatitude = 0; //current latitude of user
var userLongitude = 0; //current longitude of user

var pcLikedByUser = false; // whether current suggestion is liked by user

//resize the JS styled elements if the window resizes
$(window).resize(resizeElements);

$(document).ready(function () {
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
    
    //For testing only, make the map:
    $('#currentMap').attr('src', 'https://maps.googleapis.com/maps/api/staticmap?size=' + (window.innerWidth - 60) + 'x300&key=AIzaSyBcrXTgUVxfXVLj3rh5gIUWyYRpveHMmEs&markers=size:medium%7Clabel:A%7C55.9460736605763,-3.20059955120087&markers=size:medium%7Clabel:B%7C55.9427113171065,-3.18914651870728')
    $('#currentMap').css({
        'height': '300px',
        'width': '2000px'
    })
    
    //Apply the JS styling
    resizeElements();
    
    //Enable swiping...
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
        triggerOnTouchEnd:false
    });
    
});

// JS styling
function resizeElements(){
    // resize the arrows to take up the whole suggestion
    $('.arrow').height(0);
    $('.arrow').height(Math.max((window.innerHeight - $('.navbar').outerHeight()-$('#optionsTitle').outerHeight()),($('body').height()-$('.navbar').outerHeight()-$('#optionsTitle').outerHeight())));
}

function loadPreviousSuggestion(){
    if(currentChoice.index>0){
        currentChoice = suggestions[currentChoice.index - 1];
        loadChoice();
    }
}
function loadNextSuggestion(){
    if(currentChoice.index<suggestions.length-1){
        currentChoice = suggestions[currentChoice.index + 1];
        loadChoice();
    }
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