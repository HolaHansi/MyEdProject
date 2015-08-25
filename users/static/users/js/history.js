$(document).ready(function(){
    // style the favourites tab as the current tab
    $('#mainHamburgerMenuOptions .historyTab').addClass('currentTab');

    $('#clearHistory').click(function(){

        $.post('/history/', {'clearAll': true})
        .done(function(){
            $('.panel.panel-default').fadeOut(function() {
                $(this).remove();
                $('#historyCleared').show();
                $('#clearHistory').remove();
            });
        })
    });
    
    // make sure calendar renders when modal shows.
    $('#myModal').on('shown.bs.modal', function () {
        $("#calendar").fullCalendar('render');
    });

    // when the modal closed - kill the calendar.
    $('#closeModal').click(function(){
       $('#calendar').fullCalendar('destroy');
    });
    
    // This will make sure that the arrow in each panel changes direction whenever the panel
    // either collapses or unfolds.
    $('.panel').on('show.bs.collapse', function(){
        $(this).addClass('dropup');
    });
    $('.panel').on('hide.bs.collapse', function(){
        $(this).removeClass('dropup');
    });
    
    // add functionality to all the elements within each of the room panels
    addFunctionalityToRoomPanel($('.panel'));
});
