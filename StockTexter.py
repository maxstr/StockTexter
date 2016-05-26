import TextServer as ts
import logging
from pubsub import pub
import ScheduleServer as ss
import multiprocessing as mp
from time import sleep

logging.basicConfig()

if __name__ == '__main__':

    TextServer = ts.TextServer
    TServerP = mp.Process(target = TextServer.run, kwargs = \
                { 'debug' : True, 'host': '0.0.0.0' , 'use_reloader' : False})

    ScheduleServer = ss.ScheduleServer()
    ScheduleServer.run()
    pub.subscribe(ScheduleServer.addToSchedule, 'addToSchedule')

    
    TServerP.start()
    while True:
	sleep(100)
	print ScheduleServer.scheduler.get_jobs()
        pass



