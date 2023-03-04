#! /usr/bin/env python

import rospy

import actionlib

import baxter_chess_game.msg

class MoveBaxter():
    _feedback = baxter_chess_game.msg.move_baxterFeedback()
    _result = baxter_chess_game.msg.move_baxterResult()

    def __init__(self, name):
        self._action_name = name
        self._as = actionlib.SimpleActionServer(self._action_name, baxter_chess_game.msg.move_baxterAction, execute_cb=self.execute_cb, auto_start = False)
        self._as.start()
      
    def execute_cb(self, goal):
        self._feedback.distance = 15        
        
        r = rospy.Rate(1)
        for i in range(1, goal.goal_pos):
            if self._as.is_preempt_requested():
                self._as.set_preempted()
                break
            
            print(i)
            self._feedback.distance = i
            self._as.publish_feedback(self._feedback)
            r.sleep()

        self._result.completed = True
        self._as.set_succeeded(self._result)
        
if __name__ == '__main__':
    rospy.init_node('move_baxter')
    server = MoveBaxter(rospy.get_name())
    rospy.spin()
