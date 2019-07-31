import rospy
import time
import serial
from multiprocessing import Process, Value

def conecct_with_arduino_process(palse_count):

	port = rospy.get_param('rocker_encorder_port',"")
	try:
		ser = serial.Serial(port,timeout=0.05)
		ser.setDTR(False)
		time.sleep(1)
		ser.setDTR(True)
		print "start connection with rotarty encoder"
	except:
		print "cannot start connection with rotarty encoder"

	time.sleep(1)

	ser.write("s");

	while  not rospy.is_shutdown():
		try:
			line  = ser.readline().rstrip()
			if len(line) > 0:
				if line.isdigit():
					palse_count.value = int(line)
				elif line[0] == "-":
					if line[1:].isdigit():
						palse_count.value = int(line)
		except KeyboardInterrupt:
			print "Ctrl+C"
			break

	print "End Falg Send"
	ser.write("e");

	ser.close()

if __name__ == '__main__':
