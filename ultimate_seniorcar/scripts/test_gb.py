#!/usr/bin/env python
# coding: UTF-8
import rospy
import math
from sensor_msgs.msg import LaserScan
from ultimate_seniorcar.msg import SeniorcarState

pub = rospy.Publisher('seniorcar_command',SeniorcarState, queue_size = 10)

def callback(data):
	is_go = data.go
	is_back = data.back

	
	pub_command = SeniorcarState()

	if　#自作のメッセージで条件付け（前進と後退のに項目について０，１の判別で４通り）:

		pub_commnd.direction_switch = 1
		pub_command.accel_opening = 100

	

	pub.publish(pub_command)





def listener():
  rospy.init_node('listener', anonymous=True)

  rospy.Subscriber("is_go_back", #自作のやつ, callback)


  rospy.spin()




if __name__ == '__main__':
  listener()
