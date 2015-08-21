$(document).ready(function(){
    // load auto-complete
    autoCompleteAPI();
    
    // isClicked will change value whenever the remove fav btn is cancelled
    isClicked = false;
    $(".remove-btn").click(removeFavouriteBtn);
    // if x is pressed, then set is clicked to true, so to escape this clause.
    $('.cancelRemove').click(cancelRemoveBtn);

    // if the check symbol is pressed, then obtain the id from the parent div, and
    // call the remove from favourites function.
    $('.confirmRemove').click(confirmRemoveBtn);
    
    // This will make sure that the arrow in each panel changes direction whenever the panel
    // either collapses or unfolds.
    $(".panel").on('show.bs.collapse', function(){
        $(this).addClass('dropup');
    });

    $(".panel").on('hide.bs.collapse', function(){
        $(this).removeClass('dropup');
    });

    // style the favourites tab as the current tab
    $('#mainHamburgerMenuOptions .favouritesTab').addClass('currentTab');
    
    // book this room when the 'Book Now' button is selected
    $('.bookNow').click(function(){
        id = $(this).parents('.panel-default').prop('id');
        id = id.slice(id.indexOf('room-')+5);
        bookRoom(id);
    })
});

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
    $.post('/like/', jsonToUnlike);
    // remove this panel from the page
    $('#infoFor-' + id).fadeOut(function() { $(this).remove(); });
    isClicked = false;
    // update the autoComplete function
    autoCompleteAPI();
}

// this is the function that gets the data, and configures the settings for the autoCompleter
function autoCompleteAPI() {
    // get the data from the autocomplete API
    $.get('/autocompleteAPI/', function(allLocations) {
        // autocomplete code for PC-LABS:
        $('#autocompleteLab').autocomplete({
            lookup: allLocations['labs'],
            autoSelectFirst: true,
            maxHeight: '150',
            // when a place is chosen
            onSelect: function(suggestion) {
                // add it to favourites
                $.post('/like/', {
                        'pc_id': suggestion.data.id,
                        'pcLikedByUser': false
                    });
                // don't bring it up in the autocomplete dropdown again
                allLocations['labs'] = allLocations['labs'].filter(function(lab){return lab.data.id!=suggestion.data.id});
                $(this).autocomplete().setOptions({lookup:allLocations['labs']});
                // reset the autocomplete dropdown
                $(this).autocomplete().clear();
                $(this).val('');
                
                // create the html for this favourite
                $.post('panel/', {'pc_id':suggestion.data.id})
                .done(function(panel){
                    // append it to the list of favourites
                    newPanel = $(panel).insertBefore("#autocompleteLabLi");
                    // add functionality to the remove button
                    $(".remove-btn", newPanel).click(removeFavouriteBtn);
                    $(".confirmRemove", newPanel).click(confirmRemoveBtn);
                    $(".cancelRemove", newPanel).click(cancelRemoveBtn);
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
                $.post('/like/', {
                        'locationId': suggestion.data.locationId,
                        'roomLikedByUser': false
                    });
                // don't bring it up in the autocomplete dropdown again
                allLocations['rooms'] = allLocations['rooms'].filter(function(room){return room.data.locationId!=suggestion.data.locationId});
                $(this).autocomplete().setOptions({lookup:allLocations['rooms']});
                // reset the autocomplete dropdown
                $(this).autocomplete().clear();
                $(this).val('');
                // add the new favourite to the list:
                // create all the icons:

                // ========== add the new favourite to list of favourites using its appropriate template ========== //

                // get one of three categories: availableNow, notAvailable or localAvailable

                var availability = suggestion.data.availability;

                console.log(availability);

                var panelRoom = $(".panel.panel-default.room.template");

                // clone the template and make is visible by removing the style attribute.
                var clone = panelRoom.clone(true);
                clone.removeAttr('style');

                // remove the clone's template class
                clone.removeClass('template');


                if (availability == 'availableNow') {
                    console.log('its avail!!!!');

                    // determine where to insert the new favourite
                    var placeToInsert = '#insertRoomAvailableNow';
                    // theLink html - this goes into the panelHeading
                    var linkHtml = '<span class="badge check"><i class="fa fa-check avail"></i></span>' + suggestion.value + '<span class="caret"></span>';
                    var availForIconHtml = '<i class="fa fa-check-circle"></i>';
                    var availForDescriptionHtml = 'Available for less than';
                    var availForValueHtml = suggestion.data.availableFor;


                    console.log('panelRoom coming up');
                    console.log(panelRoom);
                }
                else if (availability == 'notAvailable') {
                    var placeToInsert = '#insertRoomNotAvailable';

                    var linkHtml = '<span class="badge times"><i class="fa fa-times"></i></span>' + suggestion.value + '<span class="caret"></span>';


                    var availForIconHtml = '<i class="fa fa-hourglass"></i>';
                    var availForDescriptionHtml = 'Will be available';
                    var availForValueHtml = suggestion.data.unavailableFor;

                    // disable the bookNow button.
                    console.log('not avail booknow');
                    console.log($('.booknow'));


                    clone.find('.booknow').addClass('disabled');


                }

                else {
                    var placeToInsert = '#insertRoomLocal';
                    var linkHtml = '<span class="badge minus"><i class="fa fa-minus avail"></i></span>' + suggestion.value + '<span class="caret"></span>';

                    var availForIconHtml = '<i class="fa fa-exclamation-triangle"></i>';
                    var availForDescriptionHtml = 'Locally Allocated';
                    var availForValueHtml = 'n/a';


                    // disable the bookNow button.
                    clone.find('.booknow').addClass('disabled');


                }

                linkHtml += '<div class="roomName ' + suggestion.data.locationId + '" id="' + suggestion.data.room_name + '"></div>';

                // initialize id variables
                var infoForID = 'infoFor-room-' + suggestion.data.locationId;
                var roomID = 'room-'+ suggestion.data.locationId;
                var collapseID = '#collapse-' + suggestion.data.locationId;
                var collapseIDNoHashtag = 'collapse-' + suggestion.data.locationId;


                // give panel the id for infoForID.
                clone.attr('id', infoForID);

                // get pointers to all the element that must be modified in the clone:
                var panelHeading = clone.find(".panel-heading");
                var theLink = clone.find('.theLink');
                var panelCollapse = clone.find('.panel-collapse.collapse');


                var capacity = clone.find('.capacityNumber');


                console.log('this is the clone coming up');
                console.log(clone);



                // opening hour paragraphs
                var openTimeP = panelCollapse.find(".openTimeP");
                var closingTimeP = panelCollapse.find(".closingTimeP");

                // availFor
                var availForIcon = panelCollapse.find(".availForIcon");
                var availForDescription = panelCollapse.find(".availForDescription");
                var availForValue = panelCollapse.find(".availForValue");

                //suitabilities
                var suitabilities = panelCollapse.find(".suitabilitiesRoom");

                // map and remove btn
                var mapBtn = panelCollapse.find(".mapBtn");
                var rmvBtn = panelCollapse.find(".remove-btn");
                var calBtn = panelCollapse.find(".calBtn");
                var bookNow = panelCollapse.find("booknow");

                // change date-target for panelHeading
                panelHeading.attr('data-target', collapseID);


                // change attributes for theLink
                theLink.attr("data-target", collapseID);
                theLink.attr("href", collapseID);
                theLink.attr("aria-controls", collapseIDNoHashtag);


                // change the html in theLink - the html value depends on whether place is closed or not.
                theLink.html(linkHtml);


                // change id of panelCollapse to match id favourite - slice expression is for getting rid of hashtag
                panelCollapse.attr('id', collapseIDNoHashtag);


                // get the opening hours
                if (suggestion.data.openHour == 'n/a') {
                    var openHourHtml = 'n/a';
                    var closingHourHtml = 'n/a';
                }
                else {
                    var openHourHtml = suggestion.data.openHour.slice(0, 5);
                    var closingHourHtml = suggestion.data.closingHour.slice(0,5);
                }

                // write the opening hours to the paragraphs in the clone.
                openTimeP.html(openHourHtml);
                closingTimeP.html(closingHourHtml);

                // update capacity
                capacity.html(suggestion.data.capacity);

                // update availFor
                availForIcon.html(availForIconHtml);
                availForDescription.html(availForDescriptionHtml);
                availForValue.html(availForValueHtml);


                facilities = '';
                if (suggestion.data.pc){
                    facilities += '<span class="custom-glyphicon glyphicon-computer" aria-hidden="true"></span> '
                }
                if (suggestion.data.printer){
                    facilities += '<span class="custom-glyphicon glyphicon-printer" aria-hidden="true"></span> '
                }
                if (suggestion.data.projector){
                    facilities += '<span class="custom-glyphicon glyphicon-projector" aria-hidden="true"></span> '
                }
                if (suggestion.data.blackboard){
                    facilities += '<span class="custom-glyphicon glyphicon-blackboard-custom" aria-hidden="true"></span> '
                }
                if (suggestion.data.whiteboard){
                    facilities += '<span class="custom-glyphicon glyphicon-whiteboard" aria-hidden="true"></span> '
                }


                suitabilities.html(facilities);

                // update the roomName div (this is where calendar gets the room name

                var roomName = clone.find('.roomName');



                //clone.find('.roomName').attr('id', suggestion.data.room_name);

                console.log('roomName thing???');
                console.log(roomName);
                console.log('end of roomName');

                // update remove btn id
                rmvBtn.attr('id', roomID);

                // update calBtn
                calBtn.attr('id', suggestion.data.locationId);

                // insert the new favourite into the dom
                clone.insertBefore(placeToInsert);

                // relocate the insertAfter div.
                $(placeToInsert).insertAfter(clone);
            }
        });
    });

}