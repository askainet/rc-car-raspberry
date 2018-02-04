import RPi.GPIO as GPIO


SERVO_MODEL_DX001 = {
    "frequency": 50,
    "min_angle": 0,
    "max_angle": 180,
    "min_duty_cycle": 4,
    "max_duty_cycle": 12
}


class Servo:
    def __init__(self, pin, model):
        self.pin = pin
        self.model = model
        self.slope = (self.model["max_duty_cycle"] - self.model["min_duty_cycle"]) / \
                     (self.model["max_angle"] - self.model["min_angle"])
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, self.model["frequency"])
        self.pwm.start(0)

    def set_angle(self, angle):
        duty_cycle = self.slope * (angle - self.model["min_angle"]) + self.model["min_duty_cycle"]
        print("angle: {} / cycle: {}".format(angle, duty_cycle))
        self.pwm.ChangeDutyCycle(duty_cycle)

    def get_min_angle(self):
        return self.model["min_angle"]

    def get_max_angle(self):
        return self.model["max_angle"]
