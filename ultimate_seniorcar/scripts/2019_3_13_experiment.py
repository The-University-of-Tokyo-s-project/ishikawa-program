#!/usr/bin/env python
# coding: UTF-8

import rospy
from std_msgs.msg import Int8
from std_msgs.msg import Bool
from ultimate_seniorcar.msg import SeniorcarState

class playRecordedorder:
	speed_array = []
	steer_array = []
	seniorcar_command =SeniorcarState()
	enable_motor = Bool()
	enable_motor.data = True
	seniorcar_command.accel_opening = 0
	seniorcar_command.steer_angle = 0
	seniorcar_command.max_velocity = 0
	index = 0

	def __init__(self):
		rospy.init_node('play_recorded_order')
		self.get_order_from_txt()
		self.pub = rospy.Publisher('seniorcar_command', SeniorcarState, queue_size=10)
		self.pub2 = rospy.Publisher('enable_motor', Bool, queue_size=10)

	def get_order_from_txt(self):

        filename = rospy.get_param('command_array_file_path',"/home/ishikawa/catkin_ws/suzuki_demo/command_array.txt")
        print "open " + str(filename)

        f=open(filename,'r')
        num = 0

        for i in f.readlines():
        
            #print i
            i=i.strip()         #末尾の改行を除去
            i=i.split("\t")     #空白(tab)で文字列を区切り、リストを作成

            

            speed = float(i[0])
            steer = float(i[1])

            self.speed_array.append(speed)
            self.steer_array.append(steer)
            num += 1

            print pose_info

        f.close()
        print "success to load %d command_array" % num

        

    def update_order
    	if len(speed_array) -1 > self.index:
    		self.seniorcar_command.max_velocity = self.speed_array[self.index] * 3.6
    		self.seniorcar_command.accel_opening = 127
    		self.seniorcar_command.steer_angle = self.steer_array[self.index]
    		self.index += 1

    	else:
    		self.seniorcar_command.accel_opening = 0
    		self.enable_motor.data = False
    		rospy.on_shutdown(self.print_finish)



    def calculate_and_publish_cmd_vel(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            self.update_order()
            self.pub.publish(self.seniorcar_command)
            self.pub.publish(self.enable_motor)
            rate.sleep()

    def print_finish
    	print "finish auto driving"

if __name__ == '__main__':
	processor = playRecordedorder()
	processor.calculate_and_publish_cmd_vel()