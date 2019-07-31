#!/usr/bin/env python
# coding: UTF-8

import rospy
from ultimate_seniorcar.msg import SeniorcarState
from std_msgs.msg import Bool
from std_msgs.msg import String

PUBLISH_RATE = 10.0       # コマンドをパブリッシュする周期


class GenerateSeniorcarCommand:

	seniorcar_state   = SeniorcarState()
	seniorcar_command = SeniorcarState()
	seniorcar_command.accel_opening = 0
	seniorcar_state.accel_opening = 0
	seniorcar_command.steer_angle = 0
	seniorcar_command.max_velocity = 2.0
	enable_steer_motor = Bool()
	
	def __init__(self):
		rospy.init_node('generate_seniorca_comand_to_avoid_predicted_accident')
		self.pub = rospy.Publisher('seniorcar_command', SeniorcarState, queue_size=10)
		self.pub2 = rospy.Publisher('enable_motor', Bool, queue_size=10)
	
	def start_subscribe(self):
		rospy.Subscriber("seniorcar_state", SeniorcarState , self.stateCallback)
		
	def stateCallback(self,msg):
		self.seniorcar_state = msg
		self.seniorcar_command.max_velocity  = msg.max_velocity

	def update_seniorcar_command(self):

		self.seniorcar_command.steer_angle = self.seniorcar_state.steer_angle
		self.enable_steer_motor.data = False
		self.seniorcar_command.accel_opening = self.seniorcar_state.accel_opening
	
	def publish_command(self):
		rate = rospy.Rate(PUBLISH_RATE)
		while not rospy.is_shutdown():
			self.update_seniorcar_command()
			self.pub.publish(self.seniorcar_command)
			self.pub2.publish(self.enable_steer_motor)
			rate.sleep()

if __name__ == '__main__':
	calclater = GenerateSeniorcarCommand()
	calclater.start_subscribe()
	calclater.publish_command()