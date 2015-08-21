$(document).ready(function(){
    // style the favourites tab as the current tab
    $('#mainHamburgerMenuOptions .historyTab').addClass('currentTab');

    // This will make sure that the arrow in each panel changes direction whenever the panel
    // either collapses or unfolds.
    $(".panel").on('show.bs.collapse', function(){
        $(this).addClass('dropup');
    });

    $(".panel").on('hide.bs.collapse', function(){
        $(this).removeClass('dropup');
    });
    
    $('#clearHistory').click(function(){

        $.post('/history/', {
                'clearAll': true
        })
        .done(function(){
                $('.panel.panel-default').fadeOut(function() {
                    $(this).remove();
                    $('#historyCleared').removeAttr('style');
                    $('#clearHistory').remove();
                });
            }
        )
    });

});