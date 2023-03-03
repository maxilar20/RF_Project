#!/usr/bin/env python
import sys
import copy

import rospy
import rospkg

from std_msgs.msg import (
    Empty,
)

from geometry_msgs.msg import (
    Pose,
    Point,
    Quaternion,
)

from gazebo_msgs.srv import (
    SpawnModel,
    DeleteModel,
)

import baxter_interface
import moveit_commander


class ChessGame(object):
    def __init__(self, verbose=True):
        self.piece_positions = [(1,1)]

def main():
    rospy.init_node("chess_game")

    chess_game = ChessGame()

    while not rospy.is_shutdown():
        print(f"\n {chess_game.piece_positions}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
