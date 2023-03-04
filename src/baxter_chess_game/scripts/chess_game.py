#!/usr/bin/env python
import sys
import copy
from copy import deepcopy


import rospy,rospkg,tf

from std_msgs.msg import (
    Empty,
)

from geometry_msgs.msg import (
    Pose,
    Point,
    Quaternion,
    PoseStamped
)

from gazebo_msgs.srv import (
    SpawnModel,
    DeleteModel,
)

import baxter_interface
import moveit_commander

class ChessGame(object):
    def __init__(self, limb, hover_distance=0.15, verbose=True):
        self._limb_name = limb  # string
        self._hover_distance = hover_distance  # in meters
        self._verbose = verbose  # bool
        self._limb = baxter_interface.Limb(limb)
        self._gripper = baxter_interface.Gripper(limb)
        print("Getting robot state... ")
        self._rs = baxter_interface.RobotEnable(baxter_interface.CHECK_VERSION)
        self._init_state = self._rs.state().enabled
        print("Enabling robot... ")

        self._robot = moveit_commander.RobotCommander()
        self._group = moveit_commander.MoveGroupCommander(limb+"_arm")

    def move_to_start(self, start_angles=None):
        print("Moving the {0} arm to start pose...".format(self._limb_name))

        self.gripper_open()
        self._group.set_pose_target(start_angles)
        plan = self._group.plan()
        self._group.execute(plan)
        rospy.sleep(1.0)
        print("Running. Ctrl-c to quit")

    def _guarded_move_to_joint_position(self, joint_angles):
        if joint_angles:
            self._limb.move_to_joint_positions(joint_angles)
        else:
            rospy.logerr("No Joint Angles provided for move_to_joint_positions. Staying put.")

    def gripper_open(self):
        self._gripper.open()
        rospy.sleep(1.0)

    def gripper_close(self):
        self._gripper.close()
        rospy.sleep(1.0)

    def _approach(self, pose):
        approach = copy.deepcopy(pose)
        approach.position.z = approach.position.z + self._hover_distance

        self._group.set_pose_target(approach)
        plan = self._group.plan()
        self._group.execute(plan)

    def _retract(self):
        # retrieve current pose from endpoint
        current_pose = self._limb.endpoint_pose()
        ik_pose = Pose()
        ik_pose.position.x = current_pose['position'].x
        ik_pose.position.y = current_pose['position'].y
        ik_pose.position.z = current_pose['position'].z + self._hover_distance
        ik_pose.orientation.x = current_pose['orientation'].x
        ik_pose.orientation.y = current_pose['orientation'].y
        ik_pose.orientation.z = current_pose['orientation'].z
        ik_pose.orientation.w = current_pose['orientation'].w

        # servo up from current pose
        self._group.set_pose_target(ik_pose)
        plan = self._group.plan()
        self._group.execute(plan)

    def _servo_to_pose(self, pose):
        # servo down to release
        self._group.set_pose_target(pose)
        plan = self._group.plan()
        self._group.execute(plan)

    def pick(self, pose):
        self.gripper_open()
        self._approach(pose)
        self._servo_to_pose(pose)
        self.gripper_close()
        self._retract()

    def place(self, pose):
        self._approach(pose)
        self._servo_to_pose(pose)
        self.gripper_open()
        self._retract()

    def tf_callback(self, pose_msg):
        print
        # block_pose_pick = Pose(
        #     position=Point(x=pose_msg.pose.position.x, y=pose_msg.pose.position.y, z=pose_msg.pose.position.z - 0.02),
        #     orientation=self.overhead_orientation)

        # picking_pose = Pose(position=Point(x=0.0, y=0.7, z=0.15),
        #     orientation=self.overhead_orientation)


def load_gazebo_models():
    rospy.wait_for_service("gazebo/spawn_sdf_model")

    srv_call = rospy.ServiceProxy("gazebo/spawn_sdf_model", SpawnModel)
    
    # Table
    model_path = rospkg.RosPack().get_path('baxter_sim_examples')+"/models/"
    table_xml = ''
    with open(model_path + "cafe_table/model.sdf", "r") as table_file:
        table_xml = table_file.read().replace('\n', '')

    table_pose=Pose(position=Point(x=0.73, y=0.4, z=0.0))
    try:
        spawn_sdf = rospy.ServiceProxy('/gazebo/spawn_sdf_model', SpawnModel)
        spawn_sdf("cafe_table", table_xml, "/", table_pose, "world")
    except rospy.ServiceException, e:
        rospy.logerr("Spawn SDF service call failed: {0}".format(e))
    
    
    # ChessBoard
    orient = Quaternion(*tf.transformations.quaternion_from_euler(0, 0, 0))
    board_pose = Pose(Point(0.3,0.55,0.78), orient)
    frame_dist = 0.025
    model_path = rospkg.RosPack().get_path('baxter_chess_game')+"/models/"
    
    with open(model_path + "chessboard/model.sdf", "r") as f:
        board_xml = f.read().replace('\n', '')

    # Add chessboard into the simulation
    print(srv_call("chessboard", board_xml, "", board_pose, "world"))

    # Add chesspieces into the simulation
    origin_piece = 0.03125

    pieces_xml = dict()
    list_pieces = 'rnbqkpRNBQKP'
    for each in list_pieces:
        with open(model_path + each+".sdf", "r") as f:
            pieces_xml[each] = f.read().replace('\n', '')
            

    board_setup = ['rnbqkbnr', 'pppppppp', '', '', '', '', 'PPPPPPPP', 'RNBQKBNR']
    #board_setup = ['r******r', '', '**k*****', '', '', '******K*', '', 'R******R']

    piece_positionmap = dict()
    piece_names = []
    for row, each in enumerate(board_setup):
        # print row
        for col, piece in enumerate(each):
            pose = deepcopy(board_pose)
            pose.position.x = board_pose.position.x + frame_dist + origin_piece + row * (2 * origin_piece)
            pose.position.y = board_pose.position.y - 0.55 + frame_dist + origin_piece + col * (2 * origin_piece)
            pose.position.z += 0.018
            piece_positionmap[str(row)+str(col)] = [pose.position.x, pose.position.y, pose.position.z-0.93] #0.93 to compensate Gazebo RViz origin difference
            if piece in list_pieces:
                name = "%s%d" % (piece,col)
                piece_names.append(name)
                # Add chessboard into the simulation
                print(srv_call(name, pieces_xml[piece], "", pose, "world"))
    
    rospy.set_param('board_setup', board_setup) # Board setup
    rospy.set_param('list_pieces', list_pieces) # List of unique pieces
    rospy.set_param('piece_target_position_map', piece_positionmap) # 3D positions for each square in the chessboard
    rospy.set_param('piece_names', piece_names) # Pieces that will be part of the game
    rospy.set_param('pieces_xml', pieces_xml) # File paths to Gazebo models, i.e. SDF files


def delete_gazebo_models():
    try:
        piece_names = rospy.get_param('piece_names')
    except:
        return
    
    rospy.wait_for_service("gazebo/delete_model")

    delete_model = rospy.ServiceProxy("gazebo/delete_model", DeleteModel)
    
    for piece in piece_names:
        print ("Deleting " + piece)
        delete_model(piece)

    delete_model("cafe_table")
    delete_model("chessboard")


def main():
    rospy.init_node("chess_game")
    delete_gazebo_models()
    load_gazebo_models()
    rospy.on_shutdown(delete_gazebo_models)

    rospy.wait_for_message("/robot/sim/started", Empty)

    limb = 'left'
    hover_distance = 0.15  # meters

    overhead_orientation = Quaternion(x=-0.0249590815779, y=0.999649402929, z=0.00737916180073, w=0.00486450832011)

    
    chess_game = ChessGame(limb, hover_distance)

    # Subscriber
    listener = tf.TransformListener()

    orient = Quaternion(*tf.transformations.quaternion_from_euler(0, 0, 0))
    starting_pose = Pose(Point(0.3,0.55,0.85), orient)
    
    chess_game.move_to_start(starting_pose)

    while not rospy.is_shutdown():
        chess_game.gripper_open()

        try:
            (trans,rot) = listener.lookupTransform('/world', '/p1', rospy.Time(0))
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            continue

        print("\nPicking...")
        block_pose = Pose(position = Point(x=trans[0],y=trans[1],z=trans[2]), orientation = overhead_orientation)
        chess_game.pick(block_pose)

    
    return 0

if __name__ == '__main__':
    sys.exit(main())
