import RPi.GPIO as IO
import time

'''
Cobit car motor setup 

motor 1  Right motor 
    PWM pin = 19 (GPIO no 35)       IA1 
    Direction pin = 13 (GPIO no 33) IB1

motor 2 Left motor 
    PWM pin = 12 (GPIO no 32)       IA2
    Dirction pin = 16 (GPIO no 36)  IB2

'''

class CobitCarMotorL9110():

    def __init__(self):
        self.motor1_r_pwmPin = 19
        self.motor1_r_dirPin = 13
        self.motor2_l_pwmPin = 12
        self.motor2_l_dirPin = 16
        IO.setwarnings(False)
        IO.setmode(IO.BCM)
        IO.setup(self.motor1_r_pwmPin, IO.OUT)
        IO.setup(self.motor1_r_dirPin, IO.OUT)
        IO.setup(self.motor2_l_pwmPin, IO.OUT)
        IO.setup(self.motor2_l_dirPin, IO.OUT)
        self.motor1_pwm = IO.PWM(self.motor1_r_pwmPin, 100)
        self.motor1_pwm.start(0)
        self.motor2_pwm = IO.PWM(self.motor2_l_pwmPin, 100)
        self.motor2_pwm.start(0)
    
    def motor1_start(self, speed):
        self.motor1_pwm.ChangeDutyCycle(speed)

    def motor2_start(self, speed):
        self.motor2_pwm.ChangeDutyCycle(speed)

    def motor_all_start(self, speed):
        self.motor1_start(speed)
        self.motor2_start(speed)

    def motor_all_stop(self):
        self.motor1_start(0)
        self.motor2_start(0)

if __name__ == '__main__':

    cobit_motor = CobitCarMotorL9110()
    while True:
        cobit_motor.motor_all_start(50)
        time.sleep(2)
        cobit_motor.motor_all_stop()
        time.sleep(2)





