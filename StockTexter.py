import TextServer as ts
import logging
import ScheduleServer as ss
import multiprocessing as mp
from time import sleep

logging.basicConfig()

if __name__ == '__main__':

    TextServer = ts.TextServer
    TServerP = mp.Process(target = TextServer.run, kwargs = \
                { 'debug' : True, 'host': '0.0.0.0' })

    ScheduleServer = ss.ScheduleServer()
    SServerP = mp.Process(target = ScheduleServer.run)


    TServerP.start()
    SServerP.start()
    while True:
	sleep(10)
        pass



