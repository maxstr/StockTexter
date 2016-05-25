from flask import Flask, request, make_response
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
    twimlResponse = twilio.twiml.twimlresponse()

    moreFooter = "Respond with SUBSCRIBE to subscribe to a daily update for these stocks"

    lastRequestedStocks = request.cookies.get('lastRequested')

    if not lastRequestedStocks:
        twimlResponse.message("You must lookup stocks before requesting more information on them")
        return twimlResponse

    stockList = []

    try:
        stockList = json.loads(lastRequestedStocks)
    except:
        twimlResponse.message("An error occurred when loading stock data")
        return twimlResponse

    stockInfo = stockInfoAsString(stockList, sg.FINANCE_PARAMS_EXTRA, "Here's some additional info\n")

    twimlResponse.message(stockInfo)
    twimlResponse.message(moreFooter)

    flaskResponse = make_response(twimlResponse, 200)

    flaskResponse.set_cookie('lastRequested', json.dumps(filter(lambda key: stockInfo[key]['Name'] != 'N/A', stockInfo)))

    return flaskResponse


# Given a request with just tickers, we return some basic information about those stocks
def basicInfo(request):

    twimlResponse = twilio.twiml.response()

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

    twimlResponse.message(stockInfo)
    twimlResponse.message(basicFooter)

    flaskResponse = make_response(twimlResponse, 200)
    # Drop all stocks that returned N/A, put the rest in a cookie
    flaskResponse.set_cookie('lastRequested', json.dumps(filter(lambda key: stockInfo[key]['Name'] != 'N/A', stockInfo)))

    return flaskResponse

# Given a request for all information about a stock, returns a string with information about each ticker requested
def allInfo(resp):

    twimlResponse = twilio.twiml.response()

    allFooter = "Respond with SUBSCRIBE to subscribe to a daily update for these stocks"

    # If we need to strip out the command, do so.
    incomingText = request.form['Body']
    words = incomingText.split()
    if words[0].lower() == 'all':
        stockList = words[1:]
    else:
        stockList = words

    # Get the stock info we want.
    stockInfo = stockInfoAsString(stockList, sg.FINANCE_PARAMS_ALL)

    twimlResponse.message(stockInfo)
    twimlResponse.message(allFooter)

    flaskResponse = make_response(twimlResponse, 200)

    flaskResponse.set_cookie('lastRequested', json.dumps(filter(lambda key: stockInfo[key]['Name'] != 'N/A', stockInfo)))

    return flaskResponse


def addToSchedule(request):

    twimlResponse = twilio.twiml.twimlResponse()

    lastRequestedStocks = request.cookies.get('lastRequested')

    if not lastRequestedStocks:
        twimlResponse.message("You must lookup stocks before subscribing to them")
        return twimlResponse

    stockList = []
    try:
        stockList = json.loads(lastRequestedStocks)
    except:
        twimlResponse.message("An error occurred when loading stock data")
        return twimlResponse

    if stockList:
        # Use PubSub to add this stocklist and number to the schedule
        pub.sendMessage('addToSchedule', tickers = stockList, phoneNumberString = request.form['From'])
        twimlResponse.message("You've subscribed to daily alerts for the following tickers: " + " ".join(stockList))
    else:
        twimlResponse.message("No valid stocks found to subscribe for.")


    flaskResponse = make_response(twimlResponse, 200)

    return flaskResponse

def removeFromSchedule(request):
    twimlResponse = twilio.twiml.response()


    flaskResponse = make_response(twimlResponse, 200)

    return flaskResponse


# List of possible commands (first word in message) and their associated functions for handling them. These functions need to accept a Flask request and returns a flask response

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
    else:
        response = COMMANDS['default'](request)



    return response

if __name__ == "__main__":
    TextServer.run(debug=True, host='0.0.0.0')
