from flask import request
import twilio.twiml
import StockGrabber as sg
import json
from pubsub import pub



# Given tickers, parameters as { 'yahooParam' : 'Parameter Name' }, and optionally a header returns a well-formatted string with information on each ticker.
def stockInfoAsString(stockList, params=sg.FINANCE_PARAMS_BASIC, header = ""):
    parameters = params.copy()
    parameters.update({'n' : 'Name'})

    stockInfo = sg.stockInfoFromTickers(stockList, parameters)
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

