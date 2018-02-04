import time
import itertools
from threading import Thread
from rc_car.servo import Servo
from rc_car.distance_sensor.DistanceSensor import DistanceSensor


class RotaryDistanceSensor:
    def __init__(self, pin_trigger, pin_echo, pin_servo,
                 servo_min_angle=45, servo_max_angle=135,
                 auto_rotation=True, rotation_delay=0.2, rotation_step_angle=45):

        self.distance_sensor = DistanceSensor(pin_trigger=pin_trigger,
                                              pin_echo=pin_echo)

        self.Servo = Servo.Servo(pin=pin_servo,
                                 model=Servo.SERVO_MODEL_DX001)

        self.servo_min_angle = max(servo_min_angle, self.Servo.get_min_angle())
        self.servo_max_angle = min(servo_max_angle, self.Servo.get_max_angle())
        self.angles = itertools.cycle(
            self.__angles(
                self.servo_min_angle,
                self.servo_max_angle,
                rotation_step_angle)
        )

        self.servo_angle = (self.servo_min_angle + self.servo_max_angle) // 2
        self.Servo.set_angle(self.servo_angle)

        self.auto_rotation = auto_rotation
        if self.auto_rotation:
            self.__pause_rotation = False
            self.rotation_delay = rotation_delay
            self.start_servo_rotation_loop()

    def __del__(self):
        if self.auto_rotation:
            self.stop_rotation = True
            try:
                self.servo_rotation_thread.join()
            except Exception:
                pass

    def __angles(self, start, stop, step):
        angles_progression = [i for i in range(start, stop + step, step)] + \
                             [i for i in range(stop - step, start, -step)]
        return angles_progression

    def start_servo_rotation_loop(self):
        self.servo_rotation_thread = Thread(
            target=self.__servo_rotation_loop)
        self.servo_rotation_thread.start()

    def __servo_rotation_loop(self):
        while self.auto_rotation:
            if not self.__pause_rotation:
                self.servo_angle = next(self.angles)
                self.Servo.set_angle(self.servo_angle)
                time.sleep(self.rotation_delay)

    def pause_rotation(self):
        self.__pause_rotation = True

    def resume_rotation(self):
        self.__pause_rotation = False

    def detect_object(self, min_distance=20, angle=None):
        if angle is not None:
            self.servo_angle = min(max(angle, self.servo_min_angle, self.servo_max_angle))
            self.Servo.set_angle(self.servo_angle)
            time.sleep(0.1)

        obstacle_detected = self.distance_sensor.detect_object(min_distance=min_distance)

        if self.auto_rotation and obstacle_detected:
            self.pause_rotation()

        return obstacle_detected
