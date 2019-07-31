#!/usr/bin/env python
# coding: UTF-8

import rospy
import math
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PoseWithCovarianceStamped

recorded_xypoints = [] 


def callback(data):
# 設定した範囲内にある点群の数をカウントし、点が4つ以上あれば障害物があると判定
    data_num = len(data.ranges)
    print "num_of_data = %d" % len(data.ranges)

        #LRF極座標データを直行座標データに変換(x,y)
    for i in range(0,data_num-1):
        x = data.ranges[i] * math.sin( data.angle_min + data.angle_increment * i )
        y = data.ranges[i] * math.cos( data.angle_min + data.angle_increment * i )

        recorded_xypoints.append(str(x) + ",")
        recorded_xypoints.append(str(y) + " ")


def output_to_txt():
    f=open('xyplot6.txt','w')

    #print "num_of_data = %d" % len(data.ranges)
    for i in range(0,len(recorded_xypoints)-1):
        mod = (i+1) % (734*2)
        if mod == 0 and not (i+1) == 0:
            f.write(str(recorded_xypoints[i]) )
            f.write("\n")
        else:
            f.write(str(recorded_xypoints[i]) )
            f.write("\t")
     

    f.close()

def listener():

    rospy.init_node('detect_object', anonymous=True)

        #odom_topic = rospy.get_param('odom_topic',"/amcl_pose")

    rospy.Subscriber("scan_front", LaserScan, callback)

    rospy.spin()

    output_to_txt()

if __name__ == '__main__':
    listener()