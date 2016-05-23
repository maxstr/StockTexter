from flask import Flask, request, redirect
import StockGrabber as sg
import twilio.twiml

HTTPServer = Flask(__name__)

class TextServer:
    def __init__(self):
        self.HTTPServer = HTTPServer

    @HTTPServer.route("/", methods=['POST'])
    def stockResponse(self):
        """Returns a response to a text message"""

        # Handle and parse incoming data
        incomingText = request.form['Body']
        stockList = incomingText.split()

        # Get the stock info we want.
        stockInfo = stockInfoFromTickers(stockList, sg.FINANCE_PARAMS_BASIC)


        #Return a response
        returnLines = ""
        for stock in stockList:
            returnLines += "%s \n" % stockInfo[stock]['Name']
            for param in filter(lambda key: key != 'Name', sg.FINANCE_PARAMS_BASIC.values()):
                returnLines += "%s : %s" % (param, stockInfo[stock][param])
            returnLines += "\n"



        resp = twilio.twiml.Response()
        resp.message(returnLines)

        return str(resp)

if __name__ == "__main__":
    HTTPServer.run(debug=True, host='0.0.0.0')
