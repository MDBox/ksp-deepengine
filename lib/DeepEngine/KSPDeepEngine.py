from __future__ import print_function
from json import JSONEncoder
import numpy as np
import json
import os
import time
import math

GAMECHALLENGE1 = "../Plugins/deep_engine/challenge1/"

GAMEOUT = '/tmp/gamepipe.out'
GAMEIN = '/tmp/gamepipe.in'

# Vessel keys and value types
#
# INPUTFILTER = {}
# INPUTFILTER['currentStage'] = 'int'
# INPUTFILTER['srfRelRotation'] = 'vector'
# INPUTFILTER['longitude'] = 'float'
# INPUTFILTER['latitude'] = 'float'
# INPUTFILTER['altitude'] = 'float'
# INPUTFILTER['radarAltitude'] = 'float'
# INPUTFILTER['distanceTraveled'] = 'float'
# INPUTFILTER['vesselSize'] = 'vector'
# INPUTFILTER['state'] = 'int'
# INPUTFILTER['situation'] = 'int'
# INPUTFILTER['missionTime'] = 'float'
# INPUTFILTER['launchTime'] = 'float'
# INPUTFILTER['obt_velocity'] = 'vector'
# INPUTFILTER['srf_velocity'] = 'vector'
# INPUTFILTER['srf_vel_direction'] = 'vector'
# INPUTFILTER['rb_velocity'] = 'vector'
# INPUTFILTER['velocityD'] = 'vector'
# INPUTFILTER['obt_speed'] = 'float'
# INPUTFILTER['acceleration'] = 'vector'
# INPUTFILTER['acceleration_immediate'] = 'vector'
# INPUTFILTER['perturbation'] = 'vector'
# INPUTFILTER['perturbation_immediate'] = 'vector'
# INPUTFILTER['specificAcceleration'] = 'float'
# INPUTFILTER['upAxis'] = 'vector'
# INPUTFILTER['CoM'] = 'vector'
# INPUTFILTER['MoI'] = 'vector'
# INPUTFILTER['angularVelocity'] = 'vector'
# INPUTFILTER['angularMomentum'] = 'vector'
# INPUTFILTER['geeForce'] = 'float'
# INPUTFILTER['geeForce_immediate'] = 'float'
# INPUTFILTER['gravityMultiplier'] = 'float'
# INPUTFILTER['graviticAcceleration'] = 'vector'
# INPUTFILTER['gravityForPos'] = 'vector'
# INPUTFILTER['gravityTrue'] = 'vector'
# INPUTFILTER['verticalSpeed'] = 'float'
# INPUTFILTER['horizontalSrfSpeed'] = 'float'
# INPUTFILTER['srfSpeed'] = 'float'
# INPUTFILTER['indicatedAirSpeed'] = 'float'
# INPUTFILTER['mach'] = 'float'
# INPUTFILTER['speed'] = 'float'
# INPUTFILTER['externalTemperature'] = 'float'
# INPUTFILTER['atmosphericTemperature'] = 'float'
# INPUTFILTER['staticPressurekPa'] = 'float'
# INPUTFILTER['dynamicPressurekPa'] = 'float'
# INPUTFILTER['atmDensity'] = 'float'
# INPUTFILTER['up'] = 'vector'
# INPUTFILTER['north'] = 'vector'
# INPUTFILTER['east'] = 'vector'
# INPUTFILTER['totalMass'] = 'float'
# INPUTFILTER['heightFromTerrain'] = 'float'
# INPUTFILTER['terrainAltitude'] = 'float'
# INPUTFILTER['pqsAltitude'] = 'float'
# INPUTFILTER['localCoM'] = 'vector'

class KSPAction(object):
    FLIGHTCTRL   = 0
    STAGING      = 1
    RESETGAME    = 2
    CRASHED      = 3
    STATEONLY    = 4
    LOADGAME     = 5
    
    def __init__(self):
        self.action = KSPAction.FLIGHTCTRL
        self.flightCtrlState = FlightCtrl()
        self.gamepath = GAMECHALLENGE1
        
    def toJSON(self):
        obj = {}
        obj['action'] = self.action
        obj['flightCtrlState'] = self.flightCtrlState.toJSON()
        obj['gamepath'] = self.gamepath
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
        self.starttime = time.time()
            
    def new_episode(self):
        action = KSPAction()
        action.action = KSPAction.RESETGAME
        self.get_state(action)
        time.sleep(15)
        self.starttime = time.time()
        
    def parseFlightControls(self, flightControl):
        values = []
        for key in flightControl:
            if type(flightControl[key]) is float:
                values.append((flightControl[key] + 1) / 2)
            if type(flightControl[key]) is bool:
                values.append(int(flightControl[key] == 'true'))
        return values
    
    def get_state(self, action = None):
        if not action:
            action = KSPAction()
            action.action = KSPAction.STATEONLY
        
        with open(GAMEIN, 'w', encoding='utf-8-sig') as w:
            w.write(action.toJSON()+'\n')
            w.flush()
            w.close()
        
        with open(GAMEOUT, 'r', encoding='utf-8-sig') as fifo:
            line = fifo.read()
        
        message = json.loads(line)
        vessel = json.loads(message['vessel'])
        flightCtrlState = json.loads(message['flightCtrlState'])
        state = self.parseFlightControls(flightCtrlState)
        
        action.action = message['action']
        action.vessel = vessel
        action.flightCtrlState = FlightCtrl(**flightCtrlState)
                 
        return action, state


if __name__ == '__main__':
    game = KSPDeepEngine()
    
    action = KSPAction()
    action.action = KSPAction.STATEONLY
    
    print(game.get_state(action))
    
    

    
