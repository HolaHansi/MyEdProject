var roomLikedByUser = false; // whether current suggestion is liked by user
var searchingForBuildings = true; // whether we're currently searching for buildings (true) or tutorial rooms (false)
var currentBuildingId = ''; // the id of the building we're currently searching in, or '' if we're searching for a building
var buildingIndexToReturnTo = 0; // the index of the building we're searching within


// Initialisation
$(document).ready(function () {
    
    // get the list of all the rooms the user likes
    getFavourites('rooms')
    
    // if the user has changed their settings this session, use the new settings
    if (sessionStorage['roomOptions']){
        var options = JSON.parse(sessionStorage['roomOptions']);
        $('#nearbyCheckbox').attr('checked',options.nearby);
        $('#bookableCheckbox').attr('checked',options.bookable);
        $('#availabilityInput').val(options.availableForHours);
        $('#pcCheckbox').toggleClass('checked',options.pc);
        $('#printerCheckbox').toggleClass('checked',options.printer);
        $('#projectorCheckbox').toggleClass('checked',options.projector);
        $('#whiteboardCheckbox').toggleClass('checked',options.whiteboard);
        $('#blackboardCheckbox').toggleClass('checked',options.blackboard);
        $('.campusCheckbox').each(function(){
            $(this).toggleClass('checked', (options.campuses.indexOf($(this).attr('id'))==-1) )
        })
    // otherwise, use and save the standard settings
    } else {
        // save the current options state
        var oldOptions = {
            nearby: $('#nearbyCheckbox').is(':checked'), 
            bookable: $('bookableCheckbox').is(':checked'), 
            availableForHours: $('#availabilityInput').val(),
            pc: $('#pcCheckbox').is(':checked'), 
            printer: $('#printerCheckbox').is(':checked'), 
            projector: $('#projectorCheckbox').is(':checked'), 
            whiteboard: $('#whiteboardCheckbox').is(':checked'), 
            blackboard: $('#blackboardCheckbox').is(':checked'), 
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
    
    // initialize the alert if it's not been initialized yet
    if (!sessionStorage['locallyAllocatedRoomWarningShown']){ 
        sessionStorage['locallyAllocatedRoomWarningShown'] = false;
    }
    
    // style the rooms tab as the current tab
    $('#mainHamburgerMenuOptions .roomsTab').addClass('currentTab');
    
    $('#switchViewBtn').click(function(){
        // toggle search mode
        searchingForBuildings = !searchingForBuildings;
        // if we're now back to searching for buildings, clear the current building
        if (searchingForBuildings){
            currentBuildingId = '';
        // if we're now searching within a building, save the building we're searching in
        } else {
            currentBuildingId = currentChoice.abbreviation;
            buildingIndexToReturnTo = currentChoice.index;
        }
        // get new suggestions from the server
        getSuggestionsUsingOptions();
    });
    
    // when the user books a room, save that room to the history database
    // bookRoom function is in core/booking.js
    $('#bookBtn').click(function(){
        bookRoom(currentChoice.locationId)
    });
    
    // when the user clicks the 'add to favourites' star, like or unlike the room as appropriate
	$('#suggestion .fa-star').click(function () {
		var locationId = currentChoice.locationId;
        // send the like request to the server
		$.post(rootURL + '/like/', {
				'locationId': locationId,
				'roomLikedByUser': (''+roomLikedByUser)
			})
			.fail(function () {
                alert('Failed to favourite location');
                // if the request failed, undo the local favouriting
                $('#suggestion .fa-star').toggleClass('unstarred');
                $('#suggestion .fa-star').toggleClass('starred');
                // toggle the room from the local list of favourite rooms
                if (roomLikedByUser){
                    // remove locationId from the list
                    userFavourites.splice(userFavourites.indexOf(locationId),1);
                } else {
                    // add locationId to the list
                    userFavourites.push(locationId);
                }
                roomLikedByUser=!roomLikedByUser;
			});
        // toggle star colour
        $('#suggestion .fa-star').toggleClass('unstarred');
        $('#suggestion .fa-star').toggleClass('starred');
        // toggle the room from the local list of favourite rooms
        if (roomLikedByUser){
            // remove locationId from the list
            userFavourites.splice(userFavourites.indexOf(locationId),1);
        } else {
            // add locationId to the list
            userFavourites.push(locationId);
        }
        roomLikedByUser=!roomLikedByUser;
	});
    
    // intialize options buttons to act as checkboxes
    $('.campusCheckbox, .facilitiesCheckbox').click(function(){
        $(this).toggleClass('checked');
        $('input', this).prop('checked', !$('input', this).prop('checked'))
    });
    // when the 'other' checkbox is clicked, toggle all hidden campuses too
    $('#otherCheckbox').click(function(){
        $('.campusCheckbox').each(function(){
            if($(this).css('display')=='none'){
                $(this).toggleClass('checked');
            }
        });
    });
    
    // alert the user the first time they ask to include locally allocated rooms in their search
    $('.bootstrap-switch-id-bookableCheckbox').on('switchChange.bootstrapSwitch',function(event, checkboxNowSelected){
        // if this is the first time they've selected the checkbox
        if (sessionStorage['locallyAllocatedRoomWarningShown']=="false" && !checkboxNowSelected){
            // prompt for a response
            if (confirm('This will include rooms not accessible to all students.  Continue?')){
                // if they said yes, don't show them the alert again
                sessionStorage['locallyAllocatedRoomWarningShown'] = true;
            } else {
                // if they said no, go back to not showing rooms
                $('.bootstrap-switch-id-bookableCheckbox .bootstrap-switch-handle-off').trigger('click');
                return;
            }
        } 
    })
});


// open or close the options menu
function toggleOptionsMenu(){
    $('#optionsMenu').toggleClass('opened');
    // apply the JS styling to reposition the options menu
    resizeElements();
    // if the options menu has just opened:
    if ($('#optionsMenu').hasClass('opened')){
        // disable the suggester interface
        $('.arrow').addClass('disabled');
        $('#switchViewBtn').addClass('disabled');
        $('#bookBtn').addClass('disabled');
        $('#toMapBtn').addClass('disabled');
        $('#mainContainer').css('opacity',0.3);
    } else {
        // reenable the suggester interface
        // note that arrows are reenabled seperately due to their also being disabled if on the first or last suggestion
        $('#mainContainer').css('opacity',1);
        $('#switchViewBtn').removeClass('disabled');
        $('#bookBtn').removeClass('disabled');
        $('#toMapBtn').removeClass('disabled');
        // ensure the 'available for' option has a sensible value
        // ie it's an integer between 0 and 24
        if (!( (parseInt($('#availabilityInput').val()))>=0 && (parseInt($('#availabilityInput').val()))<=24 )){
            // if they entered a value that's too large, cap it at 24
            if (parseInt($('#availabilityInput').val())>=24 ){
                $('#availabilityInput').val(24);
            // if they entered a value that's too small or invalid in some other way (not an integer), set it to 0
            } else {
                $('#availabilityInput').val(0);
            }
        }
        // ensure the number is indeed an int not a float
        // needed to prevent weirdness with eg 1.3e10
        $('#availabilityInput').val(parseInt($('#availabilityInput').val()));
        // check if the options have changed
        var newOptions = {
            nearby: $('#nearbyCheckbox').is(':checked'), 
            bookable: $('#bookableCheckbox').is(':checked'), 
            availableForHours: $('#availabilityInput').val(),
            pc: $('#pcCheckbox').hasClass('checked'), 
            printer: $('#printerCheckbox').hasClass('checked'), 
            projector: $('#projectorCheckbox').hasClass('checked'), 
            whiteboard: $('#whiteboardCheckbox').hasClass('checked'), 
            blackboard: $('#blackboardCheckbox').hasClass('checked'), 
            campuses:getUnselectedCampuses()
        };
        var oldOptions = JSON.parse(sessionStorage['roomOptions']);
        var optionsChanged = oldOptions.bookable!=newOptions.bookable || oldOptions.nearby!=newOptions.nearby || oldOptions.availableForHours!=newOptions.availableForHours || oldOptions.pc!=newOptions.pc || oldOptions.printer!=newOptions.printer || oldOptions.projector!=newOptions.projector || oldOptions.blackboard!=newOptions.blackboard || oldOptions.whiteboard!=newOptions.whiteboard ||  (! arraysEqual(oldOptions.campuses,newOptions.campuses));
        // if they have, or the user specifically asked for a refresh, refresh the suggestions
        if (optionsChanged || $(this).prop('id')=='searchWithNewOptionsBtn'){
            buildingIndexToReturnTo=0;
            searchingForBuildings=true;
            currentBuildingId='';
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
            
            // if there are no rooms that fit the criteria, keep the options menu open
            if (suggestions.length==0){
                // timeout makes the options menu do a wee bump for pretty-ness sake
                setTimeout(function(){
                    toggleOptionsMenu();
                    alert('No rooms available fit that criteria.  Try again.  ');
                }, 30)
            }
        }
        // deselect all options
        $('#optionsMenu *').blur();
    }
}

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
    // get the suggestions
    getSuggestions($('#bookableCheckbox').is(':checked'), $('#availabilityInput').val(), $('#pcCheckbox').hasClass('checked'), $('#printerCheckbox').hasClass('checked'), $('#whiteboardCheckbox').hasClass('checked'), $('#blackboardCheckbox').hasClass('checked'), $('#projectorCheckbox').hasClass('checked'), currentBuildingId, $('#nearbyCheckbox').is(':checked'), ids); 
}

/* 
   Get the list of suggestions from the server
   Parameters:
   bookable (boolean): whether the user wants only bookable rooms
   pc (boolean): whether the user wants only rooms with a pc
   printer (boolean): whether the user wants only rooms with a printer
   whiteboard (boolean): whether the user wants only rooms with a whiteboard
   blackboard(boolean): whether the user wants only rooms with a blackboard
   projector (boolean): whether the user wants only rooms with a projector
   building (string): the abbreviation of the building the user is searching within if they've chosen one, else ''
   nearby (boolean): whether the user is sorting by distance
   campuses (array of strings): the campuses that the user doesn't want, a subset of [‘Central’,‘Lauriston’,"King's Buildings", 'Holyrood', 'Other']
*/
function getSuggestions(bookable, availableFor, pc, printer, whiteboard, blackboard, projector, building, nearby, campuses) {
	// send the get request
	$.get(rootURL + 'rooms/filter', {
			'bookable': bookable,
            'availableFor': availableFor,
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
                
                // if returning to the building suggester, go back to the building you came from
                if (searchingForBuildings){
                    currentChoice=suggestions[buildingIndexToReturnTo]
                    
                // otherwise, load the first suggestion
                } else{
                    currentChoice = suggestions[0];
                }
				loadChoice();
                if (suggestions.length==1){
                    // don't remind the user they can swipe if they can't
                    clearTimeout(idleReminder);
                }
			} else {
                toggleOptionsMenu();
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
    // change view to the appropriate version
    switchView();
    
    // populate the html
    if (searchingForBuildings){
        // display the details for the building
        $('#buildingName').html(currentChoice.building_name);
        $('#roomsFreeNumber').html(currentChoice.rooms);
        // update the map to the new coordinates
        updateMap();
        // update the 'Take me there' Google Maps deeplink
        $('#toMapBtn').attr('href','https://www.google.com/maps/preview?saddr='+userLatitude+','+userLongitude+'&daddr='+currentChoice.latitude+','+currentChoice.longitude+'&dirflg=w');
    } else{
        // display the details for the room
        $('#roomName').html(currentChoice.room_name);
        $('#capacityNumber').html(currentChoice.capacity);
        // display the availability details
        if (currentChoice.availableFor=='unknown'){
            $('#availabilityNumber').addClass('unavailable');
            $('#availabilityNumber').html('(No information available)');
        } else {
            $('#availabilityNumber').removeClass('unavailable');
            $('#availabilityNumber').html(currentChoice.availableFor);
        }
        // display the opening hours
        // if it's a Sunday, display Sunday's hours
        if (new Date().getDay==0){
            displayTime(currentChoice.sundayOpen,currentChoice.sundayClosed);
        // if it's a Saturday, display Saturday's hours
        } else if (new Date().getDay==6){
            displayTime(currentChoice.saturdayOpen,currentChoice.saturdayClosed);
        // if it's a weekday, display the weekday's hours
        } else {
            displayTime(currentChoice.weekdayOpen,currentChoice.weekdayClosed);
        }
        $('#openingHoursValue').html()
        // display the facilities
        if (currentChoice.pc){
            $('#facilities .glyphicon-computer').show();
        } else {
            $('#facilities .glyphicon-computer').hide();
        }
        if (currentChoice.printer){
            $('#facilities .glyphicon-printer').show();
        } else {
            $('#facilities .glyphicon-printer').hide();
        }
        if (currentChoice.projector){
            $('#facilities .glyphicon-projector').show();
        } else {
            $('#facilities .glyphicon-projector').hide();
        }
        if (currentChoice.whiteboard){
            $('#facilities .glyphicon-whiteboard').show();
        } else {
            $('#facilities .glyphicon-whiteboard').hide();
        }
        if (currentChoice.blackboard){
            $('#facilities .glyphicon-blackboard-custom').show();
        } else {
            $('#facilities .glyphicon-blackboard-custom').hide();
        }
        if (currentChoice.pc || currentChoice.printer || currentChoice.projector || currentChoice.whiteboard || currentChoice.blackboard){
            $('#facilities .noFacilities').hide();
        } else {
            $('#facilities .noFacilities').show();
        }
        // check if current choice is liked by user and toggle the star icon appropriately
        liked(currentChoice.locationId);
    }
    
	// if the user has reached the end of the list of suggestions, or if the options menu is currently open, disable the 'next' button
	if (currentChoice.index == suggestions.length - 1 || $('#optionsMenu').hasClass('opened') ) {
		$('.right-arrow').addClass('disabled');
	} else {
        $('.right-arrow').removeClass('disabled');
    }
	// if the user is at the start of the list of suggestions, or if the options menu is currently open, disable the 'previous' button
	if (currentChoice.index == 0 || $('#optionsMenu').hasClass('opened') ) {
		$('.left-arrow').addClass('disabled');
	} else {
		$('.left-arrow').removeClass('disabled');
    }
}

// Switch view from searching for rooms to searching for buildings
function switchView(){
    // if switching to buildings
    if (searchingForBuildings){
        // hide the room name and favourites button
        $('#roomRow').hide();
        // hide the favourites button
        $('#starContainer').hide();
        //make the building name a title again
        $('#buildingName').removeClass('subtitle');
        // show the number of rooms free
        $('#roomsFreeRow').show();
        // hide the room details
        $('#capacityRow').hide();
        $('#availabilityRow').hide();
        $('#facilitiesRow').hide();
        $('#openingHoursRow').hide();
        // display the map
        $('#mapContainer').removeClass('hidden-xs');
        // change search version button to 'View rooms >>'
        $('#switchViewBtn .backIcon').hide();
        $('#switchViewBtn .forwardIcon').show();
        $('#switchViewBtn .content').html('View rooms');
        // display the 'Take me there' button
        $('#toMapBtnContainer').show();
        // hide the 'book now' button
        $('#bookBtnContainer').hide();
    } else {
        // show the room name
        $('#roomRow').show();
        // show the favourites button
        $('#starContainer').show();
        //make the building name a subtitle
        $('#buildingName').addClass('subtitle');
        // hide the number of rooms free
        $('#roomsFreeRow').hide();
        // show the room details
        $('#capacityRow').show();
        $('#availabilityRow').show();
        $('#facilitiesRow').show();
        $('#openingHoursRow').show();
        // hide the map on mobiles
        $('#mapContainer').addClass('hidden-xs');
        // change search version button to '<< Back to buildings'
        $('#switchViewBtn .backIcon').show();
        $('#switchViewBtn .forwardIcon').hide();
        $('#switchViewBtn .content').html('Back to buildings');
        // hide the 'Take me there' button
        $('#toMapBtnContainer').hide();
        // show the 'book now' button
        $('#bookBtnContainer').show();
    }
}

// displays the times inputted in a nicely formatted style
// if no times are known, displays a message saying so to the user
// inputs: start (string) - the opening time of the building, in the format HH:MM:SS
//         end   (string) - the closing time of the building, in the format HH:MM:SS
// output: none;
function displayTime(start,end){
    if (start===null){
        $('#openingHoursValue').addClass('unavailable');
        $('#openingHoursValue').html( '(No information available)' );
    } else{
        $('#openingHoursValue').removeClass('unavailable');
        $('#openingHoursValue').html( start.slice(0,5) + ' - ' + end.slice(0,5) );
    }
}
