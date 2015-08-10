/**
 * Created by hanschristiangregersen on 07/08/15.
 */



var locationId;


$(document).ready(function(){
    // style the favourites tab as the current tab

    $('.calBtn').click(function(){

        locationId = $(this).attr('id');

        console.log(locationId);

        $.get('/calendar/', {
                'locationId': locationId
        })
        .done(function(data){
            var activities = data;
                var daller = true;

                console.log('activities coming up');
                console.log(activities);
                console.log(daller);

            });
        });




    });


