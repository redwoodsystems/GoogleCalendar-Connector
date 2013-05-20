# Uses 2-legged Auth with GData API to access google calendars

import gdata.auth
import gdata.calendar.service

import datetime

def get_next_event(req_email_address, calendar_name='default'):
    """Uses two-legged OAuth to retrieve the user's next Calendar event."""
    CONSUMER_KEY = "llllllllllllll"
    CONSUMER_SECRET = "mmmmmmmmmmmmmmmmmmmmmmmm"
    SIG_METHOD = gdata.auth.OAuthSignatureMethod.HMAC_SHA1
    
    client = gdata.calendar.service.CalendarService(source='mmmmmm.com')
    
    client.SetOAuthInputParameters(SIG_METHOD, CONSUMER_KEY, consumer_secret=CONSUMER_SECRET,
                                   two_legged_oauth=True, requestor_id=req_email_address )
    
    #query = gdata.calendar.service.CalendarEventQuery('default', 'private', 'full')
    query = gdata.calendar.service.CalendarEventQuery(calendar_name, 'private', 'full')
    query.start_min = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    query.sortorder = 'ascending'
    query.orderby = 'starttime'
    #query.max_results = 1
    query.max_results = 10
    feed = client.CalendarQuery(query)
    
    if len(feed.entry):
        #return feed.entry[0]
        return feed.entry
    else:
        return None
    
def main():
    
    events = get_next_event(req_email_address='zzzz.yyyyy.com',
                            calendar_name='zzzz@yyyy.com'
                            )
    
    for event in events:
        print event.title.text
        print event.when[0].start_time
        print event.when[0].end_time
        print event.where[0].value_string
        print event.content.text
        print event.author[0].name.text
        print event.author[0].email.text
        for attendee in event.who:
            print "attendees-->"
            print attendee.name
            print attendee.email
            print attendee.attendee_status.value
            print attendee.value
            print
        #print event
        print
            
    
        
    return

if __name__ == '__main__':
    main()
    
