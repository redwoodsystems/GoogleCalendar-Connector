from django.db import models
import datetime
from django.utils import timezone

# Create your models here.
class ReaperConfig(models.Model):
    id = models.AutoField(primary_key=True)
    rw_api_url = models.CharField(max_length=500, verbose_name='Redwood API URL')
    rw_api_user = models.CharField(max_length=30, verbose_name='Redwood API User')
    rw_api_pwd = models.CharField(max_length=30, verbose_name='Redwood API Password')
    occ_motion_timeout = models.IntegerField(verbose_name='Cancel After (Mins.)')
    notif_duration = models.IntegerField(default=15, verbose_name='Notification Duration')
    motion_poll_freq = models.IntegerField(default=30, verbose_name='Motion Poll Frequency')
    g_consumer_key = models.CharField(max_length=100, verbose_name='Google Consumer Key')
    g_consumer_secret = models.CharField(max_length=100, verbose_name='Google Consumer Secret')
    g_admin_user_email = models.CharField(max_length=100, verbose_name='Google Admin User Email')
    g_developer_key = models.CharField(max_length=100, verbose_name='Google Developer Key')
    creation_date = models.DateTimeField(default=timezone.now)
    last_modified_date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = u'rw_reaper_config'
        verbose_name = u'Configuration'
        verbose_name_plural = u'Configuration'
        
    def __unicode__(self):
        return u'Default'

    

class RoomConfig(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='Room Name')
    motion_enabled = models.BooleanField(default=True, verbose_name='Motion Enabled')
    g_calendar_id = models.CharField(max_length=200, blank=True, null=True, verbose_name='Google Calendar Id')
    rw_location_id = models.IntegerField(blank=True, null=True, verbose_name='Redwood Location Id')
    rw_location_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Redwood Location Name')
    creation_date = models.DateTimeField(default=timezone.now)
    last_modified_date = models.DateTimeField(default=timezone.now)
    
    def __unicode__(self):
        return u'%s' %(self.name)
    
    
    class Meta:
        db_table = u'rw_room_config'
        verbose_name = u'Room Setup'
        verbose_name_plural = u'Room Setup'


class RoomStatus(models.Model):
    id = models.AutoField(primary_key=True)
    room = models.ForeignKey(RoomConfig, verbose_name='Room')
    occupied = models.BooleanField(default=False, verbose_name='Occupied')
    reserved = models.BooleanField(default=False, verbose_name='Reserved')
    last_motion_ts = models.DateTimeField(blank=True, null=True, verbose_name='Last Motion Timestamp')
    last_checked_ts = models.DateTimeField(blank=True, null=True, verbose_name='Last Checked Timestamp')
    vacant_secs = models.IntegerField(blank=True, null=True, verbose_name='Vacant Seconds')
    time_to_reap = models.IntegerField(blank=True, null=True, verbose_name='Time to Reap' )
    occupancy_pct = models.FloatField(blank=True, null=True, verbose_name='Occupancy Pct')
    avail_until =  models.DateTimeField(blank=True, null=True, verbose_name='Availability Until')
    booked_until = models.DateTimeField(blank=True, null=True, verbose_name='Booked Until')
    rsv_begin_time = models.DateTimeField(blank=True, null=True, verbose_name='Reservation Begin Time')
    rsv_end_time = models.DateTimeField(blank=True, null=True, verbose_name='Reservation End Time')
    rsv_owner_email = models.CharField(max_length=100, blank=True, null=True, verbose_name='Reservation Owner Email')
    rsv_owner_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Reservation Owner Name')
    event_timezone = models.CharField(max_length=30, blank=True, null=True, verbose_name='Event Timezone')
    allow_res = models.BooleanField(default=True, verbose_name='Allow Reservation')
    creation_date = models.DateTimeField(default=timezone.now)
    last_modified_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = u'rw_room_status'
        verbose_name = u'Room Status'
        verbose_name_plural = u'Room Status'


class PseudoRoomMotion(models.Model):
    id = models.IntegerField(primary_key=True)
    motion_detected = models.BooleanField(default=True)
    motion_instant = models.IntegerField(blank=True, null=True)
    curr_motion_time = models.DateTimeField(blank=True, null=True)
    class Meta:
        db_table = u'rw_pseudo_room_motion'
        verbose_name = u'Pseudo Room Motion'
        verbose_name_plural = u'Pseudo Room Motion'
    

class PseudoRoomResv(models.Model):
    id = models.IntegerField(primary_key=True)
    reserved = models.BooleanField(default=True)
    rsv_begin_time = models.DateTimeField(blank=True, null=True)
    rsv_end_time = models.DateTimeField(blank=True, null=True)
    rsv_owner_email = models.CharField(max_length=100, blank=True, null=True)
    rsv_owner_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = u'rw_pseudo_room_resv'
        verbose_name = u'Pseudo Room Resv'
        verbose_name_plural = u'Pseudo Room Resv'
        
class ReaperLog(models.Model):
    id = models.AutoField(primary_key=True)
    g_event_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='Google Event Id')
    rsv_begin_time = models.DateTimeField(blank=True, null=True, verbose_name='Begin Time')
    rsv_end_time = models.DateTimeField(blank=True, null=True, verbose_name='End Time')
    rsv_owner_email = models.CharField(max_length=100, blank=True, null=True, verbose_name='Owner Email')
    rsv_owner_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Owner Name')
    room = models.ForeignKey(RoomConfig, verbose_name='Room Name')
    room_calendar_id = models.CharField(max_length=100, verbose_name='Google Calendar Id')
    room_name = models.CharField(max_length=100, verbose_name='Room Name')
    reap_date = models.DateTimeField(default=timezone.now, verbose_name='Cancel Time')
    creation_date = models.DateTimeField(default=timezone.now)
    last_modified_date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = u'rw_reaper_log'
        verbose_name = u'Room Cancellation Log'
        verbose_name_plural = u'Room Cancellation Log'
        
    def __unicode__(self):
        return u'%s' %(self.room_name)

