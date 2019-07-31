#!/usr/bin/env python
# coding: UTF-8

# this program was written to read serial data of rotally encoder.

import rospy
import time
import serial
import math
import tf
from multiprocessing import Process, Value

from std_msgs.msg import Float64


PALUSE_NUM_PER_ROTATION = 360 # to be comfirm


port = rospy.get_param('Encorder_port',"/dev/ttyUSB0")#if parameter don't exist,second argument is taken.
try:
	ser = serial.Serial(port,baudrate=115200,timeout=0.05,)
	ser.setDTR(False)
	time.sleep(1)
	ser.setDTR(True)
	print "start connection with rotarty encoder"
except:
	print "cannot start connection with rotarty encoder"


def conecct_with_arduino_process(pulse_count):


	time.sleep(1)

	

	while  not rospy.is_shutdown():
		try:
			line  = ser.readline().rstrip()
			if len(line) > 0:
				if line.isdigit():
					pulse_count.value = int(line)
				elif line[0] == "-":
					if line[1:].isdigit():
						pulse_count.value = int(line)
		except KeyboardInterrupt:
			print "Ctrl+C"
			break

	print "End Falg Send"
	ser.write("e");

	ser.close()


def calculate_odometory_process(pulse_count,):

	rospy.init_node('Encoder_connecter', anonymous=True)
	br = tf.TransformBroadcaster()
	pub = rospy.Publisher('rotational_speed', Float64 , queue_size=10)
	rate = rospy.Rate(50.0)#50Hz


	while not rospy.is_shutdown():
		try:
			rotational_speed = 2.0 * 3.14 * float(pulse_count.value) / PALUSE_NUM_PER_ROTATION#pulse_count[num/sec],rotational_speed[rad/sec]
			ser.write("r");
			pub.publish(rotational_speed)
			rate.sleep()
			print pulse_count.value
		except KeyboardInterrupt:
			print "End TF process"
			break


if __name__ == '__main__':
	pulse_count = Value('d',0)#this means that generate object which have a compatible data type(data type is double) and dont lock the object.(to communicate esp_boad)
	connect_process = Process( target = conecct_with_arduino_process , args = (pulse_count,) )
	calculate_process = Process( target = calculate_odometory_process, args = (pulse_count,) )
	try:
		connect_process.start()
		calculate_process.start()
	except rospy.ROSInterruptException:
		pass