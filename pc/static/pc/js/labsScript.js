var labLikedByUser = false; // whether current suggestion is liked by user


// Initialisation
$(document).ready(function () {
    
    // get the list of all the rooms the user likes
    getFavourites('labs')
    
    // if the user has changed their settings this session, use the new settings
    if (sessionStorage['labOptions']){
        var options = JSON.parse(sessionStorage['labOptions']);
        
        $('#nearbyCheckbox').attr('checked',options.nearby);
        $('#quietCheckbox').attr('checked',options.quiet);
        $('.campusCheckbox').each(function(){
            $(this).toggleClass('checked', (options.campuses.indexOf($(this).attr('id'))==-1) )
        })
    
    // otherwise, use and save the standard settings
    } else {
        // save the current options state
        var oldOptions = {
            nearby: $('#nearbyCheckbox').is(':checked'), 
            quiet: $('#quietCheckbox').is(':checked'), 
            campuses:getUnselectedCampuses()
        };
        sessionStorage['labOptions'] = JSON.stringify(oldOptions)
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
    
    // style the labs tab as the current tab
    $('#mainHamburgerMenuOptions .labsTab').addClass('currentTab');
    
    // when the user clicks the 'add to favourites' star, like or unlike the room as appropriate
	$('#suggestion .fa-star').click(function () {
		var pc_id = currentChoice.id;
        // send the like request to the server
		$.post(rootURL + '/like/', {
				'pc_id': pc_id,
				'pcLikedByUser': (''+labLikedByUser)
			})
			.fail(function () {
                alert('Failed to favourite location');
                // if the request failed, undo the local favouriting
                $('#suggestion .fa-star').toggleClass('unstarred');
                $('#suggestion .fa-star').toggleClass('starred');
                // toggle the lab from the local list of favourite labs
                if (labLikedByUser){
                    // remove pc_id from the list
                    userFavourites.splice(userFavourites.indexOf(pc_id),1);
                } else {
                    // add pc_id to the list
                    userFavourites.push(pc_id);
                }
                labLikedByUser=!labLikedByUser;
			});
        // toggle star colour
        $('#suggestion .fa-star').toggleClass('unstarred');
        $('#suggestion .fa-star').toggleClass('starred');
        // toggle the lab from the local list of favourite labs
        if (labLikedByUser){
            // remove pc_id from the list
            userFavourites.splice(userFavourites.indexOf(pc_id),1);
        } else {
            // add pc_id to the list
            userFavourites.push(pc_id);
        }
        labLikedByUser=!labLikedByUser;
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
        var oldOptions = JSON.parse(sessionStorage['labOptions']);
        var optionsChanged = oldOptions.nearby!=newOptions.nearby || oldOptions.quiet!=newOptions.quiet || (! arraysEqual(oldOptions.campuses,newOptions.campuses));
        // if they have, or the user specifically asked for a refresh, refresh the suggestions
        if (optionsChanged || $(this).prop('id')=='searchWithNewOptions'){
            getSuggestionsUsingOptions();
            sessionStorage['labOptions'] = JSON.stringify(newOptions)
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
    getSuggestions( $('#nearbyCheckbox').is(':checked'), $('#quietCheckbox').is(':checked'), ids); //TODO FIX
}

/* 
   Get the list of suggestions from the server
   Parameters:
   nearby (boolean): whether the user is sorting by distance
   empty (boolean): whether the user is sorting by emptiness ratio
   campuses (array of strings): the campuses that the user doesn't want, a subset of ['Central','Lauriston',"King's Buildings", 'Holyrood', 'Other']
*/
function getSuggestions(nearby, empty, campuses) {
	// send the get request
	$.get(rootURL + 'filter', {
			'nearby': nearby,
			'empty': empty,
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
	// populate the html
	$('#roomName').html(currentChoice.name);
	$('#computersFreeRow .badge.free').html(currentChoice.free);
    $('#computersFreeRow .badge.inuse').html(currentChoice.seats-currentChoice.free);
    makepie("computersFreeGraph", currentChoice.free, (currentChoice.seats-currentChoice.free));
    
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
	// check if current choice is liked by user and toggle the star icon appropriately
	liked(currentChoice.id);
    // update the map to the new coordinates
    updateMap();
    // update the 'Take me there' Google Maps deeplink
    $('#yesBtn').attr('href','https://www.google.com/maps/preview?saddr='+userLatitude+','+userLongitude+'&daddr='+currentChoice.latitude+','+currentChoice.longitude+'&dirflg=w');
}
