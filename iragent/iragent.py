#!python3

from urllib.error import URLError
from urllib.request import Request, urlopen
from datetime import datetime, timedelta
import argparse
import irsdk
import json
import time
import traceback

parser = argparse.ArgumentParser()
parser.add_argument("--url", "-u", help="server API URL", required=True)
parser.add_argument("--int", "-i", help="telemetry polling interval", type=int, default=3)
parser.add_argument("--avg", "-a", help="# of laps for calculating averages", type=int, default=1000)
parser.add_argument("--data", "-d", help="telemetry test file", default=None)
args = parser.parse_args()

server_url = args.url + '/api/telemetry'
polling_interval = args.int
data_source = args.data
print(f"Sending telemetry data to {server_url} every {polling_interval} seconds.")

# this is our State class, with some helpful variables
class State:
    ir_connected = False

    def __init__(self):
        self.reset()

    def reset(self):
        self.last_car_setup_tick = -1
        self.laps = []
        self.last_lap = 0
        self.last_laps_complete = 0
        self.last_lap_fuel_level = 0
        self.session_num = None

# here we check if we are connected to iracing
# so we can retrieve some data
def check_iracing():
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        # don't forget to reset your State variables
        state.reset()
        # we are shutting down ir library (clearing all internal variables)
        ir.shutdown()
        print('irsdk disconnected')
    elif not state.ir_connected and ir.startup(test_file=data_source) and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
        print('irsdk connected')

def track_lap_data(result):
    last_lap = result["Lap"]
    last_laps_complete = result["LapsComplete"]
    # detect new lap
    # https://members.iracing.com/jforum/posts/list/1700/1470675.page#9182663
    # https://members.iracing.com/jforum/posts/list/1332280.page#2858801
    if last_lap != state.last_lap or last_laps_complete != state.last_laps_complete:
        print(f"lap: {last_lap}|{state.last_lap}, completed: {last_laps_complete}|{state.last_laps_complete}")
        # store lap data
        lap_time = result["LastTime"]
        is_valid = False
        if lap_time > 0:
            is_valid = True
        lap = {
            'lap': last_lap,
            'time': lap_time,
            'valid': is_valid,
            'fuel_used': state.last_lap_fuel_level - ir['FuelLevel']
        }
        state.laps.append(lap)
        state.last_lap = last_lap
        state.last_laps_complete = last_laps_complete
        state.last_lap_fuel_level = ir['FuelLevel']
        print(f"new lap added: {lap}")

def send_to_server(data):
    postdata = json.dumps(data).encode()
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    request = Request(server_url, data=postdata, method="POST", headers=headers)
    try:
        with urlopen(request) as response:
            pass
    except URLError as e:
        if hasattr(e, 'reason'):
            print('Error communicating with server.')
            print('Reason: ', e.reason)
        elif hasattr(e, 'code'):
            print('Server failed to fulfill request.')
            print('Error code: ', e.code)

def seconds_to_time_clock(s):
    delta = timedelta(seconds=s)
    return str(delta - timedelta(microseconds=delta.microseconds))

def seconds_to_time_lap(s):
    dt = datetime.utcfromtimestamp(s)
    return '%s.%03d'%(dt.strftime("%M:%S"), int(dt.microsecond/1000))

def split_and_strip(l):
    return [x.strip() for x in l.split(',')]

# our main loop, where we retrieve data
# and do something useful with it
def loop():

    # freeze the buffer with live telemetry
    ir.freeze_var_buffer_latest()

    # check for new session
    if state.session_num != ir['SessionNum']:
        print(f"new session detected: {ir['SessionNum']}")
        # reset state for new session
        state.reset()
        state.session_num = ir['SessionNum']
        state.last_lap_fuel_level = ir['FuelLevel']

    # resolve relevant property arrays from telemetry
    driver = next(d for d in ir['DriverInfo']['Drivers'] if d['CarIdx'] == ir['DriverInfo']['DriverCarIdx'])
    session = next(s for s in ir['SessionInfo']['Sessions'] if s['SessionNum'] == ir['SessionNum'])
    result = next(r for r in session["ResultsPositions"] if r['CarIdx'] == ir["DriverInfo"]["DriverCarIdx"])

    # update lap data
    # must happen after the result property array has set
    track_lap_data(result)

    # calculate additional telemetry properties
    team_id = f"{ir['WeekendInfo']['SessionID']}-{ir['WeekendInfo']['SubSessionID']}-{ir['DriverInfo']['DriverCarIdx']}"
    valid_laps = [lap for lap in state.laps if lap['valid']][-(args.avg):]
    lap_time_avg = sum([lap['time'] for lap in valid_laps]) / len(valid_laps) if valid_laps else 0
    time_laps_remain = ir['SessionTimeRemain'] / lap_time_avg if lap_time_avg else 0
    fuel_burn_avg = sum([i['fuel_used'] for i in valid_laps]) / len(valid_laps)
    fuel_laps_remain = ir['FuelLevel'] / fuel_burn_avg if fuel_burn_avg else 0
    fuel_time_remain = fuel_laps_remain * lap_time_avg

    # build the data object for the server
    data = {
        'car': {
            'id': team_id,
            'number': driver['CarNumber'],
            'class': driver['CarClassShortName'] or driver['CarScreenName'],
            'class_position': ir['PlayerCarClassPosition'],
            'incident_count': driver['TeamIncidentCount']
        },
        'driver': {
            'id': driver['UserID'],
            'name': driver['UserName'],
            'active': False if driver['IsSpectator'] else True,
            'incident_count': driver['CurDriverIncidentCount']
        },
        'session': {
            'event': ir['WeekendInfo']['TrackDisplayName'],
            'type': session['SessionType'],
            'time_remain': seconds_to_time_clock(ir['SessionTimeRemain'])
        },
        'telemetry': {
            'laps_completed': result['LapsComplete'],
            'avg_lap_time': seconds_to_time_lap(lap_time_avg),
            'last_lap_time': seconds_to_time_lap(result['LastTime']),
            'best_lap_time': seconds_to_time_lap(result['FastestTime']),
            'time_laps_remain': '{:.2f}'.format(time_laps_remain),
            'fuel_remain': '{:.2f} L'.format(ir['FuelLevel']),
            'fuel_burn_avg': '{:.3f} L/Lap'.format(fuel_burn_avg),
            'fuel_laps_remain': '{:.2f} Laps'.format(fuel_laps_remain),
            'fuel_time_remain': seconds_to_time_clock(fuel_time_remain).split('.')[0],
            'tire_wear': {
                'fl': [round(ir['LFwearL'], 2), round(ir['LFwearM'], 2), round(ir['LFwearR'], 2)],
                'fr': [round(ir['RFwearL'], 2), round(ir['RFwearM'], 2), round(ir['RFwearR'], 2)],
                'rl': [round(ir['LRwearL'], 2), round(ir['LRwearM'], 2), round(ir['LRwearR'], 2)],
                'rr': [round(ir['RRwearL'], 2), round(ir['RRwearM'], 2), round(ir['RRwearR'], 2)]
            }
        }
    }

    # send the data to the server
    send_to_server(data)

if __name__ == '__main__':
    # initializing ir and state
    ir = irsdk.IRSDK()
    state = State()

    # infinite loop
    while True:
        try:
            # check if we are connected to iracing
            check_iracing()
            # if we are, then process data
            if state.ir_connected:
                loop()
            else:
                print('iRacing telemetry not available')
            # sleep for N seconds
            # maximum you can use is 1/60
            # because iracing updates data with 60 fps
            time.sleep(polling_interval)
        except KeyboardInterrupt:
            # press ctrl+c to exit
            break
        except:
            traceback.print_exc()
