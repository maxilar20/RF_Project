Instructions:

1.- Download and extract the folder

2.- Open a terminal and access the workspace: $cd RF_Project

3.- Use the command: $catkin_make to compile the project and create the build folder

4.- Enter: $cd and then: $source ~/RF_Project/devel/setup.bash

5.- Use the following command to edit the setup.bash and add the source: $nano ~/.bashrc and add: source ~/RF_Project/devel/setup.bash at the end of the file.

6.- Now open three terminals and run the following commands:

**Terminal 1:**
roslaunch baxter_gazebo baxter_world.launch
Note: Please wait until it displays: "Robot is disabled"

**Terminal 2:**
roslaunch baxter_chess_game baxter_chess_game.launch

**Terminal 3:**
rosrun baxter_chess_game chess_game.py


Any questions you can contact us:
Mael Dorne: 2806329d@student.gla.ac.uk
Ernesto Flores: 2659823F@student.gla.ac.uk
