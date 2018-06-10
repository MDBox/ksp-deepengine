from __future__ import print_function
import json
import os
import subprocess
import threading
from threading import Thread

KSPHOME = '/home/michael/dev/ksp-deepengine/kerbal/KSP_linux'
GAMEOUT = '/tmp/gamepipe.out'
GAMEIN = '/tmp/gamepipe.in'

class ItemStore(object):
    def __init__(self):
        self.cond = threading.Condition()
        self.items = []

    def add(self, item):
        with self.cond:
            self.items.append(item)
            self.cond.notify()

    def getAll(self, blocking=False):
        with self.cond:
            while blocking and len(self.items) == 0:
                self.cond.wait()
            items, self.items = self.items, []
        return items

    
class FlightCtrl:
    def __init__(self):
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
            
class KSPDeepEngine:
    def __init__(self):
        self.inmessage = ItemStore()
        self.outmessage = ItemStore()
        if not os.path.exists(GAMEIN):
            os.mkfifo(GAMEIN, 0o777)
        if not os.path.exists(GAMEOUT):
            os.mkfifo(GAMEOUT, 0o777)

        thread1 = FifoReadPipeThread(self)
        thread1.start()

        thread2 = FifoOutPipeThread(self)
        thread2.start()

        subprocess.Popen([KSPHOME+"/KSP.x86_64"], stdout=None)

    def getLastState(self):
        return self.inmessage.getAll(blocking=True)[-1]

    def getAllQueuedStates(self):
        return self.inmessage.getAll()

    def sendAcation(self, action):
        #print(action)
        self.outmessage.add(action)


class FifoReadPipeThread(Thread):
    def __init__(self, game):
        Thread.__init__(self)
        self.daemon = False
        self.game = game

    def run(self):
        if not os.path.exists(GAMEOUT):
            os.mkfifo(GAMEOUT, 0o777)

        while True:
            try:
                with open(GAMEOUT, 'r', encoding='utf-8-sig') as fifo:
                    try:
                        line = fifo.read()
                        state = json.loads(line)
                        state['vessel'] = json.loads(state['vessel'])
                        state['flightCtrlState'] = json.loads(state['flightCtrlState'])
                        self.game.inmessage.add(state)
                    except Exception as e:
                        pass
                        #print(str(e))
            except Exception as e:
                print(str(e))



class FifoOutPipeThread(Thread):
    def __init__(self, game):
        Thread.__init__(self)
        self.daemon = False
        self.game = game

    def run(self):
        if not os.path.exists(GAMEIN):
            os.mkfifo(GAMEIN, 0o777)

        try:
            while True:
                message = self.game.outmessage.getAll(blocking=True)
                outmessage = {'action': 5}
                if len(message) > 0:
                    outmessage = message[-1]
                    outmessage['vessel'] = json.dumps(outmessage['vessel'])
                    outmessage['flightCtrlState'] = json.dumps(outmessage['flightCtrlState'])
                with open(GAMEIN, 'w', encoding='utf-8-sig') as fifo:
                    #print(message)
                    fifo.write(json.dumps(outmessage)+'\n')
                    fifo.flush()
                    fifo.close()
        except Exception as e:
            print(str(e))


if __name__ == '__main__':
    game = KSPDeepEngine()
