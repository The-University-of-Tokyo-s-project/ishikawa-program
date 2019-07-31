#!/usr/bin/env python
# coding: UTF-8

import rospy
import math
from sensor_msgs.msg import LaserScan
from ultimate_seniorcar.msg import GoBack
from ultimate_seniorcar.msg import SeniorcarState


#前後で別々のPythonスクリプトファイルを作り、そこから送られたトピックを元にセニアカーを動かす

pub = rospy.Publisher('is_go',GoBack , queue_size=10)


def callback(data):
	data_num = len(data.ranges)
	obj_count = 0

	for i in range(0,data_num-1):
		if data.ranges[i] < 4.0 and data.ranges[i] > 0.2 :
			x = data.ranges[i] * math.sin( data.angle_min + data.angle_increment * i )
			y = data.ranges[i] * math.cos( data.angle_min + data.angle_increment * i )
			print x,y
			if 0.0 < y and y < 2.0:
				if -0.3 < x and x < 0.3:
					obj_count += 1

	pub_command = GoBack()

	if obj_count > 40:
		pub_command.go = 1
	if obj_count < 40:
		pub_command.go = 0
	
	pub.publish(pub_command)


def listener():
  rospy.init_node('listener', anonymous=True)

  rospy.Subscriber("scan_front", LaserScan, callback)

  #rospy.Subscriber("/keyboard/keydown", Key, callback)

  # spin() simply keeps python from exiting until this node is stopped
  rospy.spin()




if __name__ == '__main__':
  listener()
