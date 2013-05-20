# Call Calendar v3 api with 2 legged auth

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


def main():
    CONSUMER_KEY = "yyyyyyyyy.com"
    CONSUMER_SECRET = "uuuuuuuuuuuuuuuuuuuuuuuu"
    ADMIN_USER_EMAIL = "zzzzz@yyyyyyyyyyy.com"
    DEVELOPER_KEY="AUAUAUAUAUAUAUAUAUAUAUAUAUAUAUAUAUAUAUA"
    
    credentials = oauth.TwoLeggedOAuthCredentials(
      consumer_key=CONSUMER_KEY,
      consumer_secret=CONSUMER_SECRET,
      user_agent='Python-EDT-Cal-Clear/1.0')
    
    credentials.setrequestor(ADMIN_USER_EMAIL)
    
    http = httplib2.Http()
    http = credentials.authorize(http)
    
    service = build(serviceName='calendar',
                version='v3',
                http=http,
                developerKey=DEVELOPER_KEY)
    
    print service
    credentials.setrequestor(ADMIN_USER_EMAIL)
    
    calendar_list = service.calendarList().list().execute()
    while True:
        for calendar_list_entry in calendar_list['items']:
            print calendar_list_entry['id'], calendar_list_entry['summary'], calendar_list_entry['accessRole'],
            calendar_list_entry['timeZone']
            print
            
        page_token = calendar_list.get('nextPageToken')
        if page_token:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
        else:
            break
    
    cal = service.calendars().get(calendarId="yyyyyyyy.com_313434373730362d393933@resource.calendar.google.com").execute()
    
    if cal:
        print cal
        print cal["id"], cal["summary"], cal["timeZone"]
        
    #get this from the calendar
    cal_tzone='America/Los_Angeles'
    curr_time=datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
    time_min = datetime.datetime.strftime(curr_time,'%Y-%m-%dT%H:%M:%S%z')
    
    print time_min
        
    
    events = service.events().list(calendarId="yyyyyyyyyyy.com_313434373730362d393933@resource.calendar.google.com",
                                   orderBy="startTime",
                                   singleEvents=True,
                                   timeMin=time_min,  #lower bound on end time
                                   #timeZone='utc'  #return all times as utc,
                                   maxResults=1
                                   ).execute()
    #Note: the above only works for single events -not for recurring events
    #timeMax doesn't seem to work
    
    while True:
        for event in events['items']:
            print event["id"],  event['start'], event['end'], event['organizer'],
            event['location']
            
            #2012-05-24T10:00:00-07:00
            #start_time = datetime.datetime.strptime(event['start'],'%Y-%m-%dT%H:%M:%S%z')
            start_time = parse(event['start']['dateTime'])
            end_time = parse(event['end']['dateTime'])
            
            print start_time, end_time
            
            print
        
        page_token = events.get('nextPageToken')
        if page_token:
            events = service.events().list(calendarId="yyyyyyyyyyy.com_313434373730362d393933@resource.calendar.google.com", pageToken=page_token).execute()
        else:
            break
        
    
    #cancel an event
    #ret = service.events().delete(calendarId="yyyyyyyyyyy.com_313434373730362d393933@resource.calendar.google.com",
    #                        eventId="ehc1kh5vhp84tregprq40q4hv0").execute()
                            
    #print ret
                            
    
        
    
    
    return

    
if __name__ == '__main__':
    main()
