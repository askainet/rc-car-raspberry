import RPi.GPIO as GPIO
import time


class DistanceSensor:
    def __init__(self, pin_trigger, pin_echo):
        self.pin_trigger = pin_trigger
        self.pin_echo = pin_echo
        GPIO.setup(self.pin_trigger, GPIO.OUT)
        GPIO.setup(self.pin_echo, GPIO.IN)
        # wait for sensor to be ready
        time.sleep(2.0)

    def measure_distance(self, timeout=0.1):
        if GPIO.input(self.pin_echo):
            print("False positive from last trigger")

        # send sonic signal during 0.01ms
        GPIO.output(self.pin_trigger, True)
        time.sleep(0.00001)
        GPIO.output(self.pin_trigger, False)

        arrival_time = time.time()
        stop_time = time.time()

        # wait for ECHO signal to arrive
        while not GPIO.input(self.pin_echo):
            arrival_time = time.time()
            if stop_time + timeout < arrival_time:
                # timeout ms exceeded waiting for ECHO
                return None

        # wait until ECHO signal stops
        while GPIO.input(self.pin_echo):
            stop_time = time.time()

        # duration of the ECHO signal
        time_elapsed = stop_time - arrival_time
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (time_elapsed * 34300) / 2

        return distance

    def detect_object(self, min_distance=10):
        timeout = min_distance * 1.5 / 34300
        distance = self.measure_distance(timeout=timeout)
        print("Distance: {}".format(distance))
        if distance is None:
            return None
        return distance <= min_distance
