$(document).ready(function () {
    
    $('.fa-star').click(function(){
        $(this).toggleClass('unstarred')
        $(this).toggleClass('starred')
    })
    
    //For testing only:
    $('#currentMap').attr('src', 'https://maps.googleapis.com/maps/api/staticmap?size=' + (window.innerWidth - 40) + 'x300&key=AIzaSyBcrXTgUVxfXVLj3rh5gIUWyYRpveHMmEs&markers=size:medium%7Clabel:A%7C55.9460736605763,-3.20059955120087&markers=size:medium%7Clabel:B%7C55.9427113171065,-3.18914651870728')
    $('#currentMap').css({
        'width': window.innerWidth - 40 + 'px',
        'height': '300px'
    })
})
