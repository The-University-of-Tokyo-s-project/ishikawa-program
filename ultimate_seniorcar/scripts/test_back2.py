#!/usr/bin/env python
# license removed for brevity
import rospy
import math
from sensor_msgs.msg import LaserScan
from ultimate_seniorcar.msg import SeniorcarState

pub = rospy.Publisher('seniorcar_command',SeniorcarState, queue_size = 10)


pub_command = SeniorcarState()



def callback1(data):
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


	pub_command.accel_opening = 100

	if obj_count > 40:

		pub_commnd.direction_switch = 1
		

	

	pub.publish(pub_command)


def callback2(data):
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

	

	pub_command.accel_opening = 100

	if obj_count > 40:

		pub_commnd.direction_switch = 0
		

	

	pub.publish(pub_command)


def listener():
  rospy.init_node('listener', anonymous=True)

  

  rospy.Subscriber("scan_front", LaserScan, callback1)



  rospy.Subscriber("scan_back", LaserScan, callback2)

  #rospy.Subscriber("/keyboard/keydown", Key, callback)

  # spin() simply keeps python from exiting until this node is stopped
  rospy.spin()




if __name__ == '__main__':
  listener()