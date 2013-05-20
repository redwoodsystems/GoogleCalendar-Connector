from reaper.models import ReaperConfig, RoomConfig, RoomStatus, ReaperLog
from django.contrib import admin

class RoomConfigAdmin(admin.ModelAdmin):
    fields = ['id','name', 'g_calendar_id', 'rw_location_id', 'rw_location_name', 'motion_enabled', 'creation_date','last_modified_date']
    readonly_fields = ('id','creation_date','last_modified_date')
    list_display = ('id', 'name', 'rw_location_id', 'rw_location_name', 'motion_enabled',)
    list_filter = ['name', 'rw_location_name', 'motion_enabled']
    search_fields = ['name', 'rw_location_name']
    actions = None
    
admin.site.register(RoomConfig, RoomConfigAdmin)


class ReaperConfigAdmin(admin.ModelAdmin):
    fields = ['rw_api_url', 'rw_api_user', 'rw_api_pwd', 'occ_motion_timeout',
              'g_consumer_key', 'g_consumer_secret', 'g_admin_user_email', 'g_developer_key' ]
    readonly_fields = ('creation_date','last_modified_date')
    list_display = ('rw_api_url', 'rw_api_user', 'rw_api_pwd', 'last_modified_date')
    actions = None
    
    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(ReaperConfig, ReaperConfigAdmin)


class ReaperLogAdmin(admin.ModelAdmin):
    fields = ['id','g_event_id', 'rsv_begin_time', 'rsv_end_time', 'rsv_owner_email', 'rsv_owner_name',
              'room', 'room_calendar_id', 'room_name', 'reap_date', 'creation_date', 'last_modified_date']
    readonly_fields = ('id','g_event_id', 'rsv_begin_time', 'rsv_end_time', 'rsv_owner_email', 'rsv_owner_name',
              'room', 'room_calendar_id', 'room_name', 'reap_date', 'creation_date','last_modified_date')
    list_display = ('id','room_name','rsv_begin_time', 'rsv_end_time', 'rsv_owner_name',
                    'reap_date')
    list_filter = ['room_name', 'reap_date']
    search_fields = ['room_name', 'rsv_owner_email', 'rsv_owner_name']
    actions = None
    list_per_page = 100

admin.site.register(ReaperLog, ReaperLogAdmin)


"""
Unregister Django Celery Admin
"""

from djcelery.models import (TaskState, WorkerState,
                 PeriodicTask, IntervalSchedule, CrontabSchedule)

admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)

"""
Unregister Site Admin
"""
from django.contrib.sites.models import Site
admin.site.unregister(Site)

"""
Unregister Auth Groups
"""
from django.contrib.auth.models import Group
admin.site.unregister(Group)

from django.contrib.auth.models import User
admin.site.unregister(User)


from django.contrib import auth

class UserAdminNew(auth.admin.UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password',
        'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser')}),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', )
    list_filter = ('is_active',)
    actions = None
    
admin.site.register(User, UserAdminNew)
