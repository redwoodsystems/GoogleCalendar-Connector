#Encapsulates calls to the Redwood Motion REST API
import httplib2
import json
import datetime, time, pytz
from django.utils import timezone

def call_motion_api(url,user,pwd,location_id):
    print "call_motion_api"
    uri_path = url+"/location/"+str(location_id)+"/sensorStats/motion/instant"
    #h = httplib2.Http(".cache",disable_ssl_certificate_validation=True)
    h = httplib2.Http(disable_ssl_certificate_validation=True)
    h.add_credentials(user, pwd)
    resp,content = h.request(uri_path,"GET", headers={'content-type':'application/json'})
    
    motion=0
    if resp and resp.has_key('status') and resp['status'] =='200':
        print "resp=",resp
        print "content=",content
        motion = parse_content(content)
        
    return int(motion)


def parse_content(content):
    return content


def parse_curr_location_fixtures(loc):
    fix_list = []
    if 'childFixture' in loc:
        for fx in loc['childFixture']:
            fix_list.append(fx.replace("/fixture/",""))
            
    return fix_list

def get_child_location_ids(loc):
    #Find child locations and obtain their fixtures
    loc_ids = []
    
    if 'childLocation' in loc:
        for l in loc['childLocation']:
            print l
            print l.replace("/location/","")
            loc_ids.append(int(l.replace("/location/","")))
            
    return loc_ids
            

def call_location_api(url,user,pwd,location_id):
    #return json for specified location
    
    uri_path = url+"/location/"+str(location_id)
    h = httplib2.Http(disable_ssl_certificate_validation=True)
    h.add_credentials(user, pwd)
    resp,content = h.request(uri_path,"GET", headers={'content-type':'application/json'})
    
    loc = None
    
    if resp and resp.has_key('status') and resp['status'] =='200':
        print "resp=",resp
        print "content=",content
        loc = json.loads(content)
        
    return loc


def get_location_fixtures2(loc, url,user,pwd,location_id):
    #return array of fixture names for a specific location and for child locations
    fix_list = []
    #obtain json for current location
    if not loc:
        loc = call_location_api(url,user,pwd,location_id)
    #get fixtures at current level
    fix_list.extend(parse_curr_location_fixtures(loc))
    #check if we have child locations
    ch_loc_ids = get_child_location_ids(loc)
    
    #obtain fixtures for each child locations
    #we assume that locations are only 2 levels (so need for recursion)
    for ch_loc_id in ch_loc_ids:
        ch_loc = call_location_api(url,user,pwd,ch_loc_id)
        fix_list.extend(parse_curr_location_fixtures(ch_loc))
        
    return fix_list

def get_motion_instant(loc):
    motion = -1
    if "sensorStats" in loc and "motion" in loc["sensorStats"]:
            instant = loc["sensorStats"]["motion"]["instant"]
            if instant:
                motion = int(instant)
    return motion
    
        

def get_occupancy(url,user,pwd,location_id, current_time, occ_threshold):
    # TODO: Combine motion instant and occupancy pct methods
    #
    # Build array of fixture ids from location
    # Find number of fixtures from location
    # For each fixture:
    #    Find motion instant
    # 
    
    print "get_occupancy"
    
    motion = 0
    occupied_pct = None
    
    loc = call_location_api(url,user,pwd,location_id)
    
    fix_list = get_location_fixtures2(loc,url,user,pwd,location_id)
    
    motion = get_motion_instant(loc)
        
    motion_list = []
    
    if len(fix_list) >0:
        #we found some fixtures under this location
        #obtain motion instants for each fixture in the list
        motion_list = call_fixture_motion_api(url,user,pwd,fix_list)
        print "motion_list=",motion_list
        
        #obtain occupancy for each fixture
        cnt_occupied = 0;
        for m in motion_list:
            if not m["dt"]:
                m["dt"] = current_time
            vacant_secs = get_pos_time_diff_secs(current_time, m["dt"])
            print "fx vacant_secs=",vacant_secs
            
            if vacant_secs <= occ_threshold:
                cnt_occupied = cnt_occupied +1
        
        occupied_pct =  (cnt_occupied * 100)/len(fix_list)
        print "location_id: %d num_fixtures: %d cnt_occupied: %d occupied pct: %f"%(location_id,
                                                                                    len(fix_list), cnt_occupied, occupied_pct)
            
    return (occupied_pct, motion)
                    
                    
    
def call_fixture_motion_api(url,user,pwd,filter_list):
    #return array of fixtures and motion instants filtered by fixture list
    print "call_fixture_motion_api"
    ret_list=[]
    
    uri_path = url+"/fixture"
    h = httplib2.Http(disable_ssl_certificate_validation=True)
    h.add_credentials(user, pwd)
    resp,content = h.request(uri_path,"GET", headers={'content-type':'application/json'})
    
    if resp and resp.has_key('status') and resp['status'] =='200':
        print "resp=",resp
        #print "content=",content
        
        fx_arr = json.loads(content)
        
        if not fx_arr or len(fx_arr) ==0:
            return None
        
        all_fixtures = {}
        for fx in fx_arr:
            all_fixtures[fx["serialNum"]] = fx
        
        for fname in filter_list:
            print fname
            if fname in all_fixtures:
                print fname+" found"
                fx = all_fixtures[fname]
                if "sensorStats" in fx and "motion" in fx["sensorStats"]:
                    print fx
                    instant = fx["sensorStats"]["motion"]["instant"]
                    dt = datetime.datetime.utcfromtimestamp(instant).replace(tzinfo=pytz.timezone('utc'))
                    ret_list.append({"fixtureName":fx["serialNum"],
                                     "instant": instant,
                                     "dt":dt })
                    
    return ret_list
                
def get_pos_time_diff_secs(dt1, dt2):
    #Assumes that both dates are timzone aware and stored in UTC
    diff = dt1 - dt2
    if diff.days >=0:
        return diff.seconds
    else:
        return 0
    


def main():
    
    current_time = timezone.now()
    get_occupancy('https://yyyyyy.xxxxxxxx.com:26443/rApi', "admin", "password", 101, current_time, 300)
    
    return

if __name__ == '__main__':
    main()
