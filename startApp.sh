#!/bin/bash

(python ScheduleServer.py)&

gunicorn -w 5 -b 0.0.0.0:5000 TextServer:TextServer
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

