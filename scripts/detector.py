#!/usr/bin/env python
    
from array import array
import rospy
from visualization_msgs.msg import Marker
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PointStamped
from geometry_msgs.msg import Point
from getfrontier import getfrontier
from std_msgs.msg import ColorRGBA

# custom msg
from frontier_based_exploration.msg import PointArray

import sys
sys.setrecursionlimit(10**7)

mapData = OccupancyGrid()

def mapCallback(data):
    global mapData
    global map_topic

    mapData = data
    rospy.loginfo(rospy.get_caller_id() + "// " + map_topic + " map data is currently received")
    
def detector_node():
    global mapData

    #--------- init ---------------
    rospy.init_node('detector', anonymous = False)
    rospy.loginfo_once("---- 'detector' node is loaded. ----")
    #------------------------------
    
    #--------- subscriber ------
    # http://wiki.ros.org/ROS/Tutorials/WritingPublisherSubscriber%28python%29
    # http://wiki.ros.org/rospy/Overview/Parameter%20Server

    global map_topic
    map_topic = rospy.get_param('~map_topic')
    rospy.loginfo_once("----- Requested map topic is " + map_topic + " -----")

    # rospy.Publisher(topic_name, msg_class, queue_size)
    rospy.Subscriber(map_topic, OccupancyGrid, mapCallback)
    #------------------------------
    
    #--------- Publisher ----------
    marker_pub = rospy.Publisher("marker", Marker, queue_size=10) # marker publish for Visualization
    target_pub = rospy.Publisher('/detected_points', PointStamped, queue_size=10) # publish for Assign
    #------------------------------

    

    while mapData.header.seq<1 or len(mapData.data)<1:
        pass

    rate = rospy.Rate(30)

    #----- rviz visualization -----
    # https://velog.io/@717lumos/Rviz-Rviz-%EC%8B%9C%EA%B0%81%ED%99%94%ED%95%98%EA%B8%B0-Marker
    exploration_goal = PointStamped()
    #------------------------------

    

    p = Point()
    

    while not rospy.is_shutdown():

        #----- rviz visualization -----
        frontier_points = Marker()
        # print("new : ", frontier_points.points)

        frontier_points.header.frame_id = mapData.header.frame_id
        frontier_points.header.stamp=rospy.Time.now()
        frontier_points.ns = "points"

        if(mapData.header.frame_id == 'robot_1/map'):
            frontier_points.id = 0
        if(mapData.header.frame_id == 'robot_2/map'):
            frontier_points.id = 1
        if(mapData.header.frame_id == 'robot_3/map'):
            frontier_points.id = 2
        
        frontier_points.type = Marker.POINTS
        frontier_points.action = Marker.ADD

        frontier_points.pose.orientation.w = 1.0
        frontier_points.scale.x = 0.15
        frontier_points.scale.y = 0.15
        frontier_points.color = ColorRGBA(1, 1, 0, 1)
        frontier_points.lifetime == rospy.Duration()
    #------------------------------

        # getfrontier.py Node
        frontiers = getfrontier(mapData)
        # print("while Processing...")
        
        arraypoints = PointArray()
        for i in range(len(frontiers)):
            x=frontiers[i]
            
            exploration_goal.header.frame_id = mapData.header.frame_id
            exploration_goal.header.stamp = rospy.Time(0)
            exploration_goal.point.x = x[0]
            exploration_goal.point.y = x[1]
            exploration_goal.point.z = 0

            p.x = x[0]
            p.y = x[1]
            p.z = 0

            frontier_points.points.append(Point(frontiers[i][0],frontiers[i][1],0))
            arraypoints.points.append(Point(frontiers[i][0],frontiers[i][1],0))

            target_pub.publish(exploration_goal) # for assigner

        marker_pub.publish(frontier_points) # for Visualization
        # target_pub.publish(arraypoints) # for assigner

        rate.sleep()

if __name__ == '__main__':
    try:
        detector_node()
    except rospy.ROSInterruptException:
        pass