from flask import request, make_response, current_app
import redis
import twilio.twiml
import StockGrabber as sg
import json
from functools import partial

# Responses that accept a flask request and return a flask response


# Given a request asking for more information, returns a string with
# the stocks listed in the lastRequested cookie and some additional info
# about them
def moreInfo(request):
    twimlResponse = twilio.twiml.Response()


    lastRequestedStocks = request.cookies.get('lastRequested')

    if not lastRequestedStocks:
        twimlResponse.message("You must lookup stocks before requesting more information on them")
        flaskResponse = make_response(str(twimlResponse), 200)
        return flaskResponse

    stockList = []


    try:
        stockList = json.loads(lastRequestedStocks.replace("|", ','))
    except:
        twimlResponse.message("An error occurred when loading stock data")
        flaskResponse = make_response(str(twimlResponse), 200)
        return flaskResponse

    stockList = map(lambda a: a.upper(), stockList)



    stockLines = sg.stockInfoAllPretty(stockList, 160)
    for line in stockLines:
        twimlResponse.message(line)

    flaskResponse = make_response(str(twimlResponse), 200)
    flaskResponse.set_cookie('lastRequested', json.dumps(stockList).replace(',', '|'))

    return flaskResponse

# Our default stock info and standard text response functions. We partially apply to get a specific function, eg basic/default, all

def textResponse(request, response = "", footer = ""):
    twimlResponse = twilio.twiml.Response()
    twimlResponse.message(response + "\n" + footer)

    flaskResponse = make_response(str(twimlResponse), 200)
    return flaskResponse


firstMessage = partial(textResponse \
        , response = """\
We noticed this is your first time using StockTexter. Here's a user guide!
1. Text [all/basic] (tickers)
2. Text subscribe afterwards if you want daily updates on these stocks.
3. Text plshelp to see this message again""" \
        , footer = '')

helpMessage = partial(textResponse \
        , response = """\
Possible actions: commands
1. For info : [all/basic] (tickers)
2. For daily updates: subscribe
3. For help: plshelp""" \
        , footer = '')



def stockInfoBasic(request, footer = "", command = '', stockParams = sg.FINANCE_PARAMS_BASIC):
    twimlResponse = twilio.twiml.Response()

    incomingText = request.form['Body']
    # If we need to strip out the command, do so.
    words = incomingText.split()
    if words[0].lower() == command:
        stockList = words[1:]
    else:
        stockList = words

    stockList = map(lambda a: a.upper(), stockList)
    # Get the stock info we want.
    stockInfo = sg.stockInfoAsString(stockList, stockParams)

    twimlResponse.message(stockInfo + "\n" + footer)

    flaskResponse = make_response(str(twimlResponse), 200)
    flaskResponse.set_cookie('lastRequested', json.dumps(stockList).replace(',', '|'))

    return flaskResponse

basicInfo = partial(stockInfoBasic \
        , footer = "" \
        , command = 'basic' \
        , stockParams = sg.FINANCE_PARAMS_BASIC )


allInfo = partial(stockInfoBasic \
        , footer = "" \
        , command = 'all' \
        , stockParams = sg.FINANCE_PARAMS_ALL)

# Accepts a request and a function that converts a list of stocks into a list of messages to send

def stockInfoPretty(request, command = '', prettyFunc = sg.stockInfoBasicPretty):
    twimlResponse = twilio.twiml.Response()

    incomingText = request.form['Body']
    # If we need to strip out the command, do so.
    words = incomingText.split()
    if words[0].lower() == command:
        stockList = words[1:]
    else:
        stockList = words

    stockList = map(lambda a: a.upper(), stockList)

    # Get the lines returned by our function
    stockLines = prettyFunc(stockList)
    for line in stockLines:
        twimlResponse.message(line)

    flaskResponse = make_response(str(twimlResponse), 200)
    flaskResponse.set_cookie('lastRequested', json.dumps(stockList).replace(',', '|'))

    return flaskResponse

basicInfoP = partial(stockInfoPretty\
        , command = "basic" \
        , prettyFunc = sg.stockInfoBasicPretty )

allInfoP = partial(stockInfoPretty\
        , command = 'all' \
        , prettyFunc = sg.stockInfoAllPretty)



def addToScheduleDB(request):

    twimlResponse = twilio.twiml.Response()

    lastRequestedStocks = request.cookies.get('lastRequested').replace("|", ",")

    if not lastRequestedStocks:
        twimlResponse.message("You must lookup stocks before subscribing to them")
        flaskResponse = make_response(str(twimlResponse), 200)
        return flaskResponse

    stockList = []

    try:
        stockList = sg.getValidStocks(json.loads(lastRequestedStocks))
    except:
        twimlResponse.message("An error occurred when loading stock data")
        flaskResponse = make_response(str(twimlResponse), 200)
        return flaskResponse
    stockList = map(lambda a: a.upper(), stockList)

    if stockList:
        # Pub via redis
        red = redis.StrictRedis(host=current_app.config['REDISHOST'], port=current_app.config['REDISPORT'],db=current_app.config['REDISDB'])
        message = { 'action' : 'addToSchedule' \
                  , 'args' : { 'tickers' : stockList \
                             , 'phoneNumberString' : request.form['From'] \
                             , 'fromNumber' : current_app.config['FROMNUMBER'] \
                             , 'freq' : 2 }
                  }
        red.publish(current_app.config['REDISTOPIC'], json.dumps(message))
        twimlResponse.message("You've subscribed to daily alerts for the following tickers: %s \n\nReply with PLSSTOP to cancel further messages" % " ".join(stockList))

    else:
        twimlResponse.message("No valid stocks found to subscribe for.")


    flaskResponse = make_response(str(twimlResponse), 200)

    return flaskResponse


def addToSchedule(request):

    twimlResponse = twilio.twiml.Response()

    lastRequestedStocks = request.cookies.get('lastRequested').replace("|", ",")

    if not lastRequestedStocks:
        twimlResponse.message("You must lookup stocks before subscribing to them")
        flaskResponse = make_response(str(twimlResponse), 200)
        return flaskResponse

    stockList = []
    try:
        stockList = json.loads(lastRequestedStocks)
    except:
        twimlResponse.message("An error occurred when loading stock data")

        flaskResponse = make_response(str(twimlResponse), 200)
        return flaskResponse

    if stockList:
        # Pub via redis
        red = redis.StrictRedis(host=current_app.config['REDISHOST'], port=current_app.config['REDISPORT'],db=current_app.config['REDISDB'])
        message = { 'action' : 'addToSchedule' \
                  , 'args' : { 'tickers' : stockList \
                             , 'phoneNumberString' : request.form['From']\
                             , 'fromNumber' : current_app.config['FROMNUMBER'] }
                  }
        red.publish(current_app.config['REDISTOPIC'], json.dumps(message))
        twimlResponse.message("You've subscribed to daily alerts for the following tickers: " + " ".join(stockList))

    else:
        twimlResponse.message("No valid stocks found to subscribe for.")


    flaskResponse = make_response(str(twimlResponse), 200)

    return flaskResponse

def removeFromSchedule(request):
    twimlResponse = twilio.twiml.Response()

    red = redis.StrictRedis(host=current_app.config['REDISHOST'] \
                            , port=current_app.config['REDISPORT'] \
                            , db=current_app.config['REDISDB'])

    message = { 'action' : 'removeFromSchedule' \
              , 'args' : { 'phoneNumberString' : request.form['From'] }
              }
    red.publish(current_app.config['REDISTOPIC'], json.dumps(message))
    twimlResponse.message("You've been unsubscribed from all alerts")



    flaskResponse = make_response(str(twimlResponse), 200)

    return flaskResponse
