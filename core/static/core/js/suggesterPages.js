// JS shared by both the labs and rooms suggester pages

var suggestions = []; // all suggestions provided by the server
var currentChoice = {}; // the suggestion currently on display
var userFavourites = []; // all the rooms currently liked by the user

var userLatitude = 55.943655; // current latitude of user
var userLongitude = -3.188775; // current longitude of user
// Note this is dummy data, pointed in the middle of George Square, which is simply used asa a default.  
// This will be overwritten if the user allows location finding or manually enters their location

var idleReminder; // the timer variable which reminds the user they can swipe if they don't swipe within the first 5 seconds
var idleTime=0; // the length of time the user has gone without swiping


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


$(document).ready(function(){
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

	// when the user clicks the next button, load the next suggestion
	$('.right-arrow').click(function () {
        loadNextSuggestion();
	});
    
	// when the user clicks the previous button, load the previous suggestion
	$('.left-arrow').click(function () {
        loadPreviousSuggestion();
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
    
    // also correct their location if they press enter while focus is on the location corrector textbox
    $('#locationCorrectorText').on('keydown', function (e) {
        if (e.which == 13) {
            $('#locationCorrectorGo').trigger('click');
            // unfocus from the textbox
            $(this).blur();
         }
    });
    
    // display or hide the options menu when the options header is clicked
    $('#optionsTitle, .triangle, #searchWithNewOptionsBtn').click(toggleOptionsMenu);
    
    // take down the options menu if the user clicks off it
    $('#mainContainer').click(function(){
        if ($('#optionsMenu').hasClass('opened')){
            toggleOptionsMenu();
        }
    })
    
})


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


/*
	Check if the current suggestion is liked by the user and color the star appropriately
	Parameters: id (string) - the id of the suggestion to be checked (pc_id for labs, locationId for rooms)
*/
function liked(id) {
    if (userFavourites.indexOf(id)>=0){
        $('#suggestion .fa-star').removeClass('unstarred');
        $('#suggestion .fa-star').addClass('starred');
        labLikedByUser=true;
    } else {
        $('#suggestion .fa-star').addClass('unstarred');
        $('#suggestion .fa-star').removeClass('starred');
        labLikedByUser=false;
    }
};


// returns the id of all campuses the user doesn't want included
function getUnselectedCampuses(){
    ids = [];
	$('.campusCheckbox:not(.checked)').each(function () {
        ids.push(this.id);
	});
	return ids;
}


/*
    Get the list of this user's favourites from the server
    Parameters: type: 'rooms' or 'labs' depending on which favourites you're getting
*/
function getFavourites(type){
    $.get(rootURL + '/getLiked', {
        'type':type
    })
    .done(function (data) {
        userFavourites = data;
    })
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
