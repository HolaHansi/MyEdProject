/**
 * Created by hanschristiangregersen on 07/08/15.
 */

$(document).ready(function(){
    // style the favourites tab as the current tab
    $('#mainHamburgerMenuOptions .historyTab').addClass('currentTab');


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