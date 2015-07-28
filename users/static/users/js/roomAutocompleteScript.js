
$(document).ready(function(){
    // isClicked will change value whenever the remove fav btn is pressed.
    var isClicked = false;
    $(".remove-btn").click(removeFavouriteBtn);

    // This will make sure that the arrow in each panel changes direction whenever the panel
    // either collapses or unfolds.
    $(".panel").on('show.bs.collapse', function(){
        console.log('hej');
        $(this).addClass('dropup');
    });

    $(".panel").on('hide.bs.collapse', function(){
        console.log('hej');
        $(this).removeClass('dropup');
    });

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
            $(".remove-btn").html("<i class='fa fa-star starred'></i>Remove");
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

    $('#infoFor-' + id).fadeOut('slow');
    isClicked = false;
}




//$(function() {
//    // get the data from the autocomplete API
//    $.get('/autocompleteAPI/', function(allLocations) {
//
//        // lab autocomplete dropdown code:
//        $('#autocompleteLab').autocomplete({
//            lookup: allLocations['labs'],
//            autoSelectFirst: true,
//            // when a place is chosen
//            onSelect: function(suggestion) {
//                // add it to favourites
//                $.post('/like/', {
//                        'pc_id': suggestion.data.id,
//                        'pcLikedByUser': false
//                    })
//                // don't bring it up in the autocomplete dropdown again
//                allLocations['labs'] = allLocations['labs'].filter(function(lab){return lab.data.id!=suggestion.data.id})
//                $(this).autocomplete().setOptions({lookup:allLocations['labs']});
//                // reset the autocomplete dropdown
//                $(this).autocomplete().clear()
//                $(this).val('')
//                // add the new favourite to the list
//                var newItem = $('<li class="list-group-item" id="lab-'+suggestion.data.id+'">'+suggestion.value+': '+suggestion.data.free+'/'+suggestion.data.seats+' computers free ('+Math.floor(suggestion.data.ratio*100)+'%) <span class="unliker unclicked">Unlike</span></li>');
//                newItem.insertBefore('#autocompleteLabLi');
//                $('.unliker.unclicked').click(toggleLikes);
//                $('#noLabFavourites').remove()
//            }
//        });
//
//        // room autocomplete dropdown code
//        $('#autocompleteRoom').autocomplete({
//            lookup: allLocations['rooms'],
//            autoSelectFirst: true,
//            // when a place is chosen
//            onSelect: function(suggestion) {
//                // add it to favourites
//                $.post('/like/', {
//                        'locationId': suggestion.data.id,
//                        'roomLikedByUser': false
//                    })
//                // don't bring it up in the autocomplete dropdown again
//                allLocations['rooms'] = allLocations['rooms'].filter(function(room){return room.data.id!=suggestion.data.id})
//                $(this).autocomplete().setOptions({lookup:allLocations['rooms']});
//                // reset the autocomplete dropdown
//                $(this).autocomplete().clear()
//                $(this).val('')
//                // add the new favourite to the list:
//                // create all the icons:
//                facilities = ''
//                if (suggestion.data.pc){
//                    facilities += '<span class="custom-glyphicon glyphicon-computer" aria-hidden="true"></span> '
//                }
//                if (suggestion.data.printer){
//                    facilities += '<span class="custom-glyphicon glyphicon-printer" aria-hidden="true"></span> '
//                }
//                if (suggestion.data.projector){
//                    facilities += '<span class="custom-glyphicon glyphicon-projector" aria-hidden="true"></span> '
//                }
//                if (suggestion.data.blackboard){
//                    facilities += '<span class="custom-glyphicon glyphicon-blackboard-custom" aria-hidden="true"></span> '
//                }
//                if (suggestion.data.whiteboard){
//                    facilities += '<span class="custom-glyphicon glyphicon-whiteboard" aria-hidden="true"></span> '
//                }
//                if (facilities == ''){
//                    facilities = "<div id='blackboardTick' class='tickOrCross cross'></div>"
//                }
//                // create the other details
//                var newItem = $('<li class="list-group-item" id="room-'+suggestion.data.id+'">'+suggestion.data.room_name+', '+suggestion.data.building_name+': '+facilities+' <span class="unliker unclicked">Unlike</span></li>');
//                // insert the new favourite into the dom
//                newItem.insertBefore('#autocompleteRoomLi');
//                $('.unliker.unclicked').click(toggleLikes);
//                $('#noRoomFavourites').remove()
//            }
//        });
//    });
//
//});
