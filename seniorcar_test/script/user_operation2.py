#!/usr/bin/env python
# coding: UTF-8

# CANを上書きしてユーザの操作をそのまま入力するノード
# 上書き中の移動用

import rospy
from ultimate_seniorcar.msg import SeniorcarState
from std_msgs.msg import Bool

PUBLISH_RATE = 10.0       # コマンドをパブリッシュする周期

class PublishSeniorcarCommand:

	def __init__(self):
		rospy.init_node('generate_seniorca_comand_to_avoid_predicted_accident')
		self.pub = rospy.Publisher('seniorcar_command', SeniorcarState, queue_size=10)
		self.pub2 = rospy.Publisher('enable_motor', Bool, queue_size=10)
		rospy.Subscriber("seniorcar_state", SeniorcarState , self.stateCallback)
		rospy.spin()
		
	def stateCallback(self,msg):
		self.pub.publish(msg)
		self.pub2.publish(False)

if __name__ == '__main__':
	pub_com = PublishSeniorcarCommand()