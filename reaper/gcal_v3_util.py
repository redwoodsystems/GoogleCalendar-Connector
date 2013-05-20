import csv
import datetime
import logging
from optparse import OptionParser
import sys
from apiclient import oauth
from apiclient.discovery import build
import httplib2

from dateutil.parser import parse
import pytz

# Calls Calendar v3 api with 2 legged auth
# Requires consumer key, consumer secret and admin email address

class GCalendar(object):
    
    def __init__(self, consumer_key, consumer_secret, admin_user_email, developer_key):
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._admin_user_email = admin_user_email
        self._developer_key = developer_key
        self._service = None
        self.getService()
    
    def getService(self, refresh=False):
        if refresh or not self._service:        
            credentials = oauth.TwoLeggedOAuthCredentials(
            consumer_key=self._consumer_key,
            consumer_secret=self._consumer_secret,
            user_agent='Python-EDT-Cal-Clear/1.0')
            
            #we will always be working with the admin user    
            credentials.setrequestor(self._admin_user_email)
            
            http = httplib2.Http()
            http = credentials.authorize(http)
            
            self._service = build(serviceName='calendar',
                        version='v3',
                        http=http,
                        developerKey=self._developer_key)
            
        return self._service
    
    def getCurrentEventFromCalendar(self, calendar_id, default_tz='America/Los_Angeles'):
        print "calendar_id: ", calendar_id
        if not calendar_id:
            return None
        
        cal = self._service.calendars().get(calendarId=calendar_id).execute()
        
        event_dict={}
        if cal:
            if cal['timeZone']:
                curr_time=datetime.datetime.now(pytz.timezone(cal['timeZone']))
            else:
                curr_time=datetime.datetime.now(pytz.timezone(default_tz))
                
            time_min = datetime.datetime.strftime(curr_time,'%Y-%m-%dT%H:%M:%S%z')
                        
            events = self._service.events().list(calendarId=calendar_id,
                               orderBy="startTime",
                               singleEvents=True,
                               timeMin=time_min,  #lower bound on end time
                               #timeZone='utc'  #return all times as utc,
                               maxResults=1  #does not handle double booking of resource
                               ).execute()
            #Note: the above only works for single events -not for recurring events
            #timeMax doesn't seem to work
            #does not handle double booking of resource
            
            
            if events and 'items' in events:
                for event in events['items']:
                    found = False
                    #2012-05-24T10:00:00-07:00
                    #start_time = datetime.datetime.strptime(event['start'],'%Y-%m-%dT%H:%M:%S%z')
                    start_time = parse(event['start']['dateTime'])
                    
                    end_time = parse(event['end']['dateTime'])
                    
                    #Imp: start_time must be less than curr_time
                    tds = curr_time - start_time
                    # end_time must be > curr_time
                    tde = end_time - curr_time
                    #meeting length - don't cancel meetings > 8hrs
                    td_length = end_time - start_time
                    
                    if tds.days >= 0 and tde.days >=0 and td_length.seconds < 14400 and tde.seconds < 14400:
                        found = True
                        
                    if (found):                    
                        event_dict['calendar_id'] = calendar_id                
                        event_dict['id'] = event["id"]
                        event_dict['start_time'] = parse(event['start']['dateTime'])
                        event_dict['end_time'] = parse(event['end']['dateTime'])
                        event_dict['owner_name'] = event['organizer']['displayName']
                        event_dict['owner_email'] = event['organizer']['email']
                        event_dict['timezone'] = (cal['timeZone'] if cal['timeZone'] else default_tz)
                        #just get one event                
                        break
        
        #print event_dict
        return event_dict
    
    def deleteEventFromCalendar(self, calendar_id, event_id, send_notification=False):
        print "delete from calendar"
        self._service.events().delete(calendarId=calendar_id,
                            eventId=event_id, sendNotifications=send_notification).execute()
        return True
        
    def createNewEvent(self,calendar_id, send_notification=False):
        
        event = {
              'summary': 'Test Appointment',
              'location': 'Somewhere',
              'start': {
                'dateTime': '2012-06-03T10:00:00.000-07:00'
              },
              'end': {
                'dateTime': '2012-06-03T10:25:00.000-07:00'
              },
              'attendees': [
                {
                  'email': self._admin_user_email
                },
                # ...
              ],
            }
        
        created_event = self._service.events().insert(calendarId=calendar_id, body=event).execute()
        
        #print created_event['id']
        return created_event['id']
    
    
    def getCurrentOrNextEventFromCalendar(self, calendar_id, default_tz='America/Los_Angeles'):
        print "calendar_id: ", calendar_id
        if not calendar_id:
            return None
        
        cal = self._service.calendars().get(calendarId=calendar_id).execute()
        
        curr_event_dict={}
        next_event_dict={}
        
        if cal:
            if cal['timeZone']:
                curr_time=datetime.datetime.now(pytz.timezone(cal['timeZone']))
            else:
                curr_time=datetime.datetime.now(pytz.timezone(default_tz))
                
            time_min = datetime.datetime.strftime(curr_time,'%Y-%m-%dT%H:%M:%S%z')
                        
            events = self._service.events().list(calendarId=calendar_id,
                               orderBy="startTime",
                               singleEvents=True,
                               timeMin=time_min,  #lower bound on end time
                               #timeZone='utc'  #return all times as utc,
                               maxResults=1  #does not handle double booking of resource
                               ).execute()
            #Note: the above only works for single events -not for recurring events
            #timeMax doesn't seem to work
            #does not handle double booking of resource
            
            if events and 'items' in events:
                for event in events['items']:
                    found_current= False
                    found_next = False
                    #2012-05-24T10:00:00-07:00
                    #start_time = datetime.datetime.strptime(event['start'],'%Y-%m-%dT%H:%M:%S%z')
                    start_time = parse(event['start']['dateTime'])
                    
                    end_time = parse(event['end']['dateTime'])
                    
                    #Imp: start_time must be less than curr_time for current event
                    tds = curr_time - start_time
                    # end_time must be > curr_time
                    tde = end_time - curr_time
                    #meeting length - don't cancel meetings > 8hrs
                    td_length = end_time - start_time
                    
                    if tds.days >= 0 and tde.days >=0 and td_length.seconds < 14400 and tde.seconds < 14400:
                        found_current = True
                        
                    if tds.days < 0 and tde.days >=0 and td_length.seconds < 14400 and tde.seconds < 14400:
                        found_next = True
                        
                    if (found_current):                    
                        curr_event_dict['calendar_id'] = calendar_id                
                        curr_event_dict['id'] = event["id"]
                        curr_event_dict['start_time'] = parse(event['start']['dateTime'])
                        curr_event_dict['end_time'] = parse(event['end']['dateTime'])
                        curr_event_dict['owner_name'] = event['organizer']['displayName']
                        curr_event_dict['owner_email'] = event['organizer']['email']
                        curr_event_dict['timezone'] = (cal['timeZone'] if cal['timeZone'] else default_tz)
                        #just get one event                
                        break
                    elif (found_next):
                        next_event_dict['calendar_id'] = calendar_id                
                        next_event_dict['id'] = event["id"]
                        next_event_dict['start_time'] = parse(event['start']['dateTime'])
                        next_event_dict['end_time'] = parse(event['end']['dateTime'])
                        next_event_dict['owner_name'] = event['organizer']['displayName']
                        next_event_dict['owner_email'] = event['organizer']['email']
                        next_event_dict['timezone'] = (cal['timeZone'] if cal['timeZone'] else default_tz)
                        break
                    
            #Find booked until if currently booked. Combine consecutive events if any
            
            if events and 'items' in events and curr_event_dict.has_key('id'):
                c1=curr_event_dict['end_time']
                for event in events['items']:
                    if event['id'] == curr_event_dict['id']:
                        continue
                    print parse(event['start']['dateTime']), c1
                    if parse(event['start']['dateTime']) == c1:
                        c1=parse(event['end']['dateTime'])
                        print "newc1",c1
                    else:
                        break
                curr_event_dict['booked_until'] = c1
            else:
                curr_event_dict['booked_until'] = None
                    
        return (curr_event_dict, next_event_dict)

        
        
if __name__ == "__main__":
    gcal = GCalendar("yyyyyy.com","yyyyyyyyyyyyyyyy","yyyyyyyyyyyyyyyy@zzzzzz.com","yyyyyyyyyyyyyyyy")
    calendar_id = 'zzzzzz.com_yyyyyyyyyyyyyyyy@resource.calendar.google.com'
    event_id = gcal.createNewEvent(calendar_id)
    if event_id:
        gcal.deleteEventFromCalendar(calendar_id, event_id, True)
    event_dict = gcal.getCurrentEventFromCalendar(calendar_id)
    print event_dict
 
