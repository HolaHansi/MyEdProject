// This file uses the Google Maps Javascript API V3 to create and look after the map and the location corrector option, used in both /labs and /rooms
// Functions that can be called:
// makeMap(): Initializes the Google map.  External global variables used: none
// updateMap(): Updates the Google map to display the current choice. External global variables used: currentChoice, userLatitude, userLongitude

var map; // the Google Map object
var mapOptions; // the JSON of options for the map
var directionOptions; // the JSON of options for getting directions
var geocodingOptions; // the JSON of options for translating an address to its geolocation (geocoding)
var directionsService; // the Google directions service object, the bit that calculates the route
var directionsDisplay;  // the Google directions renderer object, the bit that displays the route
var geocoder; // the Google object for geocoding
var startMarker; // the Google object for the marker at the start of the route
var endMarker; // the Google object for the marker at the end of the route

var refreshTimer; // the maps timeout variable for limiting number of queries per second to avoid limits

$(document).ready(function(){
    
    // Create the map
    makeMap();
    
    // Set up the location fixer
    $('#locationCorrectorGo').click(function(){
        // get the input from the user
        var newLocation=$('#locationCorrectorText').val();
        if (newLocation===''){
            // if the user leaves it blank, use their default location
            getLocation();
            return '';
        }
        // if the user hasn't narrowed down their search to Edinburgh (or elsewhere, as estimated by their using a comma), do it for them
        if (newLocation.indexOf('Edinburgh')==-1 && newLocation.indexOf(',')==-1){
            newLocation+=', Edinburgh';
        }
        // update the geocoding options
        geocodingOptions.address = newLocation;
        // get the coordinates from Google
        geocoder.geocode(geocodingOptions,function(results, status){
            // if successful, 
            if (status==google.maps.GeocoderStatus.OK){
                
                // save the new coordinates
                var newCoordinates = results[0].geometry.location;
                userLatitude = newCoordinates.lat();
                userLongitude = newCoordinates.lng();
                
                // save this to the local session
                sessionStorage['customCoordinates']=true;
                sessionStorage['userLatitude']=userLatitude;
                sessionStorage['userLongitude']=userLongitude;
                
                // display the suggestions using the new coordinates
                getSuggestionsUsingOptions();
                toggleOptionsMenu();   
                
            // otherwise, display an appropriate error message
            }else if (status==google.maps.GeocoderStatus.ZERO_RESULTS || status==google.maps.GeocoderStatus.INVALID_REQUEST){
                alert("Location not recognised - try again.");
            }else{
                alert("Lookup failed: " + status);
            }
        });
    });
})

// Initialize Google settings, set fixed object properties and render the map:
// The JSON {lat:55.943655, lng:-3.188775} is dummy data and is overwritten as soon as the list of suggestions is received from the server
function makeMap(){
    // initialize Google objects
    directionsService = new google.maps.DirectionsService();
    directionsDisplay = new google.maps.DirectionsRenderer({suppressMarkers: true});
    geocoder = new google.maps.Geocoder();

    // initialise map options, hiding all controls other than a small zoom and pan
    mapOptions = {
        disableDefaultUI: true,
        panControl: true,
        panControlOptions: {
            position: google.maps.ControlPosition.TOP_LEFT
        },
        zoomControl: true,
        zoomControlOptions: {
            style: google.maps.ZoomControlStyle.SMALL,
            position: google.maps.ControlPosition.TOP_LEFT
        },
        mapTypeControl: false,
        scaleControl: false,
        streetViewControl: false,
        overviewMapControl: false,
        rotateControl: false,
        draggable: false,
        scrollwheel: false,
        // styles: [{ featureType: "poi", elementType: "labels", stylers: [{ visibility: "off" }]}], // disable Points of Interest (and therefore their popup menus)
        maxZoom: 17,
        backgroundColor: '#ffffff'
    };
    
    // initialise direction options
    directionOptions = {
        origin: {
            lat:55.943655,
            lng:-3.188775
        },
        destination: {
            lat:55.943655,
            lng:-3.188775
        },
        travelMode: google.maps.TravelMode.WALKING,
        provideRouteAlternatives: false,
        region: 'uk'
    }
    
    // initialise geocoding options
    geocodingOptions = {
        bounds: google.maps.LatLngBounds(google.maps.LatLng(55.913840,-3.243026),google.maps.LatLng(55.970666, -3.150412)),
        region: 'uk'
    };
    
    // create the map
    map = new google.maps.Map(document.getElementById("currentMap"), mapOptions);
    // bind the directions renderer to the map
    directionsDisplay.setMap(map);
    
    // initialize marker options
    var startMarkerOptions = {
        clickable: false,
        cursor: 'default',
        map: map,
        icon: new google.maps.MarkerImage(
            '/staticfiles/core/images/startIcon.png',
            new google.maps.Size( 22, 40 ),
            new google.maps.Point( 0, 0 ),
            new google.maps.Point( 11, 40 )
        )
    }
    var finishMarkerOptions = {
        clickable: false,
        cursor: 'default',
        map: map,
        icon: new google.maps.MarkerImage(
            '/staticfiles/core/images/finishIcon.png',
            new google.maps.Size( 22, 40 ),
            new google.maps.Point( 0, 0 ),
            new google.maps.Point( 11, 40 )
        )
    }
    startMarker = new google.maps.Marker(startMarkerOptions)
    endMarker = new google.maps.Marker(finishMarkerOptions)
}

// update the map with the new directions
function updateMap(){
    $('#busyAnimation').hide();
    // update direction options
    directionOptions.origin= {
          lat:userLatitude,
          lng:userLongitude
      }
    directionOptions.destination= {
            lat:currentChoice.latitude, 
            lng:currentChoice.longitude
      }
    // calculate and display the route
    directionsService.route(directionOptions, function(result, status) {
        // if the route was successfully calculated, display it
        if (status == google.maps.DirectionsStatus.OK) {
            // display route
            directionsDisplay.setDirections(result);
            // display markers
            var leg = result.routes[ 0 ].legs[ 0 ];
            startMarker.setPosition(leg.start_location)
            endMarker.setPosition(leg.end_location)
        // if the user is flicking through choices too quickly, wait before showing the map
        }else if (status == google.maps.DirectionsStatus.OVER_QUERY_LIMIT){
            $('#busyAnimation').show();
            clearTimeout(refreshTimer)
            refreshTimer = setTimeout(updateMap, 1000)
        } else {
            alert('Error: '+status);
        }
    });
}