$(function() {
    $.get('/autocompleteAPI/', function(allLocations) {
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
                $(this).autocomplete().clear()
                $(this).val('')
                var newItem = $('<li class="list-group-item">'+suggestion.value+': '+suggestion.data.free+'/'+suggestion.data.seats+' computers free ('+Math.floor(suggestion.data.ratio*100)+'%)</li>');
                newItem.insertBefore('#autocompleteLabLi');// <li class="list-group-item">{{ fav.name }}: {{fav.free}}/{{fav.seats}} computers free ({{fav.free|ratioToPercent:fav.seats}}%)</li>
                $('#noLabFavourites').remove()
            }
        });
        
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
                $(this).autocomplete().clear()
                $(this).val('')
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
                var newItem = $('<li class="list-group-item">'+suggestion.data.room_name+', '+suggestion.data.building_name+': '+facilities+'</li>');
                newItem.insertBefore('#autocompleteRoomLi');
                $('#noRoomFavourites').remove()
            }
        });
    });

});
