$(document).ready(function(){
    $('.unliker.unclicked').click(toggleLikes);
})
function toggleLikes(){
    $('.cancelRemoval').click();
    $(this).removeClass('unclicked');
    $(this).addClass('clicked');
    $(this).html('Are you sure? ')
    $('<span class="favRemover confirmRemoval">Yes</span> <span class="favRemover cancelRemoval">No</span>').insertAfter($(this));
    $(this).unbind('click');
    that=$(this)
    $('.confirmRemoval').click(function(){
        var li=$(this).parent()
        var thisId=li.attr('id')
        var idToUnlike = thisId.slice(thisId.indexOf('-')+1);
        var type=thisId.slice(0,thisId.indexOf('-'));
        // capitalized type, used in Ids
        var capsType=type.substr(0, 1).toUpperCase() + type.substr( 1 );
        if (type=='lab'){
            jsonToUnlike={'pc_id': idToUnlike, 'pcLikedByUser': true}
        }else{
            jsonToUnlike={'locationId': idToUnlike, 'roomLikedByUser': true}
        }
        $.post('/like/', jsonToUnlike)
        li.remove();
        if ($('#'+type+'List').children().length == 1){
            $('<li class="list-group-item" id="no'+capsType+'Favourites">No favourites yet!</li>').insertBefore('#autocomplete'+capsType+'Li');;
        }
    });
    $('.cancelRemoval').click(function(){
        that.click(toggleLikes);
        that.removeClass('clicked');
        that.addClass('unclicked');
        that.html('Unlike');
        $('.confirmRemoval').remove();
        $('.cancelRemoval').remove();
    });
}

$(function() {
    // get the data from the autocomplete API
    $.get('/autocompleteAPI/', function(allLocations) {

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
                    })
                // don't bring it up in the autocomplete dropdown again
                allLocations['labs'] = allLocations['labs'].filter(function(lab){return lab.data.id!=suggestion.data.id})
                $(this).autocomplete().setOptions({lookup:allLocations['labs']});
                // reset the autocomplete dropdown
                $(this).autocomplete().clear()
                $(this).val('')
                // add the new favourite to the list
                var newItem = $('<li class="list-group-item" id="lab-'+suggestion.data.id+'">'+suggestion.value+': '+suggestion.data.free+'/'+suggestion.data.seats+' computers free ('+Math.floor(suggestion.data.ratio*100)+'%) <span class="unliker unclicked">Unlike</span></li>');
                newItem.insertBefore('#autocompleteLabLi');
                $('.unliker.unclicked').click(toggleLikes);
                $('#noLabFavourites').remove()
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
                    })
                // don't bring it up in the autocomplete dropdown again
                allLocations['rooms'] = allLocations['rooms'].filter(function(room){return room.data.id!=suggestion.data.id})
                $(this).autocomplete().setOptions({lookup:allLocations['rooms']});
                // reset the autocomplete dropdown
                $(this).autocomplete().clear()
                $(this).val('')
                // add the new favourite to the list:
                // create all the icons:
                facilities = ''
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
                $('.unliker.unclicked').click(toggleLikes);
                $('#noRoomFavourites').remove()
            }
        });
    });

});
