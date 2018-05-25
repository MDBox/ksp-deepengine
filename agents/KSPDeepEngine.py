from __future__ import print_function
import json
import os
import subprocess
import threading
from threading import Thread

KSPHOME = '../kerbal/KSP_linux'
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

        with subprocess.Popen(["/home/michael/dev/ksp-deepengine/kerbal/KSP_linux/KSP.x86_64"], stdout=None) as proc:
            print(proc.stdout.read())



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
                line = fifo.read()
                print('MESSAGE IN: ', line)
                self.game.inmessage.add(line)


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
                message = self.game.outmessage.getAll()
                if len(message) > 0:
                    print('MESSAGE OUT: ', message)
                    fifo.write(message[0])
                    fifo.flush()


game = KSPDeepEngine()

