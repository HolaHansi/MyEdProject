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
            }
        });
        // TODO: display the new favourite when chosen rather than waiting for refresh
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
            }
        });
    });

});
