from oi.core.gui.gui_base import Ui_gui
from PyQt5 import QtCore, QtWidgets
from common.messaging import MessagePasser


class Controller(Ui_gui, MessagePasser):

    def __init__(self, dialog, commands_container):
        Ui_gui.__init__(self)
        MessagePasser.__init__(self)
        self.setupUi(dialog)  # from super
        self.name = "UI"

        self.commands_container = commands_container

        self.init_debug_table()

        self.send_toggle_button(self.toggle_og_pushButton, self.commands_container.grip_orange_gripper)
        self.send_toggle_button(self.toggle_gg_pushButton, self.commands_container.grip_green_gripper)

        linked_controls = [
            [self.wpp_target_upper_verticalSlider, self.wpp_target_lower_verticalSlider, self.wpp_target_spinBox],
            [self.wpp_actual_upper_verticalSlider, self.wpp_actual_lower_verticalSlider, self.wpp_actual_spinBox],
            [self.spp_target_upper_verticalSlider, self.spp_target_lower_verticalSlider, self.spp_target_spinBox],
            [self.spp_actual_upper_verticalSlider, self.spp_actual_lower_verticalSlider, self.spp_actual_spinBox],
            [self.xpp_target_upper_verticalSlider, self.xpp_target_lower_verticalSlider, self.xpp_target_spinBox],
            [self.xpp_actual_upper_verticalSlider, self.xpp_actual_lower_verticalSlider, self.xpp_actual_spinBox],
            [self.og_target_angle_dial, self.og_target_angle_spinbox],
            [self.gg_target_angle_dial, self.gg_target_angle_spinbox],
            [self.og_actual_angle_dial, self.og_actual_angle_spinbox],
            [self.gg_actual_angle_dial, self.gg_actual_angle_spinbox],
            [self.speedfactor_horizontalSlider, self.speedfactor_spinBox],
            [self.drive_angle_dial, self.drive_angle_spinBox]
        ]
        for control_group in linked_controls:
            self.link_values(control_group)

        value_change_to_command_pairs = [
            [self.wpp_target_upper_verticalSlider, self.commands_container.set_w_pp_extension],
            [self.spp_target_upper_verticalSlider, self.commands_container.set_s_pp_extension],
            [self.xpp_target_upper_verticalSlider, self.commands_container.set_x_pp_extension],
            [self.og_target_angle_dial, self.commands_container.rotate_orange_gripper],
            [self.gg_target_angle_dial, self.commands_container.rotate_green_gripper],
        ]
        for pair in value_change_to_command_pairs:
            self.value_change_send_command(pair[0], pair[1])

        self.inc_all_rods_pushButton.clicked.connect(lambda state, delta_value=self.mod_rods_inc_spinBox: self.change_all_rods(True, delta_value.value()))
        self.dec_all_rods_pushButton.clicked.connect(lambda state, delta_value=self.mod_rods_inc_spinBox: self.change_all_rods(False, delta_value.value()))

        self.wpp_set_others_pushButton.clicked.connect(lambda: self.set_all_rods_to_given(self.wpp_target_upper_verticalSlider.value()))
        self.spp_set_others_pushButton.clicked.connect(lambda: self.set_all_rods_to_given(self.spp_target_upper_verticalSlider.value()))
        self.xpp_set_others_pushButton.clicked.connect(lambda: self.set_all_rods_to_given(self.xpp_target_upper_verticalSlider.value()))

    def set_all_rods_to_given(self, value):
        rods = [self.wpp_target_upper_verticalSlider,
                self.spp_target_upper_verticalSlider,
                self.xpp_target_upper_verticalSlider
        ]
        for rod in rods:
            rod.setValue(value)

    def change_all_rods(self, is_increase, delta):

        rods = [self.wpp_target_upper_verticalSlider,
                self.spp_target_upper_verticalSlider,
                self.xpp_target_upper_verticalSlider
        ]

        for rod in rods:

            current_value = int(rod.value())

            if is_increase:
                current_value += delta
            else:
                current_value -= delta

            rod.setValue(current_value)

    def init_debug_table(self):

        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Command", "Input"])

        for robot_command in self.commands_container.command_list:

            target_row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(target_row)

            action_button = QtWidgets.QPushButton(robot_command.name)
            self.tableWidget.setCellWidget(target_row, 0, action_button)

            if robot_command.takes_input:
                user_input = QtWidgets.QLineEdit()
                action_button.clicked.connect(lambda state, r=robot_command, i=user_input: self.add_to_partner(r.set_payload(i.text())))
            else:
                user_input = QtWidgets.QLabel("NONE")
                user_input.setAlignment(QtCore.Qt.AlignCenter)
                action_button.clicked.connect(lambda state, r=robot_command: self.add_to_partner(r))

            self.tableWidget.setCellWidget(target_row, 1, user_input)

        self.tableWidget.setVisible(False)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setVisible(True)

    def link_values(self, args):
        for arg1 in args:
            for arg2 in args:
                arg1.valueChanged.connect(arg2.setValue)

    def send_toggle_button(self, button, command):
        call_me = lambda state, c=command: (
            button.setStyleSheet("QPushButton{color:firebrick;}"),
            button.setEnabled(False),
            self.add_to_partner(c)
        )
        button.clicked.connect(call_me)

    def value_change_send_command(self, value_emitter, command):
        call_me = lambda value, c=command: (
            c.set_payload(value),
            self.add_to_partner(c.get_copy())
        )
        value_emitter.valueChanged.connect(call_me)

    def run(self):
        while True:
            message = self.message_queue.get()
            print("In [" + self.name + "] Message: " + message.name)
            if message.takes_input:
                print("Payload: " + str(message.value))