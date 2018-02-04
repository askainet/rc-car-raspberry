import time
from threading import Thread
from rc_car.drive.Motor import Motor
from rc_car.drive.DriverL9110 import DriverL9110
from rc_car.distance_sensor.RotaryDistanceSensor import RotaryDistanceSensor


class Drive:
    def __init__(self, pins, collision_avoidance=True):
        self.collision_avoidance = collision_avoidance

        self.driver_left = DriverL9110(
            Motor(reverse_polarity=False),
            pin_speed=pins["driver_left_a"],
            pin_direction=pins["driver_left_b"])

        self.driver_right = DriverL9110(
            Motor(reverse_polarity=False),
            pin_speed=pins["driver_right_a"],
            pin_direction=pins["driver_right_b"])

        self.distance_sensor_front = RotaryDistanceSensor(
            pin_trigger=pins["distance_sensor_trigger"],
            pin_echo=pins["distance_sensor_echo"],
            pin_servo=pins["distance_sensor_servo"])

        self.driving = True
        self.driving_forward = True

        if self.collision_avoidance:
            self.obstacle_front = True
            self.start_collision_avoidance()

    def __del__(self):
        self.driving = False
        if self.collision_avoidance:
            try:
                self.collision_avoidance_thread.join()
            except Exception:
                pass

    #                          both
    #                          full
    #                          speed   left full forward
    #                            0  45 right half forward
    #                            | /
    #        left stopped -90 ------- 90 left full forward
    #  right full forward        | \     right stopped
    #                            0  45
    #                                  left full backward
    #                                  right half backward

    def drive(self, forward=True, angle=0, speed=100):
        self.driving_forward = forward

        if angle > 0:
            speed_left = speed
            speed_right = round((90 - angle) / 90 * speed)
        elif angle < 0:
            speed_left = round((90 + angle) / 90 * speed)
            speed_right = speed
        else:
            (speed_left, speed_right) = (speed, speed)

        if self.collision_avoidance:
            if forward and self.obstacle_front and speed != 0:
                return False

        print("speed_left: {} / speed_right: {} / forward: {}".format(speed_left, speed_right, forward))
        self.driver_left.drive(speed=speed_left, forward=forward)
        self.driver_right.drive(speed=speed_right, forward=forward)

        if not forward or speed == 0:
            self.distance_sensor_front.pause_rotation()
        else:
            self.distance_sensor_front.resume_rotation()

    def start_collision_avoidance(self):
        self.collision_avoidance_thread = Thread(
            target=self.__collision_avoidance_loop)
        self.collision_avoidance_thread.start()

    def __collision_avoidance_loop(self):
        while self.driving:
            if self.driving_forward and \
               self.distance_sensor_front.detect_object(min_distance=30):
                if not self.obstacle_front:
                    self.obstacle_front = True
                    print("Front object detected! Emergency stop!")
                    self.drive(speed=0)
            else:
                if self.obstacle_front:
                    print("Obstacle not detected, driving again!")
                self.obstacle_front = False

            time.sleep(0.01)
