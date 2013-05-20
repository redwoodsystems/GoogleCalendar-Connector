from celery.task import task, Task, subtask
import datetime, time, pytz
from django.utils import timezone


from models import ReaperConfig, RoomConfig, RoomStatus, ReaperLog
from models import PseudoRoomMotion, PseudoRoomResv

from django.db import transaction

from gcal_v3_util import GCalendar

from motion import call_motion_api
from motion_new import get_occupancy

from mysite.settings import OCC_THRESHOLD

# max vacancy (secs) allowed before treating room / fixture as unoccupied
if not OCC_THRESHOLD or OCC_THRESHOLD <=0:
    OCC_THRESHOLD = 300
else:
    OCC_THRESHOLD = OCC_THRESHOLD * 60;

class DebugTask(Task):
    abstract = True

    def after_return(self, *args, **kwargs):
        print("Task returned: %r" % (self.request, ))
        #print("Task returned: task: %r  args: %r kwargs: %r" 
        #        % (self.request.task, self.request.args, self.request.kwargs, ))

@task
def add(x, y):
    return x + y


@task(ignore_result=True, base=DebugTask)
def poller():
    #for each room:
        #process_room --> get motion api --> get reservation status -->reap --> notify -->update_room_status
    
    rc = None
    for r in ReaperConfig.objects.all():
        rc = r
        break
    
    rooms = RoomConfig.objects.filter(motion_enabled=True)
    
    for rm in rooms:
        print ("loop --> room_id: %d" %(rm.id))
        room={'room_id':rm.id, 'calendar_id':rm.g_calendar_id, 'name':rm.name, 'location_id':rm.rw_location_id}
        room['rw_api_url']=rc.rw_api_url
        room['rw_api_user']=rc.rw_api_user
        room['rw_api_pwd']=rc.rw_api_pwd
        process_room.delay(room)

    return True

@task(ignore_result=True, base=DebugTask)
def process_room(room):
    # Create room status entry if not exists and commit !!
    # Call director api
    print ("process_room --> room_id: %d" %(room['room_id']))
        
    #check if room status record exists. If not create initial record
    create_room_status(room)
    
    result = fetch_occ_from_director.delay(room, callback=subtask(fetch_rsv_from_cal,
                                                                     callback=subtask(reap)))
    
    return result
    
        
@task(ignore_result=True)
def fetch_occ_from_director(room,callback=None):
    print ("fetch_occ_from_director --> room_id: %d" %(room['room_id']))    
    
    (occupied_pct, motion_instant) = get_current_pct_occupancy(room)
    
    curr_motion_time = datetime.datetime.utcfromtimestamp(motion_instant).replace(tzinfo=pytz.timezone('utc'))
      
    if callback:
        subtask(callback).delay(room, curr_motion_time, occupied_pct)
    
    return True

@task(ignore_result=True)
def fetch_rsv_from_cal(room, curr_motion_time, occupied_pct, callback=None):
    
    rc = None
    for r in ReaperConfig.objects.all():
        rc = r
        break
    
    #initialize google calendar api
    gcal = GCalendar(rc.g_consumer_key, rc.g_consumer_secret, rc.g_admin_user_email, rc.g_developer_key)
    
    if not gcal:
        print("Google Calendar API not initialized")
        return None

    #Get reservation if found at current time.     
    #event = gcal.getCurrentEventFromCalendar(room['calendar_id'])
    (event, next_event) = gcal.getCurrentOrNextEventFromCalendar(room['calendar_id'])
    
    if event and event.has_key('id'):
        rsv_status=True
    else:
        rsv_status=False
        
    print ("fetch_rsv_from_cal --> room_id: %d curr_motion_time: %r rsv_status: %d" 
                %(room['room_id'], curr_motion_time, rsv_status))
    
    
    if callback:
        subtask(callback).delay(room, rsv_status, event, curr_motion_time, occupied_pct, next_event)
        
    return rsv_status

@task(ignore_result=True)
def reap(room, rsv_status, event, curr_motion_time, occupied_pct, next_event):
    print ("reap --> room_id: %d curr_motion_time: %r rsv_status: %d occ_pct %f" 
                %(room['room_id'], curr_motion_time, rsv_status, occupied_pct))
    current_time = timezone.now()
    print "current time (UTC): %r" %(current_time)
    
    #get timeout from reaperconfig
    reaper_config = None
    for r in ReaperConfig.objects.all():
        reaper_config = r
        break
    
    
    #if api did not return motion time for some reason, then set it to current time
    #to prevent greedy reaps
    
    if not curr_motion_time:
        curr_motion_time = current_time
    
    #calculate vacant_secs
    if curr_motion_time:        
        vacant_secs = get_pos_time_diff_secs(current_time, curr_motion_time)
    else:
        vacant_secs = None
            
    #Calculate occ_status
    #vacant_secs > 120 secs, occ_status = False
    #if vacant_secs > 10:
    if vacant_secs > OCC_THRESHOLD:
        occ_status = False
    else:
        occ_status = True
        
    
    #Reaper Logic    
    time_to_reap = None
    reaped = False
    avail_until = None
    if rsv_status:
        occ_timeout_secs = reaper_config.occ_motion_timeout * 60
        event_start_secs = get_pos_time_diff_secs(current_time,event['start_time'])
        print "occ_timeout_secs: %f vacant_secs: %f sec_fr_event_start: %f" %(occ_timeout_secs, vacant_secs, event_start_secs)
        
        time_to_reap = None
        reaped = False
        
        #use the smaller number as the comparator
        if vacant_secs < event_start_secs:
            cmp_secs = vacant_secs 
        else:
            cmp_secs = event_start_secs
        
        # wait till occ_timeout_secs from vacant time or from start of meeting which ever is less
        if (cmp_secs >= occ_timeout_secs):
            print "OK to reap"
            time_to_reap = 0        
            #initialize google calendar api
            gcal = GCalendar(reaper_config.g_consumer_key, reaper_config.g_consumer_secret, 
                             reaper_config.g_admin_user_email, reaper_config.g_developer_key)
    
            if not gcal:
                print("Google Calendar API not initialized")
                return None
            
            reaped = gcal.deleteEventFromCalendar(room['calendar_id'], event['id'], send_notification=True)
            occ_status=False  #just in case
            rsv_status=False        
        else:
            time_to_reap = occ_timeout_secs - cmp_secs

        if time_to_reap:        
            print "time_to_reap: %f" %(time_to_reap)
        else:
            print "time_to_reap: None"
            
    
    #room is available till next event
    if next_event and 'start_time' in next_event:
        avail_until = next_event['start_time']

    #Update room status
    if rsv_status and not reaped:
        booked_until = None
        if event.has_key('booked_until'):
            booked_until = event['booked_until']
        else:
            booked_until = event['end_time']
            
        update_room_status(room,
                             occupied = occ_status,
                             reserved = rsv_status,
                             last_motion_ts = curr_motion_time,
                             last_checked_ts = current_time,
                             time_to_reap = time_to_reap,
                             vacant_secs = vacant_secs,
                             occupancy_pct = occupied_pct,
                             booked_until = booked_until,
                             avail_until = None,
                             rsv_begin_time = event['start_time'],
                             rsv_end_time = event['end_time'],
                             rsv_owner_email = event['owner_email'],
                             rsv_owner_name = event['owner_name'],
                             event_timezone = event['timezone'],
                             allow_res=False
                            )
    else:
        update_room_status(room,
                             occupied = occ_status,
                             reserved = rsv_status,
                             last_motion_ts = curr_motion_time,
                             last_checked_ts = current_time,
                             time_to_reap = None,
                             vacant_secs = None,
                             occupancy_pct = occupied_pct,
                             booked_until = None,
                             avail_until = avail_until,
                             rsv_begin_time = None,
                             rsv_end_time = None,
                             rsv_owner_email = None,
                             rsv_owner_name = None,
                             event_timezone = None,
                             allow_res=True
                            )    
        
    #Notify on cancellation and write to log
    if reaped:
        notify_on_event.subtask().delay(room,event,action='CANCEL_RSV')
        
    
            
        
@task(ignore_result=True)
def notify_on_event(room,event,action):
    #notify
    #add to log
    print ("notify-->room_id %d event %r" %(room['room_id'], action))
    
    if action =='CANCEL_RSV':
        log_reap_event(room,event)
    
    return True
        

#Utility Methods
def get_current_motion(room, pseudo=False):
    
    if pseudo:
        motion = PseudoRoomMotion.objects.get(id=room['room_id'])
        return motion.curr_motion_time
    else:
        instant = call_motion_api(room['rw_api_url'],room['rw_api_user'],room['rw_api_pwd'],
                                  room['location_id'])
        #create a timezone aware datetime from instant
        dt = datetime.datetime.utcfromtimestamp(instant).replace(tzinfo=pytz.timezone('utc'))
        #print "instant=%d dt=%r"%(instant,dt)
        return dt

    #convert from UNIX timestamp (secs. since epoch) to aware datetime
    #time.mktime(datetime.datetime.now().timetuple())
    
    #return (datetime.datetime.fromtimestamp(motion.motion_instant))

def get_current_pct_occupancy(room):
    current_time = timezone.now()
    (occ_pct, motion_instant) = get_occupancy(room['rw_api_url'],room['rw_api_user'],room['rw_api_pwd'],room['location_id'], current_time, OCC_THRESHOLD)
    return (occ_pct, motion_instant)
    
    

def get_current_room_resv(room_id, gcal):
    rr=None
    for r in PseudoRoomResv.objects.filter(id=room_id):
        rr=r
    
    if rr:
        return (rr.reserved, rr.rsv_begin_time, rr.rsv_end_time, rr.rsv_owner_id)
    else:
        return (False, None, None, None)


@transaction.commit_manually
def create_room_status(room):
    #create room status record if one does not exist    
    try:
        res = RoomConfig.objects.filter(id=room['room_id'])
        rc=None
        for r in res:
            rc=r
        
        if not rc:
            return
        
        res = RoomStatus.objects.filter(room_id=room['room_id'])
        rm = None
        for r in res:
            rm = r
            break    
        
        if not rm:            
            rm = RoomStatus(room=rc,
                             occupied=False,
                             reserved=False,
                             last_motion_ts=None,
                             last_checked_ts=None,
                             vacant_secs=None,
                             time_to_reap=None,
                             occupancy_pct=None,
                             avail_until=None,
                             booked_until=None,
                             rsv_begin_time=None,
                             rsv_end_time=None,
                             rsv_owner_email=None,
                             rsv_owner_name=None,
                             event_timezone=None,
                             allow_res=True
                             )
            rm.save()
    except:
        transaction.rollback()
        raise
    else:
        transaction.commit()
            
    return True



@transaction.commit_manually
def update_room_status(room, **kwargs):
    rm=None
    for r in RoomStatus.objects.filter(room_id=room['room_id']):
        rm =r
        break
    
    if rm:
        try:
            if 'occupied' in kwargs:
                rm.occupied=kwargs['occupied']
            if 'reserved' in kwargs:
                rm.reserved=kwargs['reserved']
            if 'last_motion_ts' in kwargs:
                rm.last_motion_ts=kwargs['last_motion_ts']
            if 'last_checked_ts' in kwargs:
                rm.last_checked_ts=kwargs['last_checked_ts']
            if 'vacant_secs' in kwargs:
                rm.vacant_secs=kwargs['vacant_secs']
            if 'time_to_reap' in kwargs:
                rm.time_to_reap=kwargs['time_to_reap']
            if 'rsv_begin_time' in kwargs:
                rm.rsv_begin_time=kwargs['rsv_begin_time']
            if 'rsv_end_time' in kwargs:
                rm.rsv_end_time=kwargs['rsv_end_time']
            if 'rsv_owner_email' in kwargs:
                rm.rsv_owner_email=kwargs['rsv_owner_email']
            if 'rsv_owner_name' in kwargs:
                rm.rsv_owner_name=kwargs['rsv_owner_name']
            if 'event_timezone' in kwargs:
                rm.event_timezone=kwargs['event_timezone']
            if 'allow_res' in kwargs: 
                rm.allow_res=kwargs['allow_res']
            if 'occupancy_pct' in kwargs: 
                rm.occupancy_pct=kwargs['occupancy_pct']
            if 'avail_until' in kwargs: 
                rm.avail_until=kwargs['avail_until']
            if 'booked_until' in kwargs: 
                rm.booked_until=kwargs['booked_until']
            rm.save()
        except:
            transaction.rollback()
            raise
        else:
            transaction.commit()
    return True
            
def get_pos_time_diff_secs(dt1, dt2):
    #Assumes that both dates are timzone aware and stored in UTC
    diff = dt1 - dt2
    if diff.days >=0:
        return diff.seconds
    else:
        return 0


@transaction.commit_manually
def log_reap_event(room,event):
    
    try:
        dbLog = ReaperLog()
        if event and event.has_key('id'):
            dbLog.g_event_id = event['id']
            dbLog.rsv_begin_time = event['start_time']
            dbLog.rsv_end_time = event['end_time']
            dbLog.rsv_owner_email = event['owner_email']
            dbLog.rsv_owner_name = event['owner_name']
        dbLog.room_id = room['room_id']
        dbLog.room_calendar_id = room['calendar_id']
        dbLog.room_name = room['name']
        dbLog.save()
    except:
        transaction.rollback()
        raise
    else:
        transaction.commit()
    
    return True
            



    
        
