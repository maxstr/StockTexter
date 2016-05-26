from flask import Flask, request, make_response, current_app
import twilio.twiml
from flask_sqlalchemy import SQLAlchemy
import FlaskResponses as fr
import TwilioFunctions as tf

# Simple HTTP server for responding to twilio

TextServer = Flask(__name__)
TextServer.config['REDISPORT'] = 6379
TextServer.config['REDISHOST'] = 'localhost'
TextServer.config['REDISDB'] = 0
TextServer.config['REDISTOPIC'] = 'schedulerMessage'
TextServer.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
TextServer.config['FROMNUMBER'] = "+18052044765"
TextServer.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(TextServer)


# List of possible commands (first word in message) and their associated functions for handling them. These functions need to accept a Flask request and returns a flask response

# Send an empty response for a start message

COMMANDS = \
    { 'more' : fr.moreInfo \
    , 'subscribe' : fr.addToSchedule \
    , 'default' : fr.basicInfo \
    , 'basic' : fr.basicInfo \
    , 'all' : fr.allInfo \
    , 'plsstop' : fr.removeFromSchedule \
    , 'subscribedb' : fr.addToScheduleDB \
    , 'start' : (lambda _ : make_response(str(twilio.twiml.Response())))
    , 'helppls' : fr.helpMessage}\



# This is the default entry point for text messages.
@TextServer.route("/", methods=['POST'])
def stockResponse():

    incomingText = request.form['Body']
    firstWord = incomingText.split()[0].lower()

    # Determine if this is a first time user and send them a nice message if so
    userNumber = request.form['From']
    userExists = bool(User.query.filter_by(number=userNumber).all())
    if (not userExists) or firstWord.lower() == 'start':
        tf.sendMessage("""\
We noticed this is your first time using StockTexter. Here's a user guide!
1. Text [all/basic] (tickers)
2. Text subscribe afterwards if you want daily updates on these stocks.
3. Text helppls to see this message again"""\
                        , '', userNumber, current_app.config['FROMNUMBER'])
	if (not userExists):
		newUser = User(userNumber)
		db.session.add(newUser)
		db.session.commit()



    # Look at incoming text, try and match the first word against our list of commands.
    # If no match, we go with the default handler
    if firstWord in COMMANDS:
        response = COMMANDS[firstWord](request)
    else:
        response = COMMANDS['default'](request)

    return response


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(15), unique=True)

    def __init__(self, number):
        self.number = number


if __name__ == "__main__":
    TextServer.run(debug=True, host='0.0.0.0')
