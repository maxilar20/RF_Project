**Terminal 1:**
roslaunch baxter_gazebo baxter_world.launch

**Terminal 2:**
roslaunch baxter_chess_game baxter_chess_game.launch

**Terminal 3:**
rosrun baxter_chess_game chess_game.py

Terminal 2:
rosrun baxter_tools enable_robot.py -e
rosrun baxter_interface joint_trajectory_action_server.py

Terminal 3:
roslaunch baxter_moveit_config baxter_grippers.launch

Terminal 4:
rosrun baxter_chess_game pick_and_place_moveit.py

TEST: Terminal 5:
rosrun baxter_chess_game gazebo_to_tf.py
rosrun baxter_chess_game spawn_chessboard.py

TODO: 
- Change spawn to an action
- Change despawn to an action