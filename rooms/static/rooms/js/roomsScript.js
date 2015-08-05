var suggestions = []; // all suggestions provided by the server
var currentChoice = {}; // the suggestion currently on display

var userLatitude = 55.943655; // current latitude of user
var userLongitude = -3.188775; // current longitude of user
// Note this is dummy data, pointed in the middle of George Square, which will be overwritten if the user allows location finding or manually enters their location

var roomLikedByUser = false; // whether current suggestion is liked by user
var searchingForBuildings = true; // whether we're currently searching for buildings (true) or tutorial rooms (false)
var currentBuildingId = ''; // the id of the building we're currently searching in, or '' if we're searching for a building

var refreshTimer; // the maps timeout variable for limiting number of queries per second to avoid limits
var idleReminder; // the timer variable which reminds the user they can swipe if they don't swipe within the first 5 seconds
var idleTime=0; // the length of time the user has gone without swiping

var map; // the Google Map object
var mapOptions; // the JSON of options for the map
var directionOptions; // the JSON of options for getting directions
var geocodingOptions; // the JSON of options for translating an address to its geolocation (geocoding)
var directionsService; // the Google directions service object, the bit that calculates the route
var directionsDisplay;  // the Google directions renderer object, the bit that displays the route
var geocoder; // the Google object for geocoding

// resize the JS styled elements if the window resizes
$(window).resize(function(){
    // don't slide the menu if repositioning due to viewport resize, just move it instantly
    $('#optionsMenu').addClass('transitionOff');
    resizeElements();
    // timeout needed to stop the transition in slower browsers
    // (yes, it's a bit of an ugly hack, but what to do with web dev isn't?)
    setTimeout(function(){
        $('#optionsMenu').removeClass('transitionOff');
    }, 100);
    
    //ensure any hidden campus buttons have the same selection state as the 'other' checkbox
    matchHiddenCampusesToOther();
});

// Initialisation
$(document).ready(function () {
    // Create the map
    makeMap();
    
    // if the user has changed their settings this session, use the new settings
    if (sessionStorage['roomOptions']){
        var options = JSON.parse(sessionStorage['roomOptions']);
        
        $('#nearbyCheckbox').attr('checked',options.nearby);
        $('#quietCheckbox').attr('checked',options.quiet);
        for (i in options.campuses){
            campus = options.campuses[i]
            $('#'+campus).attr('checked',false);
        }
    
    // otherwise, use and save the standard settings
    } else {
        // save the current options state
        var oldOptions = {
            nearby: $('#nearbyCheckbox').is(':checked'), 
            quiet: $('#quietCheckbox').is(':checked'), 
            campuses:getUnselectedCampuses()
        };
        sessionStorage['roomOptions'] = JSON.stringify(oldOptions)
    }
    
    // if the user has corrected their location this session, use the corrected coordinates
    if(sessionStorage['customCoordinates']=="true"){
        userLatitude = parseFloat(sessionStorage['userLatitude']);
        userLongitude = parseFloat(sessionStorage['userLongitude']);
	    getSuggestionsUsingOptions();
    
    // otherwise use JS to get their location
    } else {
        // get the user's location, then send a get request if that's successful and display the initial suggestion
	   getLocation();
    }
    // Apply the JS styling
    resizeElements();
    
    // initialize bootstrap switches
    $.fn.bootstrapSwitch.defaults.size = 'mini';
    $.fn.bootstrapSwitch.defaults.onColor = 'success';
    $.fn.bootstrapSwitch.defaults.offColor = 'danger';
    $.fn.bootstrapSwitch.defaults.onText = '✓';
    $.fn.bootstrapSwitch.defaults.offText = '☓';
    $.fn.bootstrapSwitch.defaults.handleWidth = 20;
    $.fn.bootstrapSwitch.defaults.labelWidth = 20;
    $('#optionsContent input[type="checkbox"]').bootstrapSwitch();
    
    //ensure the hamburger menu is always visible over the options menu
    $('#mainHamburgerMenuOptions').on('shown.bs.collapse', resizeOptionsMenu)
    $('#mainHamburgerMenuOptions').on('hidden.bs.collapse', resizeOptionsMenu)
    
    // remind the user they can swipe to see more suggestions if they don't do so quickly
    idleReminder = setTimeout(function(){
        $('#swipeReminder').css({'opacity':1, 'left':'0px'});
    }, 5000); // 5 second delay

    $('#switchViewBtn').click(function(){
        // toggle search mode
        searchingForBuildings = !searchingForBuildings;
        // if we're now back to searching for buildings, clear the current building
        if (searchingForBuildings){
            currentBuildingId = '';
        // if we're now searching within a building, save the building we're searching in
        } else {
            currentBuildingId = currentChoice.abbreviation;
        }
        // get new suggestions from the server
        getSuggestionsUsingOptions();
    });
    
	// when the user clicks the next button, load the next suggestion
	$('.right-arrow').click(function () {
        loadNextSuggestion();
	});
    
	// when the user clicks the previous button, load the previous suggestion
	$('.left-arrow').click(function () {
        loadPreviousSuggestion();
	});
    
    // when the user clicks the 'add to favourites' star, like or unlike the room as appropriate
	$('#suggestion .fa-star').click(function () {
		var pc_id = currentChoice.id;
        // send the like request to the server
		$.post('/like/', {
				'locationId': currentChoice.locationId,
				'roomLikedByUser': (''+roomLikedByUser)
			})
			.fail(function () {
                alert('Failed to favourite location');
                // if the request failed, undo the star change
                $('#suggestion .fa-star').toggleClass('unstarred');
                $('#suggestion .fa-star').toggleClass('starred');
			});
        // toggle star colour
        $('#suggestion .fa-star').toggleClass('unstarred');
        $('#suggestion .fa-star').toggleClass('starred');
	});
    
    // Enable swiping to switch suggestions
    $("#mainContainer").swipe( {
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
        // Ignore swipes on any buttons
        excludedElements:'button, a, input'
    });
    // Enable swiping on the options menu to open and close it
    // (note this is being applied to the body so that the user can swipe up from the options menu onto the body and it'll still be triggered,
    //  but due to the excludedElements property, it'll only register swipes on the options menu itself)
    $("body").swipe( {
        // Open the menu if the user swipes up
        swipeUp:function(event, direction, distance, duration, fingerCount) {
            if (!$('#optionsMenu').hasClass('opened')){
                toggleOptionsMenu();
            }
        },
        // Close the menu if the user swipes down
        swipeDown:function(event, direction, distance, duration, fingerCount) {
            if ($('#optionsMenu').hasClass('opened')){
                toggleOptionsMenu();
            }
        },
        // Menu appears before the user lifts their finger
        triggerOnTouchEnd:false,
        // this only covers the options menu
        excludedElements:'#navbar, #mainContainer, #optionsContent, input, a, button'
    });
    
    // Set up the location fixer
    $('#locationCorrectorGo').click(function(){
        // get the input from the user
        var newLocation=$('#locationCorrectorText').val();
        if (newLocation===''){
            // if the user leaves it blank, use their default location
            getLocation();
            return '';
        }
        // if the user hasn't narrowed down their search to Edinburgh (or elsewhere, as estimated by their using a comma), do it for them
        if (newLocation.indexOf('Edinburgh')==-1 && newLocation.indexOf(',')==-1){
            newLocation+=', Edinburgh';
        }
        // update the geocoding options
        geocodingOptions.address = newLocation;
        // get the coordinates from Google
        geocoder.geocode(geocodingOptions,function(results, status){
            // if successful, 
            if (status==google.maps.GeocoderStatus.OK){
                
                // save the new coordinates
                var newCoordinates = results[0].geometry.location;
                userLatitude = newCoordinates.lat();
                userLongitude = newCoordinates.lng();
                
                // save this to the local session
                sessionStorage['customCoordinates']=true;
                sessionStorage['userLatitude']=userLatitude;
                sessionStorage['userLongitude']=userLongitude;
                
                // display the suggestions using the new coordinates
                getSuggestionsUsingOptions();
                toggleOptionsMenu();   
                
            // otherwise, display an appropriate error message
            }else if (status==google.maps.GeocoderStatus.ZERO_RESULTS || status==google.maps.GeocoderStatus.INVALID_REQUEST){
                alert("Location not recognised - try again.");
            }else{
                alert("Lookup failed: " + status);
            }
        });
    });
    
    // also correct their location if they press enter while focus is on the location corrector textbox
    $('#locationCorrectorText').on('keydown', function (e) {
        if (e.which == 13) {
            $('#locationCorrectorGo').trigger('click');
            // unfocus from the textbox
            $(this).blur();
         }
    });
    
    // a wee easter egg just for a bit of fun
    // if the user enters the 'konami code' (up,up,down,down,left,right,left,right,b,a),
    // display a custom suggestion
    var kkeys = [], konami = "38,38,40,40,37,39,37,39,66,65";
    $(document).keydown(function(e) {
        kkeys.push( e.keyCode );
        if ( kkeys.toString().indexOf( konami ) >= 0 ) {
            $(document).unbind('keydown',arguments.callee);
            currentChoice['campus']='';
            currentChoice['longitude']=-3.186933;
            currentChoice['latitude']=55.949635;
            currentChoice['name']='The Hive';
            currentChoice['index']=0;
            currentChoice['free']=1337;
            currentChoice['seats']=9001;
            suggestions=[currentChoice];
            loadChoice();
            if($('#optionsMenu').hasClass('opened')){
                toggleOptionsMenu();
            }
        }
    });
    
    // display or hide the options menu when the options header is clicked
    $('#optionsTitle, .triangle, #searchWithNewOptionsBtn').click(toggleOptionsMenu);
    
    // take down the options menu if the user clicks off it
    $('#mainContainer').click(function(){
        if ($('#optionsMenu').hasClass('opened')){
            toggleOptionsMenu();
        }
    });
    
    // intialize campus buttons to act as checkboxes
    $('.campusCheckbox').click(function(){
        $(this).toggleClass('checked');
        $('input', this).prop('checked', !$('input', this).prop('checked'))
    });
    $('.campusCheckbox input').click(function(){
        $(this).prop('checked', !$(this).prop('checked'))
    });
    // when the 'other' checkbox is clicked, toggle all hidden campuses too
    $('#otherCheckbox').click(function(){
        $('.campusCheckbox').each(function(){
            if($(this).css('display')=='none'){
                $(this).toggleClass('checked');
            }
        });
    });
});

// JS styling {

// refresh all the JS styling
function resizeElements(){
    
    // resize the arrows to take up the whole suggestion
    resizeArrows();
    
    // reposition the menu:
    resizeOptionsMenu();
}

// resize the arrows to take up the whole suggestion
function resizeArrows(){
    // set the height to 0 so the current height of the arrow isn't taken into account when calculating its new height
    $('.arrow').height(0);
    // if the window is big enough to display the whole page without scrolling, make the arrows take up the whole window (other than the navbar and height), 
    // otherwise make the arrows take up the whole suggestion but no more
    $('.arrow').height(Math.max((window.innerHeight - $('.navbar').outerHeight()-$('#optionsTitle').outerHeight()),($('body').height()-$('.navbar').outerHeight()-$('#optionsTitle').outerHeight())));
}

// reposition the menu:
function resizeOptionsMenu(){
    // close the menu
    // needed even if menu is currently open to ensure all heights used in calculations are correct
    $('body').css( { 
        position: 'static',
        'overflow-y':'auto'
    });
    $('#optionsMenu').css({
        top:window.innerHeight-40,
        bottom:'auto'
    });
    $('#optionsContent').css({
        height: 'auto',
        'overflow-x': 'visible',
        'overflow-y': 'visible'
    })
    
    // if the menu is currently open:
    if($('#optionsMenu').hasClass('opened')){
        // prevent scrolling on the body if scrolling was previously possible
        if (window.innerHeight < $('body').innerHeight()){
            $('body').css( { 
                position: 'fixed',
                'overflow-y':'scroll'
            });
        }
        
        // where to position the top of the options in order to get the bottom at the bottom of the body (not viewport)
        optionsTop = (window.innerHeight - $('#optionsMenu').outerHeight())
        
        // if positioning the options there would cause the top to be too high (ie it would overlap the header), 
        // then move it down so that the top of the options is just below the header
        // and enable scrolling on the options menu
        // (only needed on very small viewports)
        if (optionsTop< $('.navbar').outerHeight() + 5 ){
            optionsTop = $('.navbar').outerHeight() + 5;
            contentHeight = (window.innerHeight - optionsTop) - $('#optionsTitle').outerHeight() - 10
            $('#optionsMenu').css({
                bottom:'0px', 
                top:optionsTop+'px'
            });
            $('#optionsContent').css({
                height: contentHeight + 'px',
                'overflow-y': 'scroll'
            })
        
        // if positioning the options menu there wouldn't be a problem, put it there
        } else{
            $('#optionsMenu').css({
                bottom:'0px', 
                top:optionsTop+'px'
            });
        }
        
    }
}

// JS styling }

// open or close the options menu
function toggleOptionsMenu(){
    $('#optionsMenu').toggleClass('opened');
    // apply the JS styling to reposition the options menu
    resizeElements();
    // if the options menu has just opened:
    if ($('#optionsMenu').hasClass('opened')){
        $('.arrow').addClass('disabled');
        $('#mainContainer').css('opacity',0.3);
    } else {
        $('#mainContainer').css('opacity',1);
        // check if the options have changed
        var newOptions = {
            nearby: $('#nearbyCheckbox').is(':checked'), 
            quiet: $('#quietCheckbox').is(':checked'), 
            campuses:getUnselectedCampuses()
        };
        var oldOptions = JSON.parse(sessionStorage['roomOptions']);
        var optionsChanged = oldOptions.nearby!=newOptions.nearby || oldOptions.quiet!=newOptions.quiet || (! arraysEqual(oldOptions.campuses,newOptions.campuses));
        // if they have, or the user specifically asked for a refresh, refresh the suggestions
        if (optionsChanged || $(this).prop('id')=='searchWithNewOptions'){
            getSuggestionsUsingOptions();
            sessionStorage['roomOptions'] = JSON.stringify(newOptions)
        // if they haven't, just continue where you left off
        } else {
            // if the user hasn't reached the end of the list of suggestions, re-enable the 'next' button
            if (currentChoice.index != suggestions.length - 1) {
                $('.right-arrow').removeClass('disabled');
            }
            // if the user isn't at the start of the list of suggestions, re-enable the 'previous' button
            if (currentChoice.index != 0) {
                $('.left-arrow').removeClass('disabled');
            }
            
        }
        // deselect all options
        $('#optionsMenu *').blur();
    }
}

// set any hidden campus buttons' selection state to that of the 'other' checkbox
function matchHiddenCampusesToOther(){
    $('.campusCheckbox').each(function(){
        if($(this).css('display')=='none'){
            if($('#otherCheckbox').hasClass('checked')){
                $(this).addClass('checked');
            }else{
                $(this).removeClass('checked');
            }
        }
    });
}

// populate the HTML with the previous suggestion's details
function loadPreviousSuggestion(){
    if(currentChoice.index>0 && (!($('#optionsMenu').hasClass('opened')))){
        currentChoice = suggestions[currentChoice.index - 1];
        loadChoice();
    }
}
// populate the HTML with the next suggestion's details
function loadNextSuggestion(){
    // don't remind the user they can swipe
    clearTimeout(idleReminder);
    $('#swipeReminder').css({'opacity':0, 'left':'-30px'});
    if(currentChoice.index<suggestions.length-1 && (!($('#optionsMenu').hasClass('opened')))){
        currentChoice = suggestions[currentChoice.index + 1];
        loadChoice();
    }
}

// Initialize Google settings, set fixed object properties and render the map:
// The JSON {lat:55.943655, lng:-3.188775} is dummy data and is overwritten as soon as the list of suggestions is received from the server
function makeMap(){
    // initialize Google objects
    directionsService = new google.maps.DirectionsService();
    directionsDisplay = new google.maps.DirectionsRenderer();
    geocoder = new google.maps.Geocoder();
    
    // initialise map options, hiding all controls other than a small zoom and pan
    mapOptions = {
        disableDefaultUI: true,
        panControl: true,
        panControlOptions: {
            position: google.maps.ControlPosition.TOP_LEFT
        },
        zoomControl: true,
        zoomControlOptions: {
            style: google.maps.ZoomControlStyle.SMALL,
            position: google.maps.ControlPosition.TOP_LEFT
        },
        mapTypeControl: false,
        scaleControl: false,
        streetViewControl: false,
        overviewMapControl: false,
        rotateControl: false,
        draggable: false,
        scrollwheel: false,
        // styles: [{ featureType: "poi", elementType: "labels", stylers: [{ visibility: "off" }]}], // disable Points of Interest (and therefore their popup menus)
        maxZoom: 17,
        backgroundColor: '#ffffff'
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
    
    // initialise geocoding options
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
    $('#busyAnimation').hide();
    // update direction options
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
        // if the route was successfully calculated, display it
        if (status == google.maps.DirectionsStatus.OK) {
            directionsDisplay.setDirections(result);
        // if the user is flicking through choices too quickly, wait before showing the map
        }else if (status == google.maps.DirectionsStatus.OVER_QUERY_LIMIT){
            $('#busyAnimation').show();
            clearTimeout(refreshTimer)
            refreshTimer = setTimeout(updateMap, 1000)
        } else {
            alert('Error: '+status);
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
			roomLikedByUser = (data==='true');
			if (roomLikedByUser) {
                $('#suggestion .fa-star').removeClass('unstarred');
                $('#suggestion .fa-star').addClass('starred');
			} else {
                $('#suggestion .fa-star').addClass('unstarred');
                $('#suggestion .fa-star').removeClass('starred');
			}
		});
};

// get the suggestions from the server using the current options chosen by the user as parameters
function getSuggestionsUsingOptions(){
    // get the list of campuses the user doesn't want
    var campuses=getUnselectedCampuses();
    var ids=[]
    // convert each id from the HTML id to the format needed by the backend, namely one of [‘Central’,‘Lauriston’,"King's Buildings", 'Holyrood', 'Other']
    for (i in campuses){
        var id=campuses[i];
        id = id.charAt(0).toUpperCase() + id.slice(1,id.indexOf('Checkbox'));
        if (id=='Kings'){
            id="King's Buildings";
        }
        ids.push(id)
    }
    // if all campuses are unselected, return all campuses
    if (ids.length==5){
        ids = [];
    }
    // get the suggestions 0613//TODO
    getSuggestions(true, true, false, false, false, false, currentBuildingId, $('#nearbyCheckbox').is(':checked'), ids); //TODO FIX
}

// returns the id of all campuses the user doesn't want included
function getUnselectedCampuses(){
    ids = [];
	$('.campusCheckbox:not(.checked)').each(function () {
        ids.push(this.id);
	});
	return ids;
}

/* 
   Get the list of suggestions from the server
   Parameters:
   bookable (boolean): whether the user wants only bookable rooms
   pc (boolean): whether the user wants only rooms with a pc
   printer (boolean): whether the user wants only rooms with a printer
   whiteboard (boolean): whether the user wants only rooms with a whiteboard
   pcblackboard(boolean): whether the user wants only rooms with a blackboard
   projector (boolean): whether the user wants only rooms with a projector
   building (string): the abbreviation of the building the user is searching within if they've chosen one, else ''
   nearby (boolean): whether the user is sorting by distance
   campuses (array of strings): the campuses that the user doesn't want, a subset of [‘Central’,‘Lauriston’,"King's Buildings", 'Holyrood', 'Other']
*/
function getSuggestions(bookable, pc, printer, whiteboard, blackboard, projector, building, nearby, campuses) {
	// send the get request
	$.get('filter', {
			'bookable': bookable,
			'pc': pc,
            'printer': printer,
            'whiteboard': whiteboard,
            'blackboard': blackboard,
            'projector': projector,
            'building': building,
            'nearby': nearby,
			'campusesUnselected[]': campuses,
			'latitude': userLatitude,
			'longitude': userLongitude
		})
		.done(function (data) {
			// if successful, save the data received
			suggestions = data;
			// if at least one room fits the criteria
			if (suggestions.length > 0) {
				// and an index to each of the JSONs
				for (var i = 0; i < suggestions.length; i++) {
					suggestions[i].index = i;
				}

				// load the first suggestion
				currentChoice = suggestions[0];
				loadChoice();
                if (suggestions.length==1){
                    // don't remind the user they can swipe if they can't
                    clearTimeout(idleReminder);
                }
			} else {
				$('.arrow').addClass('disabled');
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
    console.log(currentChoice)
	
    // change view to the appropriate version
    switchView();
    
    // populate the html
    
    if (searchingForBuildings){
        
        // populate the html
        $('#roomName').html(currentChoice.building_name);
        $('#roomsFreeNumber').html(currentChoice.rooms);
        // update the map to the new coordinates
        updateMap();
        // update the 'Take me there' Google Maps deeplink
        $('#toMapBtn').attr('href','https://www.google.com/maps/preview?saddr='+userLatitude+','+userLongitude+'&daddr='+currentChoice.latitude+','+currentChoice.longitude+'&dirflg=w');
    } else{
        
        $('#roomName').html(currentChoice.room_name);
        $('#roomsFreeNumber').html(currentChoice.capacity);
        $('#starContainer').show();
        // check if current choice is liked by user and toggle the star icon appropriately
        liked(currentChoice.locationId);
    }
    
	// if the user has reached the end of the list of suggestions, disable the 'next' button
	if (currentChoice.index == suggestions.length - 1) {
		$('.right-arrow').addClass('disabled');
	} else {
        $('.right-arrow').removeClass('disabled');
    }
	// if the user is at the start of the list of suggestions, disable the 'previous' button
	if (currentChoice.index == 0) {
		$('.left-arrow').addClass('disabled');
	} else {
		$('.left-arrow').removeClass('disabled');
    }
}

// Switch view from searching for rooms to searching for buildings
function switchView(){
    // if switching to buildings
    if (searchingForBuildings){
        // hide the favourites button
        $('#starContainer').hide();
        // change search version button to 'View rooms >>'
        $('#switchViewBtn .backIcon').hide();
        $('#switchViewBtn .forwardIcon').show();
        $('#switchViewBtn .content').html('View rooms');
        // display the map
        $('#mapContainer').show();
        // display the 'Take me there' button
        $('#toMapBtnContainer').show();
        // hide the 'book now' button
        $('#bookBtnContainer').hide();
        // show the number of rooms free
        $('#roomsFreeRow').show();
    } else {
        // show the favourites button
        $('#starContainer').show();
        // change search version button to 'View rooms >>'
        $('#switchViewBtn .backIcon').show();
        $('#switchViewBtn .forwardIcon').hide();
        $('#switchViewBtn .content').html('Back to buildings');
        // display the map
        $('#mapContainer').hide();
        // display the 'Take me there' button
        $('#toMapBtnContainer').hide();
        // show the 'book now' button
        $('#bookBtnContainer').show();
        // hide the number of rooms free
        $('#roomsFreeRow').hide();
    }
}

// Geolocation functions{

// check for browser compatibility
function getLocation() {
    // save that we're no longer using custom coordinates
    sessionStorage['customCoordinates']=false;
	// check that the browser is compatible
	if (navigator.geolocation) {
		// get the user's current coordinates or throw an error if that's not possible
		navigator.geolocation.getCurrentPosition(savePosition, showError);
	} else {
		alert('You browser does not support geolocation.  Enter your location using the options menu');
        $('.arrow').addClass('disabled');
        getSuggestionsUsingOptions();
        // open options menu and select location fixer
        toggleOptionsMenu();
        $('#locationCorrectorText').focus();
	}
}

// save the current positions, then get suggestions from the server
function savePosition(position) {
	userLatitude = position.coords.latitude;
	userLongitude = position.coords.longitude;
    // for some reason, many uni computers think they're in the middle of Arthur's seat.  If we detect this, tell them their location is wrong.  
    if (userLatitude>55.948367 && userLatitude<55.948368 && userLongitude<-3.158850 && userLongitude>-3.158851){
        alert("Unable to get accurate location.  Enter your location manually in the options menu to refine your location.");
        // open the options menu
        if (!$('#optionsMenu').hasClass('opened')){
            toggleOptionsMenu();
        }
        $('#locationCorrectorText').focus();
    }
	getSuggestionsUsingOptions();
}

// if impossible to get user's current coordinates, display a relevant error message
function showError(error) {
	switch (error.code) {
        case error.PERMISSION_DENIED:
            alert("Geolocation denied.  Enter your location using the options menu")
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Location information is unavailable.  Refresh the page or enter your location manually in the options menu.  ");
            break;
        case error.TIMEOUT:
            alert("The request to get user location timed out.  Refresh the page or enter your location manually in the options menu.  ");
            break;
        case error.UNKNOWN_ERROR:
            alert("An unknown error occurred when attempting to find your location.  Refresh the page or enter your location manually in the options menu.  ");
            break;
	}
    $('.arrow').addClass('disabled');
    getSuggestionsUsingOptions();
    // open options menu and select location fixer
    toggleOptionsMenu();
    $('#locationCorrectorText').focus();
}

// Geolocation functions}

// Weak equality for arrays:
function arraysEqual(a, b) {
    if (a === b) return true;
    if (a == null || b == null) return false;
    if (a.length != b.length) return false;
    
    for (var i = 0; i < a.length; ++i) {
        if (a[i] !== b[i]) return false;
    }
    return true;
}