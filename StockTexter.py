import TextServer as ts
import ScheduleServer as ss
import multiprocessing as mp

if __name__ == '__main__':

    TextServer = ts.TextServer
    TServerP = mp.Process(target = TextServer.run, kwargs = \
                { 'debug' : True, 'host': '0.0.0.0' })

    ScheduleServer = ss.ScheduleServer()
    SServerP = mp.Process(target = ScheduleServer.run)
    
    TServerP.start()
    SServerP.start()



