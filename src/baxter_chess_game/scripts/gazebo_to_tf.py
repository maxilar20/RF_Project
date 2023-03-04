#!/usr/bin/env python
import rospy
import tf
from gazebo_msgs.msg import LinkStates

input_linknames = None
poses = {}


def get_links_gazebo(link_states_msg):
    # global input_linkname
    global input_linknames
    global poses
    poses = {}
    
    if not input_linknames:
        try:
            input_linknames = rospy.get_param('piece_names')
        except:
            return
    for (link_idx, link_name) in enumerate(link_states_msg.name):
        modelname = link_name.split('::')[0]
        if modelname in input_linknames:
            poses[modelname] = link_states_msg.pose[link_idx]

def main():
    rospy.init_node('gazebo2tfframe')

    tfBroadcaster = tf.TransformBroadcaster()
    rospy.Subscriber('gazebo/link_states', LinkStates, get_links_gazebo)

    rospy.loginfo('Spinning')
    rate = rospy.Rate(20)
    while not rospy.is_shutdown():
        for name,pose in poses.items():
            pos = pose.position
            ori = pose.orientation
            rospy.loginfo(pos)
            tfBroadcaster.sendTransform((pos.x, pos.y, pos.z - 0.93), (ori.x, ori.y, ori.z, ori.w), rospy.Time.now(), name, 'world')
        rate.sleep()

    rospy.spin()


if __name__ == '__main__':
    main()