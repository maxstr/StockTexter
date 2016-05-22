from flask import Flask, request, redirect
import StockGrabber as sg
import twilio.twiml

app = Flask(__name__)

@app.route("/", methods=['POST'])
def stockResponse():
    """Respond to incoming calls with a simple text message."""

    # Handle and parse incoming data
    incomingText = request.form['Body']
    stockList = map(lambda stock: stock.upper(), incomingText.split())

    # Get the stock info we want.
    stockInfo = sg.stockInfoFromTickers(stockList, sg.FINANCE_PARAMS_BASIC)


    #Return a response
    returnLines = ""
    for stock in stockList:
	if stockInfo[stock]['Name'] != 'N/A':
		returnLines += "%s - %s \n" % (stockInfo[stock]['Name'], stock)
		paramsNoName = filter(lambda key: key != 'Name', sg.FINANCE_PARAMS_BASIC.values())
		for param in paramsNoName:
		    returnLines += "%s : %s\n" % (param, stockInfo[stock][param])
	else:
		returnLines += "%s - Ticker could not be found" % stock
        returnLines += "\n"



    resp = twilio.twiml.Response()
    resp.message(returnLines)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
