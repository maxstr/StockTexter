from flask import Flask, request, redirect
import StockGrabber as sg
import twilio.twiml
import ScheduleServer as ss
from TextResponse import stockInfoAsString
from pubsub import pub

TextServer = Flask(__name__)


# Given a request asking for more information, returns a string with
# the stocks listed in the lastRequested cookie and some additional info
# about them
def moreInfo(request):
    response = twilio.twiml.Response()

    lastRequestedStocks = request.cookies.get('lastRequested')

    if not lastRequestedStocks:
        response.message("You must lookup stocks before requesting more information on them")
        return response

    stockList = []

    try:
        stockList = json.loads(lastRequestedStocks)
    except:
        response.message("An error occurred when loading stock data")
        return response

    stockInfo = stockInfoAsString(stockList, sg.FINANCE_PARAMS_EXTRA, "Here's some additional info\n")

    response.message(stockInfo)
    return response


# Given a request with just tickers, we return some basic information about those stocks
def basicInfo(request):
    response = twilio.twiml.Response()

    basicFooter = "Respond with MORE or SUBSCRIBE to get more info or to subscribe to daily alerts"

    incomingText = request.form['Body']
    # If we need to strip out the command, do so.
    words = incomingText.split()
    if words[0].lower() == 'basic':
        stockList = words[1:]
    else:
        stockList = words

    # Get the stock info we want.
    stockInfo = stockInfoAsString(stockList, sg.FINANCE_PARAMS_BASIC)

    response.message(stockInfo)
    response.message(basicFooter)

    return response

# Given a request for all information about a stock, returns a string with information about each ticker requested
def allInfo(resp):

    response = twilio.twiml.Response()

    # If we need to strip out the command, do so.
    incomingText = request.form['Body']
    words = incomingText.split()
    if words[0].lower() == 'all':
        stockList = words[1:]
    else:
        stockList = words

    # Get the stock info we want.
    stockInfo = stockInfoAsString(stockList, sg.FINANCE_PARAMS_ALL)

    response.message(stockInfo)

    return response

def addToSchedule(request):

    response = twilio.twiml.Response()

    lastRequestedStocks = request.cookies.get('lastRequested')

    if not lastRequestedStocks:
        response.message("You must lookup stocks before subscribing to them")
        return response

    stockList = []
    try:
        stockList = json.loads(lastRequestedStocks)
    except:
        response.message("An error occurred when loading stock data")
        return response

    if stockList:
        # Use PubSub to add this stocklist and number to the schedule
        pub.sendMessage('addToSchedule', tickers = stockList, phoneNumberString = request.form['From'])
        response.message("You've subscribed to daily alerts for the following tickers: " + " ".join(stockList))
    else:
        response.message("No valid stocks found to subscribe for.")

    return response

def removeFromSchedule(request):
    response = twilio.twiml.Response()
    return ""


# List of possible commands (first word in message) and their associated functions for handling them. These functions need to accept a Flask request and returns a twilio twiml response

COMMANDS = \
    { 'more' : moreInfo \
    , 'subscribe' : addToSchedule \
    , 'default' : basicInfo \
    , 'basic' : basicInfo \
    , 'all' : allInfo
    , 'unsubscribe' : removeFromSchedule }




# This is the default entry point for text messages.
@TextServer.route("/", methods=['POST'])
def stockResponse():

    incomingText = request.form['Body']

    firstWord = incomingText.split()[0].lower()

    if firstWord in COMMANDS:
        response = COMMANDS[firstWord](request)
    else
        response = COMMANDS['default'](request)



    return str(response)

if __name__ == "__main__":
    TextServer.run(debug=True, host='0.0.0.0')
