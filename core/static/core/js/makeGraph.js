// Makes a pie chart using AmCharts' libraries
// Input: id (string): the id of the div which will contain the pie chart
//        free (number): the number of free computers (the size of the green slice of the pie)
//        inUse (number): the number of computers in use (the size of the red slice of the pie)
// Output: none
function makepie(id, free, inUse) {

    AmCharts.makeChart(id, {
        "type": "pie",
        "balloonText": "", // disable pop up balloons
        "labelsEnabled": false, // disable labels
        "panEventsEnabled": false, // disable touch screen scrolling
        "fontSize": 0, // disable AmCharts advert
        "pullOutDuration": 0, // disable pulling out slices
        "pullOutRadius": 0, // disable pulling out slices
        "startDuration": 0, // disable starting animation
        "innerRadius": 13, // radius of the 'hole' in the doughnut
        "minRadius": 25, // min radius of the pie chart if resized (currently impossible)
        "radius": 25, // the initial radius of the pie chart
        // REMEMBER TO CHANGE COLOURS HERE IF CHANGES ARE MADE TO VARIABLES.LESS !
        "colors": ["#2EA83D", '#D9433B'], // colors are: availableGreen and unavailableRed.
        "marginBottom": 0, // chart margins
        "marginTop": 0,    // chart margins
        "outlineAlpha": 1, // outline opacity
        "outlineThickness": 1, // outline thickness
        "titleField": "Type", // name of the field in the dataProvider array
        "valueField": "Number", // name of the field in the dataProvider array
        "dataProvider": [
            {
                "Type": "Free",
                "Number": free
            },
            {
                "Type": "In-Use",
                "Number": inUse
            }
        ]
    });
}