$(document).ready(function(){
    // load auto-complete
    autoCompleteAPI();
    
    // isClicked will change value whenever the remove fav btn is cancelled
    isClicked = false;
    
    // style the favourites tab as the current tab
    $('#mainHamburgerMenuOptions .favouritesTab').addClass('currentTab');
    
    // make sure calendar renders when modal shows.
    $('#myModal').on('shown.bs.modal', function () {
        $("#calendar").fullCalendar('render');
    });

    // when the modal closed - kill the calendar.
    $('#closeModal').click(function(){
       $('#calendar').fullCalendar('destroy');
    });
    
    // add functionality to all the panels
    addGeneralFunctionalityToPanel($('.panel'));
    addFunctionalityToRoomPanel($('#rooms .panel'));
});


// add triggers to the remove button and the caret within the inputted panel
// input: panelDiv (object): the panel which we're applying functionality to
function addGeneralFunctionalityToPanel(panelDiv){
    // 'Remove button' functionality: 
    $(".remove-btn", panelDiv).click(removeFavouriteBtn);
    // if x is pressed, then set is clicked to true, so to escape this clause.
    $('.cancelRemove', panelDiv).click(cancelRemoveBtn);
    // if the check symbol is pressed, then obtain the id from the parent div, and
    // call the remove from favourites function.
    $('.confirmRemove', panelDiv).click(confirmRemoveBtn);
    
    // This will make sure that the arrow in each panel changes direction whenever the panel
    // either collapses or unfolds.
    panelDiv.on('show.bs.collapse', function(){
        $(this).addClass('dropup');
    });
    panelDiv.on('hide.bs.collapse', function(){
        $(this).removeClass('dropup');
    });
}


// the function called whenever a remove favourite button is selected
// it'll prompt the user to confirm the removal
// note that since the yes and no options are children of the button, any time either of those are clicked,
// this function will also be called
function removeFavouriteBtn(){
    // the user is using one of these mobile devices; use comfirm prompt instead of small buttons
    // when user tries to delete a room from favourites.
    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {

        if (confirm("Do you wish to remove this space from your favourites?")) {
            // this clause is taken, if the user confirmed to above prompt.
            var thisId = $(this).attr('id');
            removeFromFavourites(thisId);
        }
    }

    // the user is on a desktop computer: use the check and x symbol
    else {
        // if the user isn't cancelling the removal
        if (isClicked == false) {
            // show the yes/no buttons
            $(this).addClass('expanded');
        }
        // if the user is indeed cancelling the removal, return to the normal button
        if (isClicked == true) {
            $(this).removeClass('expanded');
            $(this).blur();
            isClicked = false;
        }
        
    }
}


// the function called whenever a confirm removal button is selected
// gets the id of the location to be removed and passes it to the removeFromFavourites function
function confirmRemoveBtn(){
    var btn = $(this).parent();
    var thisId = btn.attr('id');
    removeFromFavourites(thisId);
}


// the function called whenever a cancel removal button is selected
// since this button is a child of the main 'remove from favourites' button, 
// the main logic is carried out on the parent's click function to prevent
// it from cancelling and immediately expanding again
function cancelRemoveBtn(){
    isClicked = true;    
}


// removes the given pc or room from the users favourites
function removeFromFavourites(id) {
    var idToUnlike = id.slice(id.indexOf('-')+1);
    var type = id.slice(0, id.indexOf('-'));
    // if the type is 'lab', then JSON is formatted for a computer lab
    if (type=='lab') {
      jsonToUnlike = {'pc_id': idToUnlike, 'pcLikedByUser': true}
    // if the type is 'room', then JSON is formatted for a tutorial room
    } else {
        jsonToUnlike={'locationId': idToUnlike, 'roomLikedByUser': true}
    }
    // unlike the room
    $.post(rootURL + 'like/', jsonToUnlike);
    // remove this panel from the page
    $('#infoFor-' + id).fadeOut(function() { $(this).remove(); });
    isClicked = false;
    // update the autoComplete function
    autoCompleteAPI();
}


// this is the function that gets the data, and configures the settings for the autoCompleter
function autoCompleteAPI() {
    // get the data from the autocomplete API
    $.get(rootURL + '/autocompleteAPI/', function(allLocations) {
        // autocomplete code for PC-LABS:
        $('#autocompleteLab').autocomplete({
            lookup: allLocations['labs'],
            autoSelectFirst: true,
            maxHeight: '150',
            // when a place is chosen
            onSelect: function(suggestion) {
                // add it to favourites
                $.post(rootURL + 'like/', {
                        'pc_id': suggestion.data.id,
                        'pcLikedByUser': false
                    });
                // don't bring it up in the autocomplete dropdown again
                allLocations['labs'] = allLocations['labs'].filter(function(lab){return lab.data.id!=suggestion.data.id});
                $(this).autocomplete().setOptions({lookup:allLocations['labs']});
                // reset the autocomplete dropdown
                $(this).autocomplete().clear();
                $(this).val('');
                
                // create the html for this favourite server side
                $.post(rootURL + 'favourites/panel/', {'pc_id':suggestion.data.id})
                .done(function(panel){
                    // append it to the list of favourites
                    newPanel = $(panel).insertBefore("#autocompleteLabLi");
                    // add functionality to the panel
                    addGeneralFunctionalityToPanel(newPanel);
                });
            }
        });

        // room autocomplete dropdown code
        $('#autocompleteRoom').autocomplete({
            lookup: allLocations['rooms'],
            autoSelectFirst: true,
            maxHeight: '150',
            // when a place is chosen
            onSelect: function(suggestion) {
                // add it to favourites
                $.post(rootURL + 'like/', {
                        'locationId': suggestion.data.locationId,
                        'roomLikedByUser': false
                    });
                // don't bring it up in the autocomplete dropdown again
                allLocations['rooms'] = allLocations['rooms'].filter(function(room){return room.data.locationId!=suggestion.data.locationId});
                $(this).autocomplete().setOptions({lookup:allLocations['rooms']});
                // reset the autocomplete dropdown
                $(this).autocomplete().clear();
                $(this).val('');
                
                // create the html for this favourite
                $.post(rootURL + 'favourites/panel/', {'locationId':suggestion.data.locationId})
                .done(function(panel){
                    // append it to the list of favourites
                    newPanel = $(panel).insertBefore("#autocompleteRoomLi");
                    // add functionality to the panel
                    addGeneralFunctionalityToPanel(newPanel);
                    addFunctionalityToRoomPanel(newPanel);
                });
            }
        });
    });

}
