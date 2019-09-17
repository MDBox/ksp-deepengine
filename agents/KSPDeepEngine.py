from __future__ import print_function
from json import JSONEncoder
import numpy as np
import json
import os
import time


GAMEOUT = '/home/michael/projects/ksp-deepengine/gamepipe.out'
GAMEIN = '/home/michael/projects/ksp-deepengine/gamepipe.in'

INPUTFILTER = {}
INPUTFILTER['currentStage'] = 'int'
INPUTFILTER['srfRelRotation'] = 'vector'
INPUTFILTER['longitude'] = 'float'
INPUTFILTER['latitude'] = 'float'
INPUTFILTER['altitude'] = 'float'
INPUTFILTER['radarAltitude'] = 'float'
INPUTFILTER['distanceTraveled'] = 'float'
INPUTFILTER['vesselSize'] = 'vector'
INPUTFILTER['state'] = 'int'
INPUTFILTER['situation'] = 'int'
INPUTFILTER['missionTime'] = 'float'
INPUTFILTER['launchTime'] = 'float'
INPUTFILTER['obt_velocity'] = 'vector'
INPUTFILTER['srf_velocity'] = 'vector'
INPUTFILTER['srf_vel_direction'] = 'vector'
INPUTFILTER['rb_velocity'] = 'vector'
INPUTFILTER['velocityD'] = 'vector'
INPUTFILTER['obt_speed'] = 'float'
INPUTFILTER['acceleration'] = 'vector'
INPUTFILTER['acceleration_immediate'] = 'vector'
INPUTFILTER['perturbation'] = 'vector'
INPUTFILTER['perturbation_immediate'] = 'vector'
INPUTFILTER['specificAcceleration'] = 'float'
INPUTFILTER['upAxis'] = 'vector'
INPUTFILTER['CoM'] = 'vector'
INPUTFILTER['MoI'] = 'vector'
INPUTFILTER['angularVelocity'] = 'vector'
INPUTFILTER['angularMomentum'] = 'vector'
INPUTFILTER['geeForce'] = 'float'
INPUTFILTER['geeForce_immediate'] = 'float'
INPUTFILTER['gravityMultiplier'] = 'float'
INPUTFILTER['graviticAcceleration'] = 'vector'
INPUTFILTER['gravityForPos'] = 'vector'
INPUTFILTER['gravityTrue'] = 'vector'
INPUTFILTER['verticalSpeed'] = 'float'
INPUTFILTER['horizontalSrfSpeed'] = 'float'
INPUTFILTER['srfSpeed'] = 'float'
INPUTFILTER['indicatedAirSpeed'] = 'float'
INPUTFILTER['mach'] = 'float'
INPUTFILTER['speed'] = 'float'
INPUTFILTER['externalTemperature'] = 'float'
INPUTFILTER['atmosphericTemperature'] = 'float'
INPUTFILTER['staticPressurekPa'] = 'float'
INPUTFILTER['dynamicPressurekPa'] = 'float'
INPUTFILTER['atmDensity'] = 'float'
INPUTFILTER['up'] = 'vector'
INPUTFILTER['north'] = 'vector'
INPUTFILTER['east'] = 'vector'
INPUTFILTER['totalMass'] = 'float'
INPUTFILTER['heightFromTerrain'] = 'float'
INPUTFILTER['terrainAltitude'] = 'float'
INPUTFILTER['pqsAltitude'] = 'float'
INPUTFILTER['localCoM'] = 'vector'

class KSPAction(object):        
    def __init__(self):
        self.action = 0;
        self.flightCtrlState = FlightCtrl()
        
    def toJSON(self):
        obj = {}
        obj['action'] = self.action
        obj['flightCtrlState'] = self.flightCtrlState.toJSON()
        return json.dumps(obj)
    
    def toArray(self):
        obj = []
        obj.append(self.action)
        obj.append(self.flightCtrlState.mainThrottle)
        obj.append(self.flightCtrlState.roll)
        obj.append(self.flightCtrlState.yaw)
        obj.append(self.flightCtrlState.pitch)
        return obj
        

class FlightCtrl(object):
    def __init__(self, **entries):
        self.mainThrottle = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        self.pitch = 0.0
        self.rollTrim = 0.0
        self.yawTrim = 0.0
        self.pitchTrim = 0.0
        self.wheelSteer = 0.0
        self.wheelSteerTrim = 0.0
        self.wheelThrottle = 0.0
        self.gearDown = True
        self.headlight = False
        self.__dict__.update(entries)
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
                
class KSPDeepEngine:
    def __init__(self):
        if not os.path.exists(GAMEIN):
            os.mkfifo(GAMEIN, 0o777)
        if not os.path.exists(GAMEOUT):
            os.mkfifo(GAMEOUT, 0o777)
        
        self.start = time.time()
        self.lastAltitude = 0

            
    def parseVector3(self, vector3):
        return [vector3['x'], vector3['y'], vector3['z']]
            
    def parseVessel(self, vessel):
        values = []
        for k in vessel:
            if k in INPUTFILTER:
                if INPUTFILTER[k] == 'int':
                    values.append([vessel[k],vessel[k],vessel[k]])
                if INPUTFILTER[k] == 'float':
                    values.append([vessel[k],vessel[k],vessel[k]])
                if INPUTFILTER[k] == 'vector':
                    values.extend([self.parseVector3(vessel[k])])            
        return values
    
    def parseFlightControls(self, flightControl):
        values = []
        for k in flightControl:
            if type(flightControl[k]) == 'float':
                values.append(flightControl[k])
            if type(flightControl[k]) == 'bool':
                values.append(int(flightControl[k] == 'true'))
                
        return values
    
    def new_episode(self):
        action = KSPAction()
        action.action = 2
        self.get_state(action)
        time.sleep(15)
        self.start = time.time()
    
    def get_state(self, action = None):
        if not action:
            action = KSPAction()
        done = False
        
        with open(GAMEIN, 'w', encoding='utf-8-sig') as w:
            w.write(action.toJSON()+'\n')
            w.flush()
            w.close()
        
        with open(GAMEOUT, 'r', encoding='utf-8-sig') as fifo:
            line = fifo.read()
        
        message = json.loads(line)
        vessel = json.loads(message['vessel'])
        flightCtrlState = json.loads(message['flightCtrlState'])
        state = self.parseVessel(vessel)
        state.extend(self.parseFlightControls(flightCtrlState))
        
        reward = int(vessel['altitude'])
        if message['action'] == 3: # Action 3 means ship crashed
            reward -= 100000
            done = True
            
        if vessel['situation'] == 5: # situation 5 means we reach a stable orbet
            reward += 100000
            done = True
        
        if int(vessel['altitude']) != self.lastAltitude:
            self.start = time.time()
        
        self.lastAltitude = int(vessel['altitude'])
        
        currentTime = time.time()
        if (currentTime - self.start) > 20:
            reward -= 100000
            done = True
                 
        return np.array(state, dtype='f'), reward, done, vessel, FlightCtrl(**flightCtrlState)


if __name__ == '__main__':
    game = KSPDeepEngine()
    
    action = KSPAction()
    action.action = 2
    
    print(game.get_state(action))
    
    

    
