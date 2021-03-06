#!/usr/bin/env python
# coding: UTF-8

# CANを上書きしてユーザの操作をそのまま入力するノード
# 上書き中の移動用

import rospy
from geometry_msgs.msg import Twist
from ultimate_seniorcar.msg import AccidentPredictResult
from ultimate_seniorcar.msg import SeniorcarState
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool

PUBLISH_RATE = 10.0       # コマンドをパブリッシュする周期

APPROACH_THRESHOLD = 2.5  # 何mまで危険な領域に直進で接近させるか
AVOID_THRESHOLD = 3.0     # 避けるとしたら何mまで余裕がある角度か

NO_INTERVATION_DISTANCE = 3.7    # 足元の情報がないため介入しない原点からの距離

DECELERATION_CONSTANT = 0.3 # 減速時に入力アクセル開度に対し何倍のアクセル開度を出力するか（0~1）


class AvoidPredictedAccident:

	accident_predict_result = AccidentPredictResult()
	seniorcar_odometry = Odometry()
	seniorcar_state   = SeniorcarState()
	seniorcar_command = SeniorcarState()
	seniorcar_command.accel_opening = 0
	seniorcar_state.accel_opening = 0
	seniorcar_command.steer_angle = 0
	seniorcar_command.max_velocity = 2.0
	enable_steer_motor = Bool()
	
	start_odometry = Odometry()
	odom_recive_flag = True

	def __init__(self):
		rospy.init_node('generate_seniorca_comand_to_avoid_predicted_accident')
		self.pub = rospy.Publisher('seniorcar_command', SeniorcarState, queue_size=10)
		self.pub2 = rospy.Publisher('enable_motor', Bool, queue_size=10)
	
	def subscribe_predicted_result(self):
		rospy.Subscriber("accident_predict", AccidentPredictResult , self.accidentsubCallback)
		rospy.Subscriber("seniorcar_state", SeniorcarState , self.stateCallback)
		rospy.Subscriber("seniorcar_odometry", Odometry, self.odomCallback)

	def stateCallback(self,msg):
		self.seniorcar_state = msg
		self.seniorcar_command.max_velocity  = msg.max_velocity

	def odomCallback(self,msg):
		if self.odom_recive_flag:
			self.start_odometry = msg
			print "start_odometry"
			print "x:" + str(self.start_odometry.pose.pose.position.x) + "y:" +  str(self.start_odometry.pose.pose.position.y) 
			self.odom_recive_flag = False
		self.seniorcar_odometry = msg

	def accidentsubCallback(self,msg):
		self.accident_predict_result = msg
		self.min_predict_angle = msg.steer_angle[0]
		self.predict_angle_devision = abs( msg.steer_angle[1] - msg.steer_angle[0] )

	def calcSteerAngleToPredictedAngleIndex(self,steer_angle):
		# radに直す
		steer_angle *= 3.14 / 180
		# まだ判定結果を受信していない場合は0を返す
		if len(self.accident_predict_result.steer_angle) < 1:
			return 0
		# 範囲外の処理
		elif steer_angle < self.accident_predict_result.steer_angle[0]:
			return 0
		elif steer_angle > self.accident_predict_result.steer_angle[-1]:
			return int( len(self.accident_predict_result.steer_angle) - 1 )
		else:
			return int( ( steer_angle - self.accident_predict_result.steer_angle[0] ) / ( self.accident_predict_result.steer_angle[1] - self.accident_predict_result.steer_angle[0] ) )

	def update_seniorcar_command(self):

		self.seniorcar_command.steer_angle = self.seniorcar_state.steer_angle
		self.enable_steer_motor.data = False
		self.seniorcar_command.accel_opening = self.seniorcar_state.accel_opening
	
	def calculate_and_publish_command(self):
		rate = rospy.Rate(PUBLISH_RATE)
		while not rospy.is_shutdown():
			# 最初は足元の情報がないので介入なし
			if pow( self.seniorcar_odometry.pose.pose.position.x - self.start_odometry.pose.pose.position.x , 2 ) +  pow( self.seniorcar_odometry.pose.pose.position.y - self.start_odometry.pose.pose.position.y , 2 )  < pow( NO_INTERVATION_DISTANCE , 2 ):
				self.enable_steer_motor.data = False
				self.seniorcar_command.accel_opening = self.seniorcar_state.accel_opening
				self.seniorcar_command.steer_angle = self.seniorcar_state.steer_angle
			else:
				self.update_seniorcar_command()
			self.pub.publish(self.seniorcar_command)
			self.pub2.publish(self.enable_steer_motor)
			rate.sleep()

if __name__ == '__main__':
	calclater = AvoidPredictedAccident()
	calclater.subscribe_predicted_result()
	calclater.calculate_and_publish_command()
