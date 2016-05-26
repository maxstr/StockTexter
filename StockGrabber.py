import urlparse
from StringIO import StringIO
from urllib import urlencode
import requests
import csv
from flask import current_app

# Functions for interacting with Yahoo! Stock quote API.


# Info from http://www.jarloo.com/yahoo_finance/
FINANCE_API_URL = "http://finance.yahoo.com/d/quotes.csv?"
FINANCE_PARAMS_BASIC = { 'a': 'Ask', 'b' : 'Bid', 'c' : 'Change', 'n' : 'Name' }

FINANCE_PARAMS_EXTRA = { 'g' : 'Day Low', 'h': 'Day High', 'v': 'Volume', 'n' : 'Name' }
FINANCE_PARAMS_ALL = FINANCE_PARAMS_BASIC.copy()
FINANCE_PARAMS_ALL.update(FINANCE_PARAMS_EXTRA)

MAX_TEXT_FLASK_LENGTH = 160
MAX_TEXT_LENGTH = 1600




# Accepts [Tickers], and a dictionary { 'urlParam': 'Name of Parameter' } and returns { 'ticker': {'Name of Parameter' : 'Value'}}
def stockInfoFromTickers(tickers, paramDict = FINANCE_PARAMS_BASIC):
    # Zip to tickers : { parameters : values }
    returnDict = dict(zip( tickers, [ dict(zip(paramDict.values(), [None] * len(paramDict))) for _ in xrange(len(tickers)) ]))
    parameters = paramDict.keys()

    urlParams = { 's' : "+".join(tickers), 'f' : "".join(parameters) }

    request = requests.get(FINANCE_API_URL, params = urlParams)

    fileHandle = StringIO(request.text)

    csvReader = csv.reader(fileHandle, delimiter = ',', dialect=None)

    for index, row in enumerate(csvReader):
        # Go from b2, b3 etc to Ask, Bid...
        paramNames = map(lambda param: paramDict[param], parameters)
        # Generate a mapping of Ask:AskVal, Bid:BidVal
        stockValues = zip(paramNames, row)
        returnDict[tickers[index]].update(stockValues)

    return returnDict

# Given tickers, parameters as { 'yahooParam' : 'Parameter Name' }, and optionally a header returns a well-formatted string with information on each ticker.
def stockInfoAsString(stockList, params=FINANCE_PARAMS_BASIC, header = ""):
    parameters = params.copy()
    parameters.update({'n' : 'Name'})

    stockInfo = stockInfoFromTickers(stockList, parameters)
    #Return a response
    returnLines = header
    for stock in stockList:
        if stockInfo[stock]['Name'] != 'N/A':
            returnLines += "%s - %s \n" % (stockInfo[stock]['Name'], stock.upper())
            paramsNoName = filter(lambda key: key != 'Name', parameters.values())
            for param in paramsNoName:
                returnLines += "%s : %s\n" % (param, stockInfo[stock][param])
        else:
            returnLines += "%s - Ticker could not be found" % stock
            returnLines += "\n"

    return returnLines

def stockInfoBasicPretty(stockList, maxLength = MAX_TEXT_FLASK_LENGTH):

    parameters = { 'a': 'Ask', 'c1' : 'Change', 'n' : 'Name', 'p2': 'Percent Change'}


    stockInfo = stockInfoFromTickers(stockList, parameters)
    validStocks = set(getValidStocks(stockList))

    returnLines = [""]
    currentIndex = 0

    for stock in validStocks:
        newText = "\n%s - %s \n" % (stockInfo[stock]['Name'], stock.upper())
        # Ask / ^ price/percent
        arrow = ('+' if ('+' in stockInfo[stock]['Change']) else '-')
        newText += "$%.2f | %s%.2f/%.2f%%\n" % (float(stockInfo[stock]['Ask'])
                                       , arrow \
                                       , float(stockInfo[stock]['Change'].translate(None, "+-")) \
                                       , float(stockInfo[stock]['Percent Change'].translate(None, "+%-")))

        # Determine if we want this stock in the current message, or the message afterwards
        if len(newText + returnLines[currentIndex]) >= maxLength:
            returnLines.append(newText)
            currentIndex += 1
        else:
            returnLines[currentIndex] += newText

    invalidStocks = list(validStocks - set(stockList))
    if invalidStocks:
	    returnLines.append("The following tickers could not be found: %s" % (" ".join(invalidStocks)) )

    return returnLines


def stockInfoAllPretty(stockList, maxLength = MAX_TEXT_FLASK_LENGTH):

    parameters= { 'a': 'Ask', 'c1' : 'Change', 'n' : 'Name', 'p2' : 'Percent Change', 'o':'Open', 'h' : 'High', 'g': 'Low', 'p' : 'Previous Close'}

    stockInfo = stockInfoFromTickers(stockList, parameters)
    validStocks = set(getValidStocks(stockList))

    returnLines = [""]
    currentIndex = 0

    for stock in validStocks:
        newText = "\n%s - %s \n" % (stockInfo[stock]['Name'], stock.upper())
        # Ask / ^ price/percent
        arrow = ('+' if ('+' in stockInfo[stock]['Change']) else '-' )
        newText += "$%.2f | %s%.2f/%.2f%% \n" % (float(stockInfo[stock]['Ask'])
                                       , arrow \
                                       , float(stockInfo[stock]['Change'].translate(None, "+-")) \
                                       , float(stockInfo[stock]['Percent Change'].translate(None, "+%-")))
        newText += """\
Open: %(Open)s
High: %(High)s
Low: %(Low)s
Previous Close: %(Previous Close)s""" % stockInfo[stock]

        # Determine if we want this stock in the current message, or the message afterwards
        if len(newText + returnLines[currentIndex]) >= maxLength:
            returnLines.append(newText)
            currentIndex += 1
        else:
            returnLines[currentIndex] += newText
    invalidStocks = list(validStocks - set(stockList))
    if invalidStocks:
	    returnLines.append("The following tickers could not be found: %s" % (" ".join(invalidStocks)) )


    return returnLines



# Given a list of tickers, returns which are valid
def getValidStocks(stockList):
    returnList = []
    parameters = { 'n' : "Name" }
    stockInfo = stockInfoFromTickers(stockList, parameters)
    for stock in stockList:
        if stockInfo[stock]['Name'] != 'N/A':
            returnList.append(stock)

    return returnList


