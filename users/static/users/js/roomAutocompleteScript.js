$(document).ready(function(){

    isClicked = false;
    $(".remove-btn").click(removeFavouriteBtn);

});



function removeFavouriteBtn(){

    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {

        if (confirm("Do you wish to remove this space from your favourites?")) {

         var thisId = $(this).attr('id');
         removeFromFavourites(thisId);

        };

    }
    else {
        if (isClicked == false) {
            // button is not clicked yet
            $(this).html("<i class='fa fa-star unstarred'></i>Remove &nbsp;");
            $("<a href='#' class='fa fa-check confirmRemove'> &nbsp; </a>").appendTo(this);
            $("<a href='#' class='fa fa-times cancelRemove'> &nbsp; </a>").appendTo(this);

            $('.cancelRemove').click(function () {
                isClicked = true;
            });

            $('.confirmRemove').click(function () {
                //var btn = $(this).parent().parent().parent().parent().parent();

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
    var idToUnlike = id.slice(id.indexOf('-')+1);
    console.log(idToUnlike);
    var type = id.slice(0, id.indexOf('-'));
    console.log(type);
    if (type=='lab') {
      jsonToUnlike = {'pc_id': idToUnlike, 'pcLikedByUser': true};
    }
    else {
        jsonToUnlike={'locationId': idToUnlike, 'roomLikedByUser': true}
    }
    console.log(jsonToUnlike);

    $.post('/like/', jsonToUnlike);

    $('#infoFor-' + id).remove();
    isClicked = false;
}


//function toggleLikes(){
//    $('.remove-btn.unclicked').fadeIn('<i class="fa fa-check"></i>')
//    $(this).removeClass('unclicked');
//    $(this).addClass('clicked');
//    $(this).unbind('click');
//    that=$(this)
//    $('.confirmRemoval').click(function(){
//        var li=$(this).parent();
//        var thisId=li.attr('id');
//        var idToUnlike = thisId.slice(thisId.indexOf('-')+1);
//        var type=thisId.slice(0,thisId.indexOf('-'));
//        // capitalized type, used in Ids
//        var capsType=type.substr(0, 1).toUpperCase() + type.substr( 1 );
//        if (type=='lab'){
//            jsonToUnlike={'pc_id': idToUnlike, 'pcLikedByUser': true}
//        }else{
//            jsonToUnlike={'locationId': idToUnlike, 'roomLikedByUser': true}
//        }
//        $.post('/like/', jsonToUnlike)
//        li.remove();
//        if ($('#'+type+'List').children().length == 1){
//            $('<li class="list-group-item" id="no'+capsType+'Favourites">No favourites yet!</li>').insertBefore('#autocomplete'+capsType+'Li');;
//        }
//    });
//    $('.cancelRemoval').click(function(){
//        that.click(toggleLikes);
//        that.removeClass('clicked');
//        that.addClass('unclicked');
//        that.html('Unlike');
//        $('.confirmRemoval').remove();
//        $('.cancelRemoval').remove();
//    });
//}

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
