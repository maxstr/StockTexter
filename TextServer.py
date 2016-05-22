from flask import Flask, request, redirect
import twilio.twiml

app = Flask(__name__)

@app.route("/", methods=['POST'])
def stockResponse():
    """Respond to incoming calls with a simple text message."""

    # Handle and parse incoming data
    incomingText = request.form['Body']
    stockList = incomingText.split()


    #Return a response
    returnLines = "\n"
    for stock in stockList:
        returnLines += "%s : %.2f\n" % (stock, 100.20)
    resp = twilio.twiml.Response()
    resp.message(returnLines)
    
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
