from __future__ import print_function
import json
import os
import subprocess
import select
from threading import Thread


KSPHOME = '../kerbal/KSP_linux'
GAMEOUT = '/tmp/gamepipe.out'
GAMEIN = '/tmp/gamepipe.in'



class KSPDeepEngine:
    def __init__(self):
        if not os.path.exists(GAMEIN):
            os.mkfifo(GAMEIN, 0o777)
        if not os.path.exists(GAMEOUT):
            os.mkfifo(GAMEOUT, 0o777)


        while True:
            with open(GAMEOUT) as fifo:
                line = fifo.read()
                print(json.loads(line))


class FifoPipeThread(Thread):
    def __init__(self, path, write = False):
        Thread.__init__(self)
        self.path = path
        self.write = write

    def run(self):
        if not os.path.exists(self.path):
            os.mkfifo(self.path, 0o777)

        flags = os.O_RDONLY
        if self.write:
            flags = os.O_WRONLY
        print('open pipe')

        with open(self.path) as fifo:
            #while True:
            line = fifo.read()
            print(line)



KSPDeepEngine()




