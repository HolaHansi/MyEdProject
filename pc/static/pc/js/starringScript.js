$(document).ready(function () {

    $('.fa-star').click(function () {
        $(this).toggleClass('unstarred')
        $(this).toggleClass('starred')
    })

    //to be moved:
    $('.arrow').css({
        'height': (window.innerHeight - 40) + 'px'
    })

    //For testing only:
    $('#currentMap').attr('src', 'https://maps.googleapis.com/maps/api/staticmap?size=' + (window.innerWidth - 60) + 'x300&key=AIzaSyBcrXTgUVxfXVLj3rh5gIUWyYRpveHMmEs&markers=size:medium%7Clabel:A%7C55.9460736605763,-3.20059955120087&markers=size:medium%7Clabel:B%7C55.9427113171065,-3.18914651870728')
    $('#currentMap').css({
        'height': '300px',
        'width': '2000px'
    })

    //make a pie chart
    makepie("computersFreeGraph", "130", "12");
})

function makepie(id, free, inuse) {

    AmCharts.makeChart(id, {
        "type": "pie",
        "balloonText": "", //disable pop up balloons
        "labelsEnabled": false, //disable labels
        "panEventsEnabled": false, //disable touch screen scrolling
        "fontSize": 0, //disable AmCharts advert
        "pullOutDuration": 0, //disable pulling out slices 
        "pullOutRadius":0, //disable pulling out slices
        "startDuration": 0, //disable starting animation
        "innerRadius": 13, //radius of the 'hole' in the doughnut
        "minRadius": 25, //min radius of the pie chart if resized (currently impossible)
        "radius": 25, //the initial radius of the pie chart
        "colors": ["#337AB7",'#bbccdd'], //brand-primary
        "marginBottom": 0, //chart margins
        "marginTop": 0,    //chart margins
        "outlineAlpha": 1, //outline opacity
        "outlineThickness": 1, //outline thickness
        "titleField": "Type", //name of the field in the dataProvider array
        "valueField": "Number", //name of the field in the dataProvider array
        "dataProvider": [
            {
                "Type": "In-Use",
                "Number": inuse
            },
            {
                "Type": "Free",
                "Number": free
            }
        ]
    });
}