#!/usr/bin/env python
# coding: UTF-8

import rospy
import time
import serial
import sys
from std_msgs.msg import Int8
from std_msgs.msg import Bool
from std_msgs.msg import String
from ultimate_seniorcar.msg import SeniorcarState

target_steer_angle = 0.0
state_steer_angle = 0.0
send_str = ""

MAX_DIV_ANGLE = 5#20
GERA_CONSTANT = 3000.0 * 160.0 * 1.561 / 360.0

MAX_STEER_ANGLE = 40

enable_motor = True#180411_AutoDrive
#enable_motor = False#180512_avoid

def callback(data):
	global target_steer_angle
	target_steer_angle = max( -MAX_STEER_ANGLE , min ( data.steer_angle ,MAX_STEER_ANGLE ) )

def state_callback(data):
	global state_steer_angle
	state_steer_angle = data.steer_angle

def enable_motor_callback(data):
	global enable_motor
	enable_motor = data.data

def connect_with_arduino():
	global send_str
	port = rospy.get_param('steer_motor_port',"/dev/ttyUSB1")
	pub = rospy.Publisher('motor_controller_input', String, queue_size=10)
	pub_str = String()
	print port
	try:
		ser = serial.Serial(port,9600)
		ser.setDTR(False)
		time.sleep(1)
		ser.setDTR(True)
		print "start connection with steer_motor"

	except:
		print "cannot start connection with steer_motor"
		sys.exit()

	time.sleep(2)
	rate = rospy.Rate(100)

	count = 0
	while count < 4:
		count += 1
		send_zero_to_steer_motor(ser)
		rate.sleep()

	print "Did You Turn On a Motor Switch??"

	wait_count = 0
	while  not wait_count > 200:
		ser.write("EN\n")
		ser.write("NP\n")
		while ser.inWaiting() > 0:
			if ser.read() == "p":
				ser.write("EN\n")
				send_devision_to_steer_motor(ser)				
				pub_str.data = send_str[:-1]
				pub.publish(pub_str)
		rate.sleep()
		wait_count = wait_count + 1


	print "Control Start"

	while  not rospy.is_shutdown():
		if enable_motor == True:
			ser.write("NP\n")
			while ser.inWaiting() > 0:
				if ser.read() == "p":
					ser.write("EN\n")
					send_devision_to_steer_motor(ser)				
					pub_str.data = send_str[:-1]
					pub.publish(pub_str)
		else:
			ser.write("DI\n")

		rate.sleep()

	ser.close()


def send_devision_to_steer_motor(ser):

	global send_str

	target_value = (state_steer_angle - target_steer_angle) * GERA_CONSTANT#max( -MAX_DIV_ANGLE , min( state_steer_angle - target_steer_angle , MAX_DIV_ANGLE ) ) * GERA_CONSTANT
	send_str = "LR" + str(int(target_value)) + "\n"
	rospy.loginfo(send_str)
	ser.write(send_str)
	ser.write("M\n")

def send_zero_to_steer_motor(ser):

	target_value = 0
	send_str = "LA" + str(int(target_value)) + "\n"
	rospy.loginfo(send_str)
	ser.write(send_str)
	ser.write("M\n")
	#ser.write("SP24\n")

if __name__ == '__main__':
	rospy.init_node('steer_motor')
	time.sleep(1)
	rospy.Subscriber("seniorcar_command", SeniorcarState, callback)
	rospy.Subscriber("seniorcar_state", SeniorcarState, state_callback)
	rospy.Subscriber("enable_motor", Bool, enable_motor_callback)#when you want to do auto drive,please comment out this sentence.
	connect_with_arduino()