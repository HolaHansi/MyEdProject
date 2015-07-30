
$(document).ready(function(){
    // isClicked will change value whenever the remove fav btn is pressed.
    isClicked = false;
    $(".remove-btn").click(removeFavouriteBtn);

    // This will make sure that the arrow in each panel changes direction whenever the panel
    // either collapses or unfolds.
    $(".panel").on('show.bs.collapse', function(){
        $(this).addClass('dropup');
    });

    $(".panel").on('hide.bs.collapse', function(){
        $(this).removeClass('dropup');
    });

    // load auto-complete
    autoCompleteAPI();
});


function removeFavouriteBtn(){

    // the user is using one of these mobile devices; use comfirm prompt instead of small buttons
    // when user tries to delete a room from favourites.
    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {

        if (confirm("Do you wish to remove this space from your favourites?")) {
            // this clause is taken, if the user confirmed to above prompt.
            var thisId = $(this).attr('id');
            removeFromFavourites(thisId);
        };
    }

    // the user is on a desktop computer: use the check and x symbol
    else {
        if (isClicked == false) {
            // button is not clicked yet

            // append x and check symbol to button.
            $(this).html("<i class='fa fa-star unstarred'></i>Remove &nbsp;");
            $("<a href='#' class='fa fa-check confirmRemove'> &nbsp; </a>").appendTo(this);
            $("<a href='#' class='fa fa-times cancelRemove'> &nbsp; </a>").appendTo(this);

            // if x is pressed, then set is clicked to true, so to escape this clause.
            $('.cancelRemove').click(function () {
                isClicked = true;
            });

            // if the check symbol is pressed, then obtain the id from the parent div, and
            // call the remove from favourites function.
            $('.confirmRemove').click(function () {
                var btn = $(this).parent();
                console.log(btn);
                var thisId = btn.attr('id');
                console.log(thisId);
                removeFromFavourites(thisId);
            });
        // end of coditional
        };

        if (isClicked == true) {
            // the x has been pressed, return to normal button again
            $(this).html("<i class='fa fa-star starred'></i>Remove");
            isClicked = false;
        };
    // end of else
    };
// end of function
};

function removeFromFavourites(id) {
    // removes the given pc or room from the users favourites.
    var idToUnlike = id.slice(id.indexOf('-')+1);
    var type = id.slice(0, id.indexOf('-'));
    // if the type is lab, then JSON is formatted for a PC.
    if (type=='lab') {
      jsonToUnlike = {'pc_id': idToUnlike, 'pcLikedByUser': true};
    }
    else {
        // the type is a tutorial room:
        jsonToUnlike={'locationId': idToUnlike, 'roomLikedByUser': true}
    }

    $.post('/like/', jsonToUnlike);

    $('#infoFor-' + id).fadeOut(function() { $(this).remove(); });
    isClicked = false;
    // update the autoComplete function.
    autoCompleteAPI();
}


function isOpenNow(suggestion) {
    var isOpen = true;
    var now = new Date();
    var currentHour = now.getHours();
    var currentMinute = now.getMinutes();

    var openTime = suggestion.data.openHour;
    var closingTime = suggestion.data.closingHour;

    // if there is no opening hours for the given suggestion,
    // then just return true, so it can be added to "green-badges"
    if (openTime == 'n/a') {
        return true;
    }

    var openHour = parseInt(openTime.slice(0, openTime.indexOf(':')));
    var openMinute = parseInt(openTime.slice(openTime.indexOf(':')+1,openTime.indexOf(':')+3));

    var closingHour = parseInt(closingTime.slice(0, closingTime.indexOf(':')));
    var closingMinute = parseInt(closingTime.slice(closingTime.indexOf(':')+1,closingTime.indexOf(':')+3));


    // the morning case (the place closes in the morning)
    if (closingHour <= 9) {
        // if close < ct < open, then closed
        // first check if greater than closed:
        if ((currentHour >= closingHour) || (currentHour == closingHour && currentMinute >= closingMinute)) {
            // we know now that close <= ct
            // now check if ct < open
            if ((currentHour < openHour) || (currentHour == openHour && currentMinute < openMinute)) {
                isOpen = false;
            };
        };
    }

    // evening case (the place closes in the evening/afternoon)
    else {
        // if ct < open or ct >= close, then closed
        if (((currentHour >= closingHour) || (currentHour == closingHour && currentMinute >= closingMinute))

            || ((currentHour < openHour) || (currentHour == openHour && currentMinute < openMinute))) {

            isOpen = false;
        };
    };

    return isOpen;

}

function autoCompleteAPI() {
    // get the data from the autocomplete API
    $.get('/autocompleteAPI/', function(allLocations) {
        allLocations;

        // lab autocomplete dropdown code:
        $('#autocompleteLab').autocomplete({
            lookup: allLocations['labs'],
            autoSelectFirst: true,
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
                // add the new favourite list of favourites

                // =========================================

                // check if place is open
                var isOpen = isOpenNow(suggestion);

                // if the place is open:
                if (isOpen) {
                  // determine where to insert the new favourite
                  var placeToInsert = '#insertAfterOpen';
                  // determine which template to use - the template is currently not visible: css(display:none;)
                  var panelPC = $(".panel.panel-default.pc.open.template");
                  // determine the content of theLink which displays the name and badge on the tab for the favourite
                  var linkHtml = '<span class="badge free">' + suggestion.data.free + '</span>' + suggestion.value + '<span class="caret"></span>';
                }
                // if the place is closed:
                else {
                    var placeToInsert = '#insertAfterClosed';
                    var panelPC = $(".panel.panel-default.pc.closed.template");
                    var linkHtml = '<span class="badge times"><i class="fa fa-times"></i></span>' + suggestion.value + '<span class="caret"></span>';
                };

                // clone the template and make is visible by removing the style attribute.
                var clone = panelPC.clone(true);
                clone.removeAttr('style');

                // remove the clone's template class
                clone.removeClass('template');

                // initialize id variables
                var infoForID = 'infoFor-lab-' + suggestion.data.id;
                var labID = 'lab-'+ suggestion.data.id;
                var collapseID = '#collapse-' + suggestion.data.id;
                var collapseIDNoHashtag = 'collapse-' + suggestion.data.id;

                // relevant attributes
                var freeVar = suggestion.data.free;
                var inUseVar = (suggestion.data.seats - suggestion.data.free);

                // give panel the id for infoForID.
                clone.attr('id', infoForID);

                // get pointers to all the element that must be modified in the clone:
                var panelHeading = clone.find(".panel-heading");
                var theLink = clone.find('.theLink');
                var panelCollapse = clone.find('.panel-collapse.collapse');

                // the badges for free and inuse
                var freeBadgeStat = panelCollapse.find("#freeBadgeText");
                var useBadgeStat = panelCollapse.find("#useBadgeText");

                // the div displaying the pie-chart
                var computerFreeGraph = panelCollapse.find('.computersFreeGraph');

                // opening hour paragraphs
                var openTimeP = panelCollapse.find(".openTimeP");
                var closingTimeP = panelCollapse.find(".closingTimeP");

                // map and remove btn
                var mapBtn = panelCollapse.find(".btn.btn-default.map-btn");
                var rmvBtn = panelCollapse.find(".btn.btn-default.remove-btn");


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


                // update inUse and free badge values
                freeBadgeStat.html('Free:  <span class="badge free">'+ freeVar + '</span>');
                useBadgeStat.html('Free:  <span class="badge inuse">'+ inUseVar + '</span>');

                // remove the script that normally makes the pie chart.
                panelCollapse.find('.makePieScript').remove();

                // change id of computerFreeGraph to match the favourite ID.
                computerFreeGraph.attr('id', suggestion.data.id);

                var stringId = suggestion.data.id.toString();



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


                // get the right longitude, latitude for the googleMaps link.
                mapBtn.attr('href', "http://maps.google.com/maps?q=" + suggestion.data.latitude + "," + suggestion.data.longitude);


                // give rmvBtn the correctID.
                rmvBtn.attr('id', labID);


                // insert the now populated clone at the appropriate spot.
                clone.insertAfter(placeToInsert);

                // make the pieChart for this favourite.
                makepie(stringId, suggestion.data.free, inUseVar);

                // relocate the insertAfter div.
                $(placeToInsert).insertAfter(clone);

            }
        });

        // room autocomplete dropdown code
        $('#autocompleteRoom').autocomplete({
            lookup: allLocations['rooms'],
            autoSelectFirst: true,
            // when a place is chosen
            onSelect: function(suggestion) {
                // add it to favourites
                $.post('/like/', {
                        'locationId': suggestion.data.id,
                        'roomLikedByUser': false
                    });
                // don't bring it up in the autocomplete dropdown again
                allLocations['rooms'] = allLocations['rooms'].filter(function(room){return room.data.id!=suggestion.data.id})
                $(this).autocomplete().setOptions({lookup:allLocations['rooms']});
                // reset the autocomplete dropdown
                $(this).autocomplete().clear();
                $(this).val('');
                // add the new favourite to the list:
                // create all the icons:
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
                if (facilities == ''){
                    facilities = "<div id='blackboardTick' class='tickOrCross cross'></div>"
                }
                // create the other details
                var newItem = $('<li class="list-group-item" id="room-'+suggestion.data.id+'">'+suggestion.data.room_name+', '+suggestion.data.building_name+': '+facilities+' <span class="unliker unclicked">Unlike</span></li>');
                // insert the new favourite into the dom
                newItem.insertBefore('#autocompleteRoomLi');
                $('#noRoomFavourites').remove()
            }
        });
    });

}
