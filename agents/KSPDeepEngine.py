from __future__ import print_function
from json import JSONEncoder
import numpy as np
import json
import os

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

class KSPAction:
    def __init__(self):
        self.action = 0;
        self.flightCtrlState = FlightCtrl()
        
    def toJSON(self):
        obj = {}
        obj['action'] = self.action
        obj['flightCtrlState'] = self.flightCtrlState.toJSON()
        return json.dumps(obj)

class FlightCtrl:
    def __init__(self):
        self.mainThrottle = 1.0
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
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
        
            
class KSPDeepEngine:
    def __init__(self):
        if not os.path.exists(GAMEIN):
            os.mkfifo(GAMEIN, 0o777)
        if not os.path.exists(GAMEOUT):
            os.mkfifo(GAMEOUT, 0o777)
            
    def parseVector3(self, vector3):
        return [vector3['x'], vector3['y'], vector3['z']]
            
    def parseVessel(self, vessel):
        values = []
        for k in vessel:
            if k in INPUTFILTER:
                if INPUTFILTER[k] == 'int':
                    values.append(vessel[k])
                if INPUTFILTER[k] == 'float':
                    values.append(vessel[k])
                if INPUTFILTER[k] == 'vector':
                    values.extend(self.parseVector3(vessel[k]))            
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
        self.getEnvironmentState(action)
    
    def get_state(self, action = None):
#         if not action:
#             action = KSPAction()
        
        with open(GAMEIN, 'w', encoding='utf-8-sig') as w:
            w.write(action.toJSON()+'\n')
            w.flush()
            w.close()
        
        with open(GAMEOUT, 'r', encoding='utf-8-sig') as fifo:
            line = fifo.read()
        
        state = json.loads(line)
        vessel = json.loads(state['vessel'])
        fc = json.loads(state['flightCtrlState'])
        state['environment'] = self.parseVessel(vessel)
        state['environment'].extend(self.parseFlightControls(fc))
        state['state'] = vessel['state']
                 
        return np.array(state['environment'], dtype='f'), vessel['state'], fc


if __name__ == '__main__':
    game = KSPDeepEngine()
    
    action = KSPAction()
    action.action = 1
    
    array, state, fc = game.get_state(action)
    
    print(array.shape, state, fc)

    
