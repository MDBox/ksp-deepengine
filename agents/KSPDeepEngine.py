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
            with open(GAMEOUT, 'r', encoding='utf-8-sig') as fifo:
                try:
                    line = fifo.read()
                    state = json.loads(line)
                    state['vessel'] = json.loads(state['vessel'])
                    #state['flightCtrlState'] = json.loads(state['flightCtrlState'])
                    self.game.inmessage.add(state)
                except Exception as e:
                    pass
                    #print(str(e))



class FifoOutPipeThread(Thread):
    def __init__(self, game):
        Thread.__init__(self)
        self.daemon = False
        self.game = game

    def run(self):
        if not os.path.exists(GAMEIN):
            os.mkfifo(GAMEIN, 0o777)
            
        
        while True:
            with open(GAMEIN, 'w', encoding='utf-8-sig') as fifo:

                message = self.game.outmessage.getAll(blocking=False)
                if len(message) > 0:
                    print('MESSAGE OUT: ', message[-1])
                    fifo.write(message[-1]+'\n')
                    

if __name__ == '__main__':
    game = KSPDeepEngine()
