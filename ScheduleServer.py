from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from twilio.rest import TwilioRestClient
import TextResponse as tr
from pubsub import pub

TWILIO_ACCOUNT_SID = "***REMOVED***"
TWILIO_AUTH_TOKEN = "***REMOVED***"
SENDING_NUMBER = "+18052044765"


class ScheduleServer:

    def __init__(self, sqlite = None, twilioSID = TWILIO_ACCOUNT_SID, twilioToken = TWILIO_AUTH_TOKEN, outgoingNumber = SENDING_NUMBER):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_jobstore('sqlalchemy', url=(sqlite if sqlite else 'sqlite:///schedule.sqlite'))
        self.restClient = TwilioRestClient(twilioSID, twilioToken)
        self.fromNumber = outgoingNumber
        pub.subscribe(self.addToSchedule, 'addToSchedule')
        pub.subscribe(self.removeFromSchedule, 'removeFromSchedule')

    def removeFromSchedule(self, phoneNumberString):
        self.scheduler.remove_job(hash(phoneNumberString))


    def addToSchedule(self, tickers, phoneNumberString, freq = 1440):
        self.scheduler.add_job(self.sendUpdate, 'interval', minutes=freq, id=hash(phoneNumberString), args=[tickers, phoneNumberString])


    def run(self):
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass

    def sendUpdate(self, tickers, phoneNumberString):

        updateLines = tr.stockInfoAsString(tickers, sg.FINANCE_PARAMS_ALL)
        footer = "\n Respond with UNSUBSCRIBE to cancel your scheduled alert"
        message1 = self.restClient.messages.create(to=phoneNumberString, from_=self.fromNumber, body = updateLines)
        message2 = self.restClient.messages.create(to=phoneNumberString, from_=self.fromNumber, body=footer)



