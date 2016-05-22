import urlparse
from StringIO import StringIO
from urllib import urlencode
import requests
import csv

# Info from http://www.jarloo.com/yahoo_finance/
FINANCE_API_URL = "http://finance.yahoo.com/d/quotes.csv?"
FINANCE_PARAMS_BASIC = { 'a': 'Ask', 'b' : 'Bid', 'c' : 'Change', 'n' : 'Name' }
FINANCE_PARAMS_EXTRA = { 'g' : 'Day Low', 'h': 'Day High', 'v': 'Volume', 't7': 'Ticker Trend' }
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
















