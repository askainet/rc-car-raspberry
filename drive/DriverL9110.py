import RPi.GPIO as GPIO


class DriverL9110:
    def __init__(self, motor, pin_speed, pin_direction):
        self.motor = motor
        self.pin_direction = pin_direction
        self.pin_speed = pin_speed
        GPIO.setup(self.pin_direction, GPIO.OUT)
        GPIO.setup(self.pin_speed, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin_speed, 100)
        self.pwm.start(0)

    def drive(self, speed=100, forward=True):
        if speed < 1:
            self.stop()
            return
        if speed > 100:
            speed = 100
        reverse = forward == self.motor.reverse_polarity
        GPIO.output(self.pin_direction, reverse)
        duty_cycle = abs(
            int(reverse) * 100 - (
                round(speed * (100 - self.motor.min_duty_cycle) / 100) +
                self.motor.min_duty_cycle
            )
        )
        self.pwm.ChangeDutyCycle(duty_cycle)

    def stop(self):
        GPIO.output(self.pin_direction, False)
        GPIO.output(self.pin_speed, False)
        self.pwm.ChangeDutyCycle(0)
