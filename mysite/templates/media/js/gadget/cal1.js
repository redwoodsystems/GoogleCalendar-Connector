// 
// The following array contains the list of locations that will be reported on.
// 
var occupiedColor = '#CC5E5A';  //red
var unoccupiedColor = '#5A9A08';   //green
var occupiedNotReservedColor = '#F7F705';   //yellow
var notOccupiedButReservedColor = '#F77905';   //orange
var idleColor = '#C5D8D9';

var reloadEvery = 10*1000; var idleTimeout = 1*60*1000; var colorFadeTime = 1500;   // ms
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
    
    //For testing only
    //weAreGoForUpdates = 1;
    //updateLocationData();
});



function buildLocationBoxes() {
    
    $('.meetNow').hide();
    $('.timeToCancel').hide();

    $('.room').click(function() {   // slide down the percent occupied on click
        $(this).children('.meetNow').slideToggle(150);
        $(this).children('.timeToCancel').slideToggle(150);

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
    	console.log("calling api");
    	var url="http://ec2-184-169-137-91.us-west-1.compute.amazonaws.com:8000/reaper/api/rmstatus";
    	
    	$.getJSON(url+"?callback=?",null,
    			function(data){
    				console.log("api returned");
    				processLocationData(data);
    			}
    	);

    }

}

function openMeetNow(location){
	console.log("in openMeetNow ...");
	//Needs the following line to be added to the gadget xml
	//<Require feature="google.calendar-0.5"/>	
	  var eventData = {
			    title: 'Meeting',
			    details: 'Meeting',
			    location: ''+location.room.name,
			    startTime: {year: 2012, month: 06, date: 22, hour: 14, minute:30, second:0},
			    endTime: {year: 2012, month: 06, date: 22, hour: 15, minute:30, second:0},
	
			    // Note that attendees MUST be sent in contact format.
			    attendees: [
			      {email: 'vphalak@redwoodsys.com'},
			      {email: ''+location.room.g_calendar_id}
			    ]
			  };
	  console.log("eventData="+eventData.location);
	 //google.calendar.composeEvent(eventData);
		
}

function registerMeetNowHandler(location){
	$('#' + location.room.id).children('.meetNow').children('a').click(function(e){
		console.log("meetnow clicked "+e);
		openMeetNow(location);
		e.preventDefault();        				
	});        			
}


function processLocationData(apiModel) {

    if (weAreGoForUpdates) {    	
    	console.log("apiModel="+apiModel);
    	for (loc in apiModel){
    		console.log("loc="+loc);
    		var location = apiModel[loc];
    		console.log("location="+location);
    		console.log("room id="+location.room.id);
    		console.log("room name="+location.room.name);
    		console.log("motion_enabled="+location.room.motion_enabled);
    		
    		if (location.room.motion_enabled){
        		console.log("occupied="+location.occupied);
        		console.log("reserved="+location.reserved);
        		
        		if ((!location.occupied && !location.reserved)){
        			//green
        			//paint meet now
        			$('#' +location.room.id ).animate({ backgroundColor: unoccupiedColor}, colorFadeTime);
        			$('#' + location.room.id ).children('.meetNow').empty().append('<a href="#">Meet Now </a>');
        			registerMeetNowHandler(location);        			
        		}

        		if (location.occupied && !location.reserved){
        			//yellow
        			//paint meet now
        			$('#' +location.room.id ).animate({ backgroundColor: occupiedNotReservedColor}, colorFadeTime);
        			$('#' + location.room.id ).children('.meetNow').empty().append('<a class=".meetNowLink" href="#">Meet Now </a>');
        			registerMeetNowHandler(location);
        		}
        		
        		if (!location.occupied && location.reserved){
        			//orange - show time to cancellation
        			$('#' +location.room.id ).animate({ backgroundColor: notOccupiedButReservedColor}, colorFadeTime);
        			if (location.time_to_reap){
        				$('#' + location.room.id ).children('.timeToCancel').empty().append('<p>Auto cancel in ' + location.time_to_reap + ' mins.</p>');
        				$('#' + location.room.id ).children('.meetNow').empty();
        			}
        			
        		}
        		
        		if (location.occupied && location.reserved){
        			//red
        			$('#' +location.room.id ).animate({ backgroundColor: occupiedColor}, colorFadeTime);
        			$('#' + location.room.id ).children('.meetNow').empty();
        		}        		
    		}
    	}
    	
    	
    }

}
