from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import StockGrabber as sg
from twilio.rest import TwilioRestClient
import TwilioFunctions as tf
import redis
from time import sleep
import json

TWILIO_ACCOUNT_SID = "***REMOVED***"
TWILIO_AUTH_TOKEN = "***REMOVED***"
SENDING_NUMBER = "+18052044765"



class ScheduleServer:

    def __init__(self
                , sqlite = None \
                , redisConfig = {'host':'localhost', 'port':6379, 'db':0} \
                , topic = 'schedulerMessage'):

        self.scheduler = BackgroundScheduler()
        if sqlite:
		self.scheduler.add_jobstore('sqlalchemy', url=sqlite)

        self.redisHandle = redis.StrictRedis(**redisConfig)
        self.pub = self.redisHandle.pubsub()

        # mapping of message keys => function to handle them
        self.messageHandles = \
                { 'addToSchedule' : self.addToSchedule \
                , 'removeFromSchedule' : self.removeFromSchedule }
        self.listenTopic = topic
        self.pub.subscribe(topic)

    def removeFromSchedule(self, phoneNumberString):
        self.scheduler.remove_job(str(hash(phoneNumberString)))


    def addToSchedule(self, tickers, phoneNumberString, fromNumber, freq = 1440):
        self.scheduler.add_job(tf.sendUpdate, 'interval', minutes=freq, id=str(hash(phoneNumberString)), replace_existing=True, args=[tickers, phoneNumberString, fromNumber] )


    def run(self):
        try:
            # Start scheduler in background, then we simply listen for messages that need to be added to the scheduler
            self.scheduler.start()
            while True:
                for message in self.pub.listen():
                    try:
                        messageContents = json.loads(message['data'])
                        if messageContents['action'] in self.messageHandles:
                            self.messageHandles[messageContents['action']](**messageContents['args'])
                    except:
                        pass
        except (KeyboardInterrupt, SystemExit):
            pass

if __name__ == '__main__':
    ScheduleServer = ScheduleServer()
    ScheduleServer.run()
