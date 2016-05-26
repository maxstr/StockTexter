from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import StockGrabber as sg
from twilio.rest import TwilioRestClient
import TextResponse as tr
from pubsub import pub

TWILIO_ACCOUNT_SID = "***REMOVED***"
TWILIO_AUTH_TOKEN = "***REMOVED***"
SENDING_NUMBER = "+18052044765"

def printDerp():
	print "derp"

def sendUpdate(tickers, phoneNumberString):
	print "we updating - %r - %r" % (tickers, phoneNumberString)
#
#        restClient = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#
#	updateLines = tr.stockInfoAsString(tickers, sg.FINANCE_PARAMS_ALL)
#	footer = "\n Respond with UNSUBSCRIBE to cancel your scheduled alert"
#	message1 = restClient.messages.create(to=phoneNumberString, from_=SENDING_NUMBER, body = updateLines)
#	message2 = restClient.messages.create(to=phoneNumberString, from_=SENDING_NUMBER, body=footer)

class ScheduleServer:

    def __init__(self, sqlite = None, twilioSID = TWILIO_ACCOUNT_SID, twilioToken = TWILIO_AUTH_TOKEN, outgoingNumber = SENDING_NUMBER):
        self.scheduler = BackgroundScheduler()
#        self.scheduler.add_jobstore('sqlalchemy', url=(sqlite if sqlite else 'sqlite:///schedule.sqlite'))
        self.restClient = TwilioRestClient(twilioSID, twilioToken)
        self.fromNumber = outgoingNumber
        pub.subscribe(self.removeFromSchedule, 'removeFromSchedule')
	self.scheduler.add_job(printDerp, 'interval', minutes = 1, id = str(hash("derp")))
	print "initialized"

    def removeFromSchedule(self, phoneNumberString):
        self.scheduler.remove_job(str(hash(phoneNumberString)))


    def addToSchedule(self, tickers, phoneNumberString, freq = 1440):
	print "adding: %r" % self.scheduler.get_jobs()
        self.scheduler.add_job(sendUpdate, 'interval', seconds=3, id=str(hash(phoneNumberString)), replace_existing=True, args=[tickers, phoneNumberString] )
	print "after: %r" % self.scheduler.get_jobs()

 
    def run(self):
        try:
            print "started"
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass

    def sendUpdate(self, tickers, phoneNumberString):

        updateLines = tr.stockInfoAsString(tickers, sg.FINANCE_PARAMS_ALL)
        footer = "\n Respond with UNSUBSCRIBE to cancel your scheduled alert"
        message1 = self.restClient.messages.create(to=phoneNumberString, from_=self.fromNumber, body = updateLines)
        message2 = self.restClient.messages.create(to=phoneNumberString, from_=self.fromNumber, body=footer)

