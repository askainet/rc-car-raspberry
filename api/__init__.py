from flask import Blueprint
from flask import request
from flask import jsonify
from rc_car.drive.Drive import Drive
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
pins_drivers = {
    "driver_left_a": 23,
    "driver_left_b": 24,
    "driver_right_a": 20,
    "driver_right_b": 21,
    "distance_sensor_trigger": 25,
    "distance_sensor_echo": 26,
    "distance_sensor_servo": 18
}


api = Blueprint('api', 'api')

drive = Drive(pins=pins_drivers)


@api.route('/drive', methods=['POST'])
def do_drive():
    payload = request.get_json()

    if payload["speed"] < 0:
        payload["speed"] = 0
    elif payload["speed"] > 100:
        payload["speed"] = 100
    if abs(payload["angle"]) > 90:
        payload["angle"] = 90

    drive.drive(
        forward=payload["forward"],
        angle=payload["angle"],
        speed=payload["speed"]
    )

    re = jsonify(
        {
            "status": "ok",
            "request": payload
        }
    )
    return re
