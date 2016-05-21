from flask import Flask, request, redirect
import twilio.twiml

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""

    resp = twilio.twiml.Response()
    resp.message("Hello, Mobile Monkey")
    print request
    return str(resp)

@app.route("/stocks", methods=['POST'])
def stockResponse():
    """Returns a stock quote given a stock"""
    pass




if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
