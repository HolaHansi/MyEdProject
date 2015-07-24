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
        "colors": ["#00aa00",'#aa0000'], //brand-primary
        "marginBottom": 0, //chart margins
        "marginTop": 0,    //chart margins
        "outlineAlpha": 1, //outline opacity
        "outlineThickness": 1, //outline thickness
        "titleField": "Type", //name of the field in the dataProvider array
        "valueField": "Number", //name of the field in the dataProvider array
        "dataProvider": [
            {
                "Type": "Free",
                "Number": free
            },
            {
                "Type": "In-Use",
                "Number": inuse
            }
        ]
    });
}