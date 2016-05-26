from twilio.rest import TwilioRestClient
import StockGrabber as sg

TWILIO_ACCOUNT_SID = "***REMOVED***"
TWILIO_AUTH_TOKEN = "***REMOVED***"


# A couple utility functions for independently sending messages from twilio
RestClient = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def sendUpdate(tickers, phoneNumberString, fromNumber):
    updateLines = sg.stockInfoAllPretty(tickers, sg.MAX_TEXT_LENGTH)
    for message in updateLines:
	sendMessage(message, '', phoneNumberString, fromNumber)

    footer = "\n Respond with PLSSTOP to cancel your scheduled alert"
    sendMessage(footer, '', phoneNumberString, fromNumber)


def sendMessage(body, footer, phoneNumberString, fromNumber):
    RestClient.messages.create(to=phoneNumberString, from_=fromNumber, body = body )
    if footer:
	    RestClient.messages.create(to=phoneNumberString, from_=fromNumber, body = footer)


