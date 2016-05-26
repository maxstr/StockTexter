import urlparse
from StringIO import StringIO
from urllib import urlencode
import requests
import csv

# Functions for interacting with Yahoo! Stock quote API.


# Info from http://www.jarloo.com/yahoo_finance/
FINANCE_API_URL = "http://finance.yahoo.com/d/quotes.csv?"
FINANCE_PARAMS_BASIC = { 'a': 'Ask', 'b' : 'Bid', 'c' : 'Change', 'n' : 'Name' }
FINANCE_PARAMS_EXTRA = { 'g' : 'Day Low', 'h': 'Day High', 'v': 'Volume', 't7': 'Ticker Trend', 'n' : 'Name' }
FINANCE_PARAMS_ALL = FINANCE_PARAMS_BASIC.copy()
FINANCE_PARAMS_ALL.update(FINANCE_PARAMS_EXTRA)

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
        paramNames = map(lambda param: FINANCE_PARAMS_ALL[param], parameters)
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

# Given a list of tickers, returns which are valid
def getValidStocks(stockList):
    returnList = []
    parameters = { 'n' : "Name" }
    stockInfo = stockInfoFromTickers(stockList, parameters)
    for stock in stockList:
        if stockInfo[stock]['Name'] != 'N/A':
            returnList.append(stock)

    return returnList


