#!/usr/bin/env python
# coding: UTF-8

import numpy
import matplotlib.pyplot as plt
import math


FILE_PATH = '/media/ishikawa/DATAPART1/HDD/bagfiles/grass_road/1/tilt1.txt'

NAN = -1.0
INF = -2.0

class ProcessLaserData:

	range_data_array = []
	inversed_range_data_array = []	# [角度][時間]になるように反転
	compensented_array = []	# 角度で距離を補正したデータ
	ARRAY_NUM = 0
	RANGE_DATA_NUM = 0

	angle_array = []

	def __init__(self):

		self.readFile()
		self.disposalValues()
		#self.outputConsole()
		self.showGraph(261)
		#self.calculateVariance()
		#self.caluculateMean()
		#self.showMaxDistance()


	def readFile(self):

		f = open(FILE_PATH,'r')
		num = 1

		for line in f.readlines():

			line = line.strip()        #末尾の改行を除去
			
			if num %16 == 14:
				lis = line.split(",")
				tmp_i = 0
				tmp_array = []
				for data in lis:
					lis[tmp_i] = lis[tmp_i].lstrip()
					tmp_array.append(lis[tmp_i])
					tmp_i += 1
				self.range_data_array.append(tmp_array)
				self.ARRAY_NUM += 1
				self.RANGE_DATA_NUM = tmp_i

			elif num == 7:
				lis = line.split(":")
				self.angle_min =  float(lis[1].lstrip())

			elif num == 8:
				lis = line.split(":")
				self.angle_max =  float(lis[1].lstrip())

			elif num == 9:
				lis = line.split(":")
				self.angle_increment =  float(lis[1].lstrip())

			
			num += 1

		f.close()

		print self.RANGE_DATA_NUM,self.ARRAY_NUM
		for j in range(0,self.RANGE_DATA_NUM):
			self.angle_array.append( (self.angle_min + self.angle_increment * j)*180 )
		print self.angle_array


	def disposalValues(self):

		for i in range(0,self.ARRAY_NUM):
			self.range_data_array[i][0] = -1.0
			self.range_data_array[i][self.RANGE_DATA_NUM-1] = -1.0
			for j in range(1,self.RANGE_DATA_NUM-1):
				if self.range_data_array[i][j] == 'nan':
					self.range_data_array[i][j] = NAN
				elif self.range_data_array[i][j] == 'inf':
					self.range_data_array[i][j] = INF
				else:
					self.range_data_array[i][j] = float(self.range_data_array[i][j])

		for j in range(0,self.RANGE_DATA_NUM):
			tmp_array = []
			tmp_compensented_array = []
			for i in range(0,self.ARRAY_NUM):
				# NAN,INFは除いたデータにする
				if 0.01 < self.range_data_array[i][j] and self.range_data_array[i][j] < 2.0:
					#tmp_array.append(self.range_data_array[i][j])
					tmp_array.append(self.range_data_array[i][j] * math.cos(self.angle_min + self.angle_increment * j))
					tmp_compensented_array.append(self.range_data_array[i][j] * math.cos(self.angle_min + self.angle_increment * j) )
			self.inversed_range_data_array.append(tmp_array)
			self.compensented_array.append(tmp_compensented_array)


	# csvの形で出力したいときに
	def outputConsole(self):

		for arr in self.range_data_array:
			for ranges in arr:
				print str(ranges) + ",",
			print ","

		print self.ARRAY_NUM,self.RANGE_DATA_NUM


	def showGraph(self,index):

		width = 0.02
		max_distance = 2.0
		min_distance = 0.5

		plt.hist(self.inversed_range_data_array[index],bins = (max_distance-min_distance)/width, range = (min_distance, max_distance))
		plt.title("Histgram at " + ('%03.1f' % self.angle_array[index]) +" degree")
		plt.xlabel("range")
		plt.xlim(min_distance,max_distance)
		plt.ylabel("frequency")
		plt.show()


	def calculateVariance(self):

		variance_array = []

		for j in range(0,self.RANGE_DATA_NUM):
			variance_array.append(numpy.var(self.inversed_range_data_array[j]))

		#print variance_array
		plt.plot(self.angle_array, variance_array, color="k", marker="o")
		plt.title("Variance of distance values")
		plt.xlabel("laser angle [deg]")
		plt.xlim(-150,150)
		plt.ylabel("variance []")
		plt.show()


	def caluculateMean(self):

		mean_array = []

		for j in range(0,self.RANGE_DATA_NUM):
			if len(self.inversed_range_data_array[j]) > 0:
				mean_array.append(sum(self.inversed_range_data_array[j])/len(self.inversed_range_data_array[j]))
			else:
				mean_array.append(0)

		#print variance_array
		plt.plot(self.angle_array, mean_array, color="k", marker="o")
		plt.title("Mean distance value")
		plt.xlabel("laser angle [deg]")
		plt.xlim(-150,150)
		plt.ylabel("distance [m]")
		plt.show()


	def showMaxDistance(self):

		max_distance_array = []

		for j in range(0,self.RANGE_DATA_NUM):
			max_range = 0.0
			for i in range(0,len(self.compensented_array[j])):
				if self.compensented_array[j][i] > max_range:
					max_range = self.compensented_array[j][i]
			max_distance_array.append(max_range)

		plt.plot(self.angle_array, max_distance_array, color="k", marker="o")
		plt.title("Max distance value")
		plt.xlabel("laser angle [deg]")
		plt.xlim(-150,150)
		plt.ylabel("distance [m]")
		plt.show()



if __name__ == '__main__':

	process = ProcessLaserData()
