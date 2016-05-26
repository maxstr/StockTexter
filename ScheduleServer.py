from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import StockGrabber as sg
from twilio.rest import TwilioRestClient
import TextResponse as tr
import redis
from time import sleep
import json

TWILIO_ACCOUNT_SID = "***REMOVED***"
TWILIO_AUTH_TOKEN = "***REMOVED***"
SENDING_NUMBER = "+18052044765"



class ScheduleServer:

    def __init__(self, sqlite = None, twilioSID = TWILIO_ACCOUNT_SID, twilioToken = TWILIO_AUTH_TOKEN \
                , outgoingNumber = SENDING_NUMBER \
                , redisConfig = {'host':'localhost', 'port':6379, 'db':0} \
                , topic = 'schedulerMessage'):

        self.scheduler = BackgroundScheduler()
#        self.scheduler.add_jobstore('sqlalchemy', url=(sqlite if sqlite else 'sqlite:///schedule.sqlite'))
        self.restClient = TwilioRestClient(twilioSID, twilioToken)
        self.fromNumber = outgoingNumber

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


    def addToSchedule(self, tickers, phoneNumberString, freq = 1440):
        self.scheduler.add_job(self.sendUpdate, 'interval', seconds=3, id=str(hash(phoneNumberString)), replace_existing=True, args=[tickers, phoneNumberString] )


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
                sleep(1)
        except (KeyboardInterrupt, SystemExit):
            pass

    def sendUpdate(self, tickers, phoneNumberString):

        updateLines = tr.stockInfoAsString(tickers, sg.FINANCE_PARAMS_ALL)
        footer = "\n Respond with UNSUBSCRIBE to cancel your scheduled alert"
        message1 = self.restClient.messages.create(to=phoneNumberString, from_=self.fromNumber, body = updateLines)
        message2 = self.restClient.messages.create(to=phoneNumberString, from_=self.fromNumber, body=footer)

