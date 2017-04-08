from common.messaging import MessageContainer, Message

robot = MessageContainer(container_name="CHAMP")

robot.abdomen = robot.add_sub_container(MessageContainer(0, "Abdomen"))
robot.abdomen.w_pp = robot.abdomen.add_sub_container(MessageContainer(0, "W Push Pull"))
robot.abdomen.w_pp.set_extension = robot.abdomen.w_pp.add_message(Message(0, "Set Extension"))
robot.abdomen.s_pp = robot.abdomen.add_sub_container(MessageContainer(1, "S Push Pull"))
robot.abdomen.s_pp.set_extension = robot.abdomen.s_pp.add_message(Message(0, "Set Extension"))
robot.abdomen.x_pp = robot.abdomen.add_sub_container(MessageContainer(2, "X Push Pull"))
robot.abdomen.x_pp.set_extension = robot.abdomen.x_pp.add_message(Message(0, "Set Extension"))

robot.orange_gripper = robot.add_sub_container(MessageContainer(1, "Orange Gripper"))
robot.orange_gripper.grip = robot.orange_gripper.add_message(Message(0, "Grip"))
robot.orange_gripper.ungrip = robot.orange_gripper.add_message(Message(1, "Un Grip"))
robot.orange_gripper.rotate = robot.orange_gripper.add_message(Message(2, "Rotate"))

robot.green_gripper = robot.add_sub_container(MessageContainer(2, "Green Gripper"))
robot.green_gripper.grip = robot.green_gripper.add_message(Message(0, "Grip"))
robot.green_gripper.ungrip = robot.green_gripper.add_message(Message(1, "Un Grip"))
robot.green_gripper.rotate = robot.green_gripper.add_message(Message(2, "Rotate"))