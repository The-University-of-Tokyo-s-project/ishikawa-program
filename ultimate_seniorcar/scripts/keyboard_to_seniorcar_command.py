#!/usr/bin/env python
# coding: UTF-8

import rospy
from std_msgs.msg import Int8
from std_msgs.msg import Bool
from keyboard.msg import Key
from ultimate_seniorcar.msg import SeniorcarState

#difined by key.msg
UP    = 273
DOWN  = 274
RIGHT = 275
LEFT  = 276
SPACE = 32
KEY_E = 101
KEY_D = 100

OUT_VOL = [1,2,3,4]

ANGLE_INCLIMENT = 0.5




class CalculateVoltage:

	motor_devision = Int8()
	seniorcar_command = SeniorcarState()
	enable_motor = Bool()
	enable_motor.data = True
	seniorcar_command.accel_opening = 0
	seniorcar_command.steer_angle = 0

	t1 = rospy.Time(0)
	t2 = rospy.Time(0)

	t3 = 0
	flag = Bool()
	flag.data = False

	counter = 0

	def __init__(self):
		rospy.init_node('keyboard_to_devision')
		self.pub = rospy.Publisher('seniorcar_command', SeniorcarState, queue_size=10)
		self.pub2 = rospy.Publisher('enable_motor', Bool, queue_size=10)
	
	def subscribe_key_data(self):
		rospy.Subscriber("keyboard/keydown", Key, self.keyboarddownCallback)
		rospy.Subscriber("keyboard/keyup", Key, self.keyboardupCallback)

	def keyboarddownCallback(self,key):
		if key.code == RIGHT:
			self.seniorcar_command.steer_angle -= ANGLE_INCLIMENT
			self.enable_motor.data = True
		elif key.code == LEFT:
			self.seniorcar_command.steer_angle += ANGLE_INCLIMENT
			self.enable_motor.data = True
		elif key.code == UP:
			self.seniorcar_command.accel_opening = 127
			self.seniorcar_command.max_velocity = 2.0
		elif key.code == DOWN:
			self.t1 = rospy.Time.now()
			self.flag.data = True
			if self.seniorcar_command.direction_switch == 0:
				self.seniorcar_command.direction_switch = 1
			else:
				self.seniorcar_command.direction_switch = 0
		elif key.code == SPACE:
			self.seniorcar_command.accel_opening = 0
			self.seniorcar_command.steer_angle = 0
		elif key.code == KEY_E:
			self.enable_motor.data = True
		elif key.code == KEY_D:
			self.enable_motor.data = False


	def keyboardupCallback(self,key):
		if key.code == UP:
			self.seniorcar_command.accel_opening = 0
		elif key.code == RIGHT or key.code == LEFT:
			self.enable_motor.data = False

	def calculate_and_publish_voltage(self):
		rate = rospy.Rate(100)
		while not rospy.is_shutdown():
			#self.counter += 1

			#if self.counter <1000:#jikan de nkirerukano kakuninn no tameni tuika 11/6
			#	self.pub.publish(self.seniorcar_command)
			#	self.pub2.publish(self.enable_motor)
			#else:
			#	self.seniorcar_command.accel_opening = 0
			#	self.seniorcar_command.steer_angle = 0
			#	self.seniorcar_command.direction_switch = 0
			#	self.pub.publish(self.seniorcar_command)
			#	self.pub2.publish(self.enable_motor)#11/6
			if self.flag.data == True:
				self.t2 = rospy.Time.now()
				self.t3 = self.t2.secs - self.t1.secs
			if self.t3>3:
				self.seniorcar_command.accel_opening = 0
				self.seniorcar_command.steer_angle = 0
				self.seniorcar_command.direction_switch = 0
			self.pub.publish(self.seniorcar_command)
			self.pub2.publish(self.enable_motor)#11/6
			rate.sleep()

if __name__ == '__main__':
	calclater = CalculateVoltage()
	calclater.subscribe_key_data()
	calclater.calculate_and_publish_voltage()
