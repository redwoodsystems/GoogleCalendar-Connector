#Encapsulates calles to the Redwood Motion REST API
import httplib2
import json
import datetime, time, pytz
from django.utils import timezone


def call_root_api(url,user,pwd):
    #return json for specified location
    
    uri_path = url
    h = httplib2.Http(disable_ssl_certificate_validation=True)
    h.add_credentials(user, pwd)
    resp,content = h.request(uri_path,"GET", headers={'content-type':'application/json'})
    
    root = None
    if resp and resp.has_key('status') and resp['status'] =='200':
        #print "resp=",resp
        #print "content=",content
        root = json.loads(content)
        
    return root


def get_location(root, location_id):
    #get location from root json
    locations = root['location']
    for loc in locations:
        if loc['id'] == location_id:
            return loc
        
    return None

def get_fixture(root, serial_num):
    #get fixture from root json
    fixtures = root['fixture']
    for fx in fixtures:
        if fx['serialNum'] == serial_num:
            return fx
        
    return None
    


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
            loc_ids.append(int(l.replace("/location/","")))
            
    return loc_ids


def get_fixture_motion(fixtures, filter_list):
    #return array of fixtures and motion instants filtered by fixture list
    #print "get_fixture_motion"
    ret_list=[]
    
    if not fixtures or len(fixtures) ==0:
        return None
    
    if not filter_list or len(filter_list) == 0:
        return None
    
    fix_dict = {}
    for fx in fixtures:
        fix_dict[fx["serialNum"]] = fx
    
    for fname in filter_list:
        print fname
        if fname in fix_dict:
            #print fname+" found"
            fx = fix_dict[fname]
            if "sensorStats" in fx and "motion" in fx["sensorStats"] and "instant" in fx["sensorStats"]["motion"]:
                print fx
                instant = fx["sensorStats"]["motion"]["instant"]
                dt = datetime.datetime.utcfromtimestamp(instant).replace(tzinfo=pytz.timezone('utc'))
                ret_list.append({"fixtureName":fx["serialNum"],
                                 "instant": instant,
                                 "dt":dt })
                    
    return ret_list
            

def get_motion_instant(loc):
    motion = -1
    if "sensorStats" in loc and "motion" in loc["sensorStats"] and "instant" in loc["sensorStats"]["motion"]:
            instant = loc["sensorStats"]["motion"]["instant"]
            if instant:
                motion = int(instant)
    return motion
    
        

def get_occupancy(url,user,pwd,location_id, current_time, occ_threshold):
    print "get_occupancy"
    
    motion = 0
    occupied_pct = None
    
    #download root json and cache
    root = call_root_api(url,user,pwd)
    
    loc = get_location(root, location_id)
    #get motion for current location
    motion = get_motion_instant(loc)
    
    #get array of fixtures
    all_fixtures = root['fixture']
    
    #fixture numbers for current location 
    fix_list = parse_curr_location_fixtures(loc)

    #get fixtures for child locations    
    ch_loc_ids = get_child_location_ids(loc)
    for ch_loc_id in ch_loc_ids:
        ch_loc = get_location(root, ch_loc_id) 
        fix_list.extend(parse_curr_location_fixtures(ch_loc))
        
    motion_list = []
    if len(fix_list) >0:
        #we found some fixtures under this location
        #obtain motion instants for each fixture in the list
        motion_list = get_fixture_motion(all_fixtures, fix_list)
        
        print "motion_list=",motion_list
        #obtain occupancy for each fixture
        cnt_occupied = 0;
        for m in motion_list:
            if not m["dt"]:
                m["dt"] = current_time
            vacant_secs = get_pos_time_diff_secs(current_time, m["dt"])
            #print "fx vacant_secs=",vacant_secs
            
            if vacant_secs <= occ_threshold:
                cnt_occupied = cnt_occupied +1
        
        occupied_pct =  (cnt_occupied * 100)/len(fix_list)
        print "location_id: %d num_fixtures: %d cnt_occupied: %d occupied pct: %f"%(location_id,
                                                                                    len(fix_list), cnt_occupied, occupied_pct)
            
    return (occupied_pct, motion)
                    
                    
                
def get_pos_time_diff_secs(dt1, dt2):
    #Assumes that both dates are timzone aware and stored in UTC
    diff = dt1 - dt2
    if diff.days >=0:
        return diff.seconds
    else:
        return 0


def main():
    
    #2.1 url
    #call_motion_api('https://ec2-23-20-243-84.compute-1.amazonaws.com/rApi','admin','redwood',101)
    #old url
    #call_motion_api('https://ec2-107-20-58-179.compute-1.amazonaws.com/rApi','admin','redwood',101)
    
    current_time = timezone.now()
    get_occupancy('https://hq.redwoodsys.com:26443/rApi', "admin", "redwood", 101, current_time, 300)
    
    return

if __name__ == '__main__':
    main()