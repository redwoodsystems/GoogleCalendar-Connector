//
//The following array contains the list of locations that will be reported on.
//
var idleColor = '#C5D8D9';

var reloadEvery = 20*1000; var idleTimeout = 1*60*1000; var colorFadeTime = 1500;   // ms
var weAreGoForUpdates = 1;     // flag that the idle timer sets/unsets

var locations = {};
var roomStates = {};


String.prototype.ellipsize = 
    function(n){
        return this.substr(0,n-1)+(this.length>n?'&hellip;':'');
    };

$(function() {
 
	initialize();
	
 $('#missYou').hide();  $('#messages').hide();

 
 $(document).bind("idle.idleTimer", function(){
    if (weAreGoForUpdates == 1) {   // we were active and have just flipped to idle
      weAreGoForUpdates = 0;
         $('.well').css('background-color', idleColor);
         //$('.room').animate({ backgroundColor: idleColor}, colorFadeTime);
         $('#missYou').show();
     }
 });

 $(document).bind("active.idleTimer", function(){
     if (weAreGoForUpdates == 0) {   // we were idle and just flipped to active
         weAreGoForUpdates = 1;
         updateLocationData();
         
         $('#missYou').hide();
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


function initialize(){
	//Operations to be done on loading gadget
	registerShowDetailsHandler();
	registerMeetNowHandlerNew();
	registerRoomFilterHandler();
}


function applyUpDownState(roomEl) {
	
	var roomId = roomEl.attr("id");
	var colorState = roomStates[roomId]['color'];
	var booked = roomStates[roomId]['booked'];
	
	if (roomStates[roomId]["up_down"] == "up") {
		//collapse
		if (colorState=="green"){
			roomEl.find('div[detailType]').each(function(){
				$(this).hide();
			});
		}
		
		if (colorState=="black" && !booked ){
			roomEl.find('div[detailType]').each(function(){
				$(this).hide();
			});
		}
		
		if (colorState=="black" && booked ){
			roomEl.find('div[detailType]').each(function(){
				if ($(this).attr('detailType') !="cancelIn"){
					$(this).hide();
				} 
			});
		}

		if (colorState=="red"){
			roomEl.find('div[detailType]').each(function(){
				$(this).hide();
			});
			roomEl.find('hr').each(function(){
				$(this).hide();
			});
		}
		
	} else {
		//expand
		roomEl.find('div[detailType]').each(function(){
			$(this).show();
		});
		roomEl.find('hr').show();
	}
	
}


function registerShowDetailsHandler(){
	//Toggle display of room occupancy details on clicking icon

	$('#rooms').on('click', '[class*="cus-down-"]', function(){
		
		var wellEl = $(this).parents(".well");
		var roomId = wellEl.attr("id");
		
		var colorState = roomStates[roomId]['color'];
		var booked = roomStates[roomId]['booked'];
		
		//set the correct state
		roomStates[roomId]["up_down"] = ["up"];
		
		if ( $(this).hasClass("arr-down") ){
			$(this).removeClass("arr-down").addClass("arr-up");
		}
		
		if ( $(this).hasClass("cus-down-"+colorState) ){
			$(this).removeClass("cus-down-"+colorState).addClass("cus-right-"+colorState);
		}

		//Collapse logic here
		applyUpDownState(wellEl);
		

	});
	
	$('#rooms').on('click', '[class*="cus-right-"]', function(){
		
		var wellEl = $(this).parents(".well");
		var roomId = wellEl.attr("id");
		
		var colorState = roomStates[roomId]['color'];
		var booked = roomStates[roomId]['booked'];
		
		roomStates[roomId]["up_down"] = ["down"];
		
		if ( $(this).hasClass("arr-up") ){
			$(this).removeClass("arr-up").addClass("arr-down");			
		}
		
		if ( $(this).hasClass("cus-right-"+colorState) ){
			$(this).removeClass("cus-right-"+colorState).addClass("cus-down-"+colorState);			
		}
		
		applyUpDownState(wellEl);

	});

}


function registerMeetNowHandlerNew(){
	
	$('#rooms').on('click', '.meet-now > a', function(){
		var wellEl = $(this).parents(".well");
		var roomId = wellEl.attr("id");
		var colorState = wellEl.attr("color-state");
		
		alert('meet-now clicked on room_id='+roomId+" color-state="+colorState);
		openMeetNow(roomId);
		e.preventDefault();

	});
	
}

function registerRoomFilterHandler(){
	
	$("#filter-rooms").on("change","",function(){
		var sel = $("#filter-rooms option:selected").attr("id");

		if (sel == "all"){
			$(".well").parent().parent().show();
			$(".well").show();
		} else if (sel == "now"){
			$('.well-green').parent().parent().show();
			$('.well-green').show();
			
			$('.well-black[booked-state="unbooked"]').parent().parent().show();
			$('.well-black[booked-state="unbooked"]').show();
			
			$('.well-black[booked-state="booked"]').parent().parent().hide();
			$('.well-black[booked-state="booked"]').hide();
			
			$(".well-red").parent().parent().hide();
			$(".well-red").hide();
		} else {
			//
		}
	});
	
	
}

function updateLocationData() {

 if (weAreGoForUpdates) {
 	console.log("calling api");
 	//var url="http://ec2-184-169-137-91.us-west-1.compute.amazonaws.com/reaper/reaper/api/rmstatus";
 	var url="http://localhost:8000/reaper/api/rmstatus";
 	
 	$.getJSON(url+"?callback=?",null,
 			function(data){
 				console.log("api returned");
 				processLocationData(data);
 			}
 	);

 }

}

function compose() {
	  var eventData = {
	    title: 'Christmas',
	    details: 'Merry Christmas to you!',
	    location: 'My house',
	    allDay: true,

	    startTime: {year: 2009, month: 12, date: 25},

	    // Within the data model, the end time is EXCLUSIVE. So the endTime MUST
	    // be on the day after the start time.
	    endTime: {year: 2009, month: 12, date: 26},

	    // Note that attendees MUST be sent in contact format.
	    attendees: [
	      {email: 'davem.gadgets@gmail.com'}
	    ],

	// For more RRULE examples, please see http://www.ietf.org/rfc/rfc2445.txt
	    rrule: 'RRULE:FREQ=YEARLY'
	  };
	  google.calendar.composeEvent(eventData);
}

function openMeetNow(roomId){
	//console.log("in openMeetNow ...");
	//Needs the following line to be added to the gadget xml
	//<Require feature="google.calendar-0.5"/>	
	console.log("in openMeetNow "+roomId);
	
	location = locations[roomId];
	if (!location){
		return;
	}
	
	  var d = new Date();
	  var minu = d.getMinutes();
          var hr = d.getHours();
	  if (minu >= 30){
		  minu = 0;
                  hr = hr+1;
	  } else {
		  minu = 30;
          }
	  
	  
	  var eventData = {
			    title: 'Meeting',
			    details: 'Meeting',
			    location: ''+location.room.name,
			    startTime: {year: d.getFullYear(), month: d.getMonth()+1, date: d.getDate(), hour:hr , minute:minu, second:0},
			    endTime: {year: d.getFullYear(), month: d.getMonth()+1, date: d.getDate(), hour: hr+1, minute:minu, second:0},
	
			    // Note that attendees MUST be sent in contact format.
			    attendees: [
			      {email: ''+location.room.g_calendar_id}
			    ]
			  };
	 console.log("eventData="+eventData.location);
	 google.calendar.composeEvent(eventData);
		
}


function processLocationData(apiModel) {

 if (weAreGoForUpdates) {    	
 	//console.log("apiModel="+apiModel);
	//clear existing values
	locations = {};
	
	var allExistingIds = [];
	var allDisplayedIds = [];
	
	allExistingIds = $("#rooms").find(".well").map(function(){
		return $(this).attr("id");
	});
		
 	for (loc in apiModel){
 		var location = apiModel[loc];
 		console.log("loc="+loc+" room name="+location.room.name);

 		//store location data in map
 		locations[location.room.id] = location;
 		
 		if (location.room.motion_enabled) {
 	 		if ($.inArray(""+location.room.id,allExistingIds) >-1){
 	 			//replace existing room
 	 		} else {
 	 			//found new room not already on page
 	 			//create scaffolding
 	 			var st = '<div class="row-fluid">'
 	 			     +'<div class="span12">'
 	 			     +'<div id="'+location.room.id+'" class="well" color-state="" booked-state="">'
 	 			     +'</div></div></div>';
 	 			$("#rooms").append(st);
 	 		}
 	 		fillRoom(location);
 		} else {
 			//remove room and scaffolding from page if it exists
 			if ($.inArray(""+location.room.id,allExistingIds) >-1){
 				//$("#"+location.room.id).remove();
 				$("#"+location.room.id).parent().parent().remove();
 			}
 		}
 		
 	}
 	
 	//apply filter again because may colors have changed
 	$("#filter-rooms").change();
 	
	//apply tooltips
	applyToolTips();
 
 }

}


function appendMeetNow(container) {
	
	if (container.find(".meet-now-container").length == 0) {
		var st = '<div class="meet-now-container room-data-row">'
			 +'<span class="meet-now"><a href="#">Meet Now</a></span>'
			 +'</div>';
		
		container.append(st);
	}
	return container;
}

function appendOccupancy(container, pct){

	container.find(".occ-container").remove();
	if (container.find(".occ-container").length == 0) {
		var st = '<div class="occ-container room-data-row" detailType="occPct">'
			 +'<span class="room-data-left">Occupancy</span> <span class="room-data-right">'+pct+"% Full"+'</span>'
			 +'</div>'
		
		container.append(st);
	}
	return container;
}

function appendAvailabilityUntil(container, tm){
	
	container.find(".avail-container").remove();
	if (container.find(".avail-container").length == 0) {
		var st = '<div class="avail-container room-data-row" detailType="availUntil">'
			 +'<span class="room-data-left">Available until</span> <span class="room-data-right">'+tm+'</span>'
			 +'</div>'
		
		container.append(st);
	}
	return container;
}

function appendCancellationIn(container, tm){
	container.find(".cancel-container").remove();
	if (container.find(".cancel-container").length == 0) {
		var st = '<div class="cancel-container room-data-row" detailType="cancelIn">'
			 +'<span class="room-data-left">Cancellation in</span> <span class="room-data-right">'+tm+'</span>'
			 +'</div>'
		
		container.append(st);
	}
	return container;
}

function appendBookedUntil(container, tm){
	container.find(".booked-container").remove();
	if (container.find(".booked-container").length == 0) {
		var st = '<div class="booked-container room-data-row" detailType="bookedUntil">'
			 +'<span class="room-data-left">Booked until</span> <span class="room-data-right">'+tm+'</span>'
			 +'</div>'
		
		container.append(st);
	}
	return container;
}

function appendRoomHeader(container, roomName){
	
	if (container.find(".room-hdr").length == 0) {
		var st = '<div class="room-hdr room-data-row">'
			+'<span class="room-data-left room-title">'+roomName.ellipsize(10)+'</span>' 
			+'<span class="room-data-right">'
			+'<i class="ic1"></i>&nbsp;'
			+'<i class="ic2"></i>&nbsp;'
			+'<i class="ic3"></i>'
			+'</span>'
			+'</div>'
			+'<hr/>';
		
		container.append(st);
	}
	return container;
}

function clearWellClass(roomEl){
	roomEl.removeClass (function (index, css) {
	    return (css.match (/well-\S+/g) || []).join(' ');
	});
	return roomEl
}

function clearIconClass(iconEl){
	iconEl.removeClass(function(index,css){
		return (css.match (/cus-\S+/g) || []).join(' ');
	});
	return iconEl;
}

function clearAllIconStates(roomEl){
	roomEl.find('i').each(function(){
		$(this).removeClass(function(index,css){
			return (css.match (/cus-\S+/g) || []).join(' ');
		});
	})
}


function loadRoomStates(location){
	
	if (!(location.room.id in roomStates)) {
		roomStates[location.room.id]= {};
		//only modify up_down state if this is a new room or loading for the first time
		roomStates[location.room.id] = {'up_down':'down'};
		console.log('state of '+location.room.id+': '+roomStates[location.room.id]);
	}
	
	if (!location.occupied && !location.reserved){
		roomStates[location.room.id]['color'] = "green";
		roomStates[location.room.id]['paintMeetNow'] = true;
		roomStates[location.room.id]['paintOcc'] = true;
		roomStates[location.room.id]['paintAvailUntil'] = true;
		roomStates[location.room.id]['paintCancelIn'] = false;
		roomStates[location.room.id]['paintBookedUntil'] = false;
		roomStates[location.room.id]['booked'] = false;
		roomStates[location.room.id]['occupied'] = false;
	}
	
	if (location.occupied && !location.reserved){
		roomStates[location.room.id]['color'] = "black";
		roomStates[location.room.id]['paintMeetNow'] = true;
		roomStates[location.room.id]['paintOcc'] = true;
		roomStates[location.room.id]['paintAvailUntil'] = true;
		roomStates[location.room.id]['paintCancelIn'] = false;
		roomStates[location.room.id]['paintBookedUntil'] = false;
		roomStates[location.room.id]['booked'] = false;
		roomStates[location.room.id]['occupied'] = true;

	}
	
	if (!location.occupied && location.reserved){
		roomStates[location.room.id]['color'] = "black";
		roomStates[location.room.id]['paintMeetNow'] = false;
		roomStates[location.room.id]['paintOcc'] = true;
		roomStates[location.room.id]['paintAvailUntil'] = false;
		roomStates[location.room.id]['paintCancelIn'] = true;
		roomStates[location.room.id]['paintBookedUntil'] = true;
		roomStates[location.room.id]['booked'] = true;
		roomStates[location.room.id]['occupied'] = false;

	}
	
	if (location.occupied && location.reserved){
		roomStates[location.room.id]['color'] = "red";
		roomStates[location.room.id]['paintMeetNow'] = false;
		roomStates[location.room.id]['paintOcc'] = true;
		roomStates[location.room.id]['paintAvailUntil'] = false;
		roomStates[location.room.id]['paintCancelIn'] = false;
		roomStates[location.room.id]['paintBookedUntil'] = true;
		roomStates[location.room.id]['booked'] = true;
		roomStates[location.room.id]['occupied'] = true;

	}

	
}

function applyToolTips(){
	$('i[class*="cus-unbooked"]').tooltip({title:'Unbooked', placement:'bottom'});
	$('i[class*="cus-booked"]').tooltip({title:'Booked', placement:'bottom'});
	$('i[class*="cus-hollow"]').tooltip({title:'Unoccupied', placement:'bottom'});
	$('i[class*="cus-solid"]').tooltip({title:'Occupied', placement:'bottom'});
	$('i[class*="cus-right"]').tooltip({title:'Expand / Collapse', placement:'bottom'});
	$('i[class*="cus-down"]').tooltip({title:'Expand / Collapse', placement:'bottom'});
}


function fillRoom(location){
	//create room content
	//assumes a well is already in place.
	console.log("room="+location.room.name+" occ="+location.occupied+" rsv="+location.reserved+" reap="+location.time_to_reap );
	
	var roomEl = $("#"+location.room.id);
	
	if (!roomEl.hasClass("well")){
		return;
	}
	
	//empty room well - note this removes event handlers too
	roomEl.empty();
	clearWellClass(roomEl);
	
	//well should be empty and clean of earlier states at this point
	//load room states
	loadRoomStates(location)
	
	console.log("room="+location.room.name+" color="+ roomStates[location.room.id]['color']);

	var color = roomStates[location.room.id]['color'] ;
	
	roomEl.addClass("well-"+color);
	roomEl.attr("color-state",color);
	
	//required for the filter handler
	if (roomStates[location.room.id]['booked']) {
		roomEl.attr("booked-state","booked");
	}else {
		roomEl.attr("booked-state","unbooked");
	}
	
	//append room header
	roomEl = appendRoomHeader(roomEl,location.room.name);
	
	//set icons
	icon1 = roomEl.find(".ic1");
	if (roomStates[location.room.id]['booked']){
		icon1.addClass('cus-booked-'+color);
	} else {
		icon1.addClass('cus-unbooked-'+color);
	}

	icon2 = roomEl.find(".ic2");
	if (roomStates[location.room.id]['occupied']){
		icon2.addClass('cus-solid-user-'+color);
	} else {
		icon2.addClass('cus-hollow-user-'+color);
	}
	
	icon3 = roomEl.find(".ic3");
	if (roomStates[location.room.id]['up_down'] == "up"){
		icon3.addClass('arr-up cus-right-'+color);	
	} else {
		icon3.addClass('arr-down cus-down-'+color);	
	}
	
	//append meet now link
	if (roomStates[location.room.id]['paintMeetNow']){
		roomEl = appendMeetNow(roomEl);
	}
	
	if (roomStates[location.room.id]['paintCancelIn']){
		roomEl = appendCancellationIn(roomEl, format_time(location.time_to_reap));
	}
	
	if (roomStates[location.room.id]['paintOcc']){
		roomEl = appendOccupancy(roomEl,location.occupancy_pct);
	}
	
	if (roomStates[location.room.id]['paintBookedUntil']){
		if (location.booked_until != null){
			roomEl = appendBookedUntil(roomEl, format_booked_date(location.booked_until));
		}else {
			roomEl = appendBookedUntil(roomEl, '');
		}
	}
	
	if (roomStates[location.room.id]['paintAvailUntil']){
		if (location.avail_until != null){
			roomEl = appendAvailabilityUntil(roomEl, format_booked_date(location.avail_until));
		}else {
			roomEl = appendAvailabilityUntil(roomEl, '');
		}
	}

	//reapply up/down state
	applyUpDownState(roomEl);
	
}


function format_time(secs){
	t = secs;
	var h = Math.floor(t/3600);
	var t = t%3600;
    var m = Math.floor(t / 60);
    var s = Math.floor(t % 60);
	
    var st = ((h > 0 ? h + 'h ' : '') +
            (m > 0 ? m + 'm ' : '') +
            s + 's');
    
    return st;
}

function format_booked_date(dt_str){
	var d = new Date(dt_str);
	//var str = d.getHours()+":"+d.getMinutes();
	var h = d.getHours();
	var t = d.getMinutes();
	var ampm;
	if (h > 12) {
		h = d.getHours() - 12;
		t = t<10?"0"+t:""+t;
		ampm = "p";
	} else if (h == 12) {
		h = "noon";
		t = ""
		ampm = "";
	} else {
		t = t<10?"0"+t:""+t;
		ampm = "a"
	}
	
	str = h+":"+t+ampm;
	return str;
}



