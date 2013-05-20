// 
// The following array contains the list of locations that will be reported on.
// 
var targetLocations = [ 'Edison',
                        'Tesla',
                        'Westinghouse' ];

var utilizationWindow = 120;  // time window used to determine percent occupancy

var percentOccThreshold    = 10;    // percent
var lastMotionOccThreshold = 120;   // seconds; these two combined determine occupancy color
var occupiedColor = '#CC5E5A'; var unoccupiedColor = '#5A9A08'; var idleColor = '#C5D8D9';

var reloadEvery = 2*1000; var idleTimeout = 1*60*1000; var colorFadeTime = 1500;   // ms
var upToDateWarningTime = 5;   // minutes; engineTime - local now greater than this creates warning
var weAreGoForUpdates = 1;     // flag that the idle timer sets/unsets



$(function() {
    buildLocationBoxes();

    $('#missYou').hide();  $('#messages').hide();

    $(document).bind("idle.idleTimer", function(){
       if (weAreGoForUpdates == 1) {   // we were active and have just flipped to idle
         weAreGoForUpdates = 0;
            $('.room').css('background-color', idleColor);
            //$('.room').animate({ backgroundColor: idleColor}, colorFadeTime);
            $('#missYou').show();
            $('.menuArrow').hide();
            $('.lastMotionTarget').empty();
            $('.percentOccupiedTarget').empty();
        }
    });

    $(document).bind("active.idleTimer", function(){
        if (weAreGoForUpdates == 0) {   // we were idle and just flipped to active
            weAreGoForUpdates = 1;
            updateLocationData();
            
            $('#missYou').hide();
            $('.menuArrow').show();
            
        }
    });
    
    $.idleTimer(idleTimeout);   // start the idle timer

    $.ajaxSetup( {timeout: reloadEvery} );   // global timeout for api requests
    $.ajaxSetup( {async: false} );
    updateLocationData();                    // populate the location boxes
    $.ajaxSetup( {async: true} );

    setInterval( 'updateLocationData()', reloadEvery );  // lather rinse etc
});



function buildLocationBoxes() {
    
    var locationNames = [];
    for (var loc in targetLocations) { locationNames.push( targetLocations[loc] ); }
    locationNames.sort();    // alphabetize

    for (var loc in locationNames) {

        var boxID = locationNames[loc].split(/\s+|\'/).join(''); // the boxID is the location name with spaces removed

        var box  = "<div class='room' id='" + boxID + "'>";
            box += "<div class='menuArrow menuArrowLeft'></div>";
            box += "<h4 class='roomTitle'>" + locationNames[loc] + "</h4>";
            box += "<div class='lastMotionTarget'></div><div class='percentOccupiedTarget'><br /></div></div>";
        
        $('#main').append(box);
        //gadgets.window.adjustHeight();
    }
    
    $('.percentOccupiedTarget').hide();

    $('.room').click(function() {   // slide down the percent occupied on click
        $(this).children('.percentOccupiedTarget').slideToggle(150);

        var arrowTarget = $(this).children('.menuArrow');
        
        if ( arrowTarget.hasClass('menuArrowLeft') ) {
            arrowTarget.removeClass('menuArrowLeft').addClass('menuArrowDown');
        } else if ( arrowTarget.hasClass('menuArrowDown') ) {
            arrowTarget.removeClass('menuArrowDown').addClass('menuArrowLeft');
        }

        //setTimeout('gadgets.window.adjustHeight()', 160)
    });
}


function updateLocationData() {

    if (weAreGoForUpdates) {

        $.getJSON("https://admin:redwood@dir1-alpha/rApi?jsonpCallback=?",
            function(data) {
                processLocationData(data.response);
            }
        );

    }

}


function processLocationData(apiModel) {

    if (weAreGoForUpdates) {

        // Display a warning of the time stamp from the Redwood API is more than <upToDateWarningTime>
        // different than the time on this host
        var hostTime = new Date();
        var diff     = new Date(hostTime.getTime() - apiModel.currentTime*1000);
        if (diff.getMinutes() > upToDateWarningTime) {
            $('#messages').empty().append('Warning: not up to date').show();
        } else {
            $('#messages').hide();
        }

        for (var loc in targetLocations) {

            var boxID = targetLocations[loc].split(/\s+|\'/).join('');
                        
            for (var modelLocation in apiModel.location) {

                if (apiModel.location[modelLocation].name == targetLocations[loc]) {

                    var id = apiModel.location[modelLocation].id;
                    var timeSinceLastMotion = apiModel.currentTime - apiModel.location[modelLocation].sensorStats.motion.instant;
                    //var percentOccupied = apiModel.location[modelLocation].sensorStats.utilization.instant;

                    //if (apiModel.location[modelLocation].sensorStats.occupancy.instant) {
                    if (timeSinceLastMotion < 120) {
                        $('#' + boxID).animate({ backgroundColor: occupiedColor}, colorFadeTime);
                    } else {
                        $('#' + boxID).animate({ backgroundColor: unoccupiedColor}, colorFadeTime);
                    }

                    if (timeSinceLastMotion < 60) {
                        $('#' + boxID).children('.lastMotionTarget').empty().append('<p>last motion < 1 min ago.</p>');
                    } else if (timeSinceLastMotion < 60*60) {
                        var t    = new Date(timeSinceLastMotion*1000);
                        var mins = t.getMinutes();
                        $('#' + boxID).children('.lastMotionTarget').empty().append('<p>last motion ' + mins + ' min ago.</p>');
                    } else {
                        $('#' + boxID).children('.lastMotionTarget').empty().append('<p>last motion > 1 hour ago.</p>');
                    }
    
                    $('#' + boxID).children('.percentOccupiedTarget')
                                  .empty()
                                  .append('<br /><p>estimated ?% occupied.</p>');

                    break;

                }


            }


        }

    }

}
