# Martin O'Hanlon
# www.stuffaboutcode.com
# A class for reading values from an xbox controller
# uses xboxdrv and pygame
# xboxdrv should already be running

import pygame
from pygame.locals import *
import os, sys
import threading

from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal)

import time

"""
NOTES - pygame events and values

JOYAXISMOTION
event.axis              event.value
0 - x axis left thumb   (+1 is right, -1 is left)
1 - y axis left thumb   (+1 is down, -1 is up)
2 - x axis right thumb  (+1 is right, -1 is left)
3 - y axis right thumb  (+1 is down, -1 is up)
4 - right trigger
5 - left trigger

JOYBUTTONDOWN | JOYBUTTONUP
event.button
A = 0
B = 1
X = 2
Y = 3
LB = 4
RB = 5
BACK = 6
START = 7
XBOX = 8
LEFTTHUMB = 9
RIGHTTHUMB = 10

JOYHATMOTION
event.value
[0] - horizontal
[1] - vertival
[0].0 - middle
[0].-1 - left
[0].+1 - right
[1].0 - middle
[1].-1 - bottom
[1].+1 - top

"""


# Main class for reading the xbox controller values
class XboxController(QThread):

    # set up the signals, note that these are not in the constructor.
    signal_left_stick_x = pyqtSignal(float)
    signal_left_stick_y = pyqtSignal(float)
    signal_right_stick_x = pyqtSignal(float)
    signal_right_stick_y = pyqtSignal(float)
    signal_trigger = pyqtSignal(float)

    signal_a_button = pyqtSignal(int)
    signal_b_button = pyqtSignal(int)
    signal_x_button = pyqtSignal(int)
    signal_y_button = pyqtSignal(int)

    signal_right_bumper = pyqtSignal(int)
    signal_left_bumper = pyqtSignal(int)

    signal_back_button = pyqtSignal(int)
    signal_start_button = pyqtSignal(int)

    signal_guide_button = pyqtSignal(int)

    signal_left_stick_button = pyqtSignal(int)
    signal_right_stick_button = pyqtSignal(int)

    signal_dpad_buttons = pyqtSignal((int, int))

    # setup xbox controller class
    def __init__(self, controllerCallBack=None, joystickNo=0, deadzone=0.1, scale=1, invertYAxis=False):

        # setup threading
        QThread.__init__(self)

        # persist values
        self.running = False
        self.controllerCallBack = controllerCallBack
        self.joystickNo = joystickNo
        self.lowerDeadzone = deadzone * -1
        self.upperDeadzone = deadzone
        self.scale = scale
        self.invertYAxis = invertYAxis
        self.controlCallbacks = {}

        # setup controller properties
        self.controlValues = {self.XboxControls.LTHUMBX: 0,
                              self.XboxControls.LTHUMBY: 0,
                              self.XboxControls.TRIGGER: 0,
                              self.XboxControls.RTHUMBX: 0,
                              self.XboxControls.RTHUMBY: 0,
                              self.XboxControls.A: 0,
                              self.XboxControls.B: 0,
                              self.XboxControls.X: 0,
                              self.XboxControls.Y: 0,
                              self.XboxControls.LB: 0,
                              self.XboxControls.RB: 0,
                              self.XboxControls.BACK: 0,
                              self.XboxControls.START: 0,
                              self.XboxControls.LEFTTHUMB: 0,
                              self.XboxControls.RIGHTTHUMB: 0,
                              self.XboxControls.DPAD: (0, 0)}

        # map controller inputs to the emitters
        self.signals = {
            self.XboxControls.LTHUMBY: self.signal_left_stick_y,
            self.XboxControls.LTHUMBX: self.signal_left_stick_x,
            self.XboxControls.RTHUMBX: self.signal_right_stick_x,
            self.XboxControls.RTHUMBY: self.signal_right_stick_y,
            self.XboxControls.TRIGGER: self.signal_trigger,
            self.XboxControls.A: self.signal_a_button,
            self.XboxControls.B: self.signal_b_button,
            self.XboxControls.X: self.signal_x_button,
            self.XboxControls.Y: self.signal_y_button,
            self.XboxControls.LB: self.signal_left_bumper,
            self.XboxControls.RB: self.signal_right_bumper,
            self.XboxControls.BACK: self.signal_back_button,
            self.XboxControls.START: self.signal_start_button,
            self.XboxControls.LEFTTHUMB: self.signal_left_stick_button,
            self.XboxControls.RIGHTTHUMB: self.signal_right_stick_button,
            self.XboxControls.DPAD: self.signal_dpad_buttons
        }

        # setup pygame
        self._setupPygame(joystickNo)

    class XboxControls():
        LTHUMBX = 0
        LTHUMBY = 1
        TRIGGER = 2
        RTHUMBX = 3
        RTHUMBY = 4
        A = 5
        B = 6
        X = 7
        Y = 8
        LB = 9
        RB = 10
        BACK = 11
        START = 12
        LEFTTHUMB = 13
        RIGHTTHUMB = 14
        DPAD = 15

    # pygame axis constants for the analogue controls of the xbox controller
    class PyGameAxis():
        LTHUMBX = 0
        LTHUMBY = 1
        TRIGGER = 2
        RTHUMBX = 4
        RTHUMBY = 3

    # pygame constants for the buttons of the xbox controller
    class PyGameButtons():
        A = 0
        B = 1
        X = 2
        Y = 3
        LB = 4
        RB = 5
        BACK = 6
        START = 7
        LEFTTHUMB = 8
        RIGHTTHUMB = 9

    # map between pygame axis (analogue stick) ids and xbox control ids
    AXISCONTROLMAP = {PyGameAxis.LTHUMBX: XboxControls.LTHUMBX,
                      PyGameAxis.LTHUMBY: XboxControls.LTHUMBY,
                      PyGameAxis.RTHUMBX: XboxControls.RTHUMBX,
                      PyGameAxis.RTHUMBY: XboxControls.RTHUMBY}

    # map between pygame axis (trigger) ids and xbox control ids
    TRIGGERCONTROLMAP = {PyGameAxis.TRIGGER: XboxControls.TRIGGER}

    # map between pygame buttons ids and xbox contorl ids
    BUTTONCONTROLMAP = {PyGameButtons.A: XboxControls.A,
                        PyGameButtons.B: XboxControls.B,
                        PyGameButtons.X: XboxControls.X,
                        PyGameButtons.Y: XboxControls.Y,
                        PyGameButtons.LB: XboxControls.LB,
                        PyGameButtons.RB: XboxControls.RB,
                        PyGameButtons.BACK: XboxControls.BACK,
                        PyGameButtons.START: XboxControls.START,
                        PyGameButtons.LEFTTHUMB: XboxControls.LEFTTHUMB,
                        PyGameButtons.RIGHTTHUMB: XboxControls.RIGHTTHUMB}

    # setup pygame
    def _setupPygame(self, joystickNo):
        # set SDL to use the dummy NULL video driver, so it doesn't need a windowing system.
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        # init pygame
        pygame.init()
        # create a 1x1 pixel screen, its not used so it doesnt matter
        screen = pygame.display.set_mode((1, 1))
        # init the joystick control
        pygame.joystick.init()
        # how many joysticks are there
        # print pygame.joystick.get_count()
        # get the first joystick
        joy = pygame.joystick.Joystick(joystickNo)
        # init that joystick
        joy.init()

    # called by the thread
    def run(self):
        self.running = True

        # run until the controller is stopped
        while (self.running):
            # react to the pygame events that come from the xbox controller
            for event in pygame.event.get():

                # thumb sticks, trigger buttons
                if event.type == JOYAXISMOTION:
                    # is this axis on our xbox controller
                    if event.axis in self.AXISCONTROLMAP:
                        yAxis = True if (event.axis == self.PyGameAxis.LTHUMBY or event.axis == self.PyGameAxis.RTHUMBY) else False
                        self.updateControlValue(self.AXISCONTROLMAP[event.axis], self._sortOutAxisValue(event.value, yAxis))

                    # is this axis a trigger
                    if event.axis in self.TRIGGERCONTROLMAP:
                        self.updateControlValue(self.TRIGGERCONTROLMAP[event.axis], self._sortOutTriggerValue(event.value))

                # d pad
                elif event.type == JOYHATMOTION:
                    # update control value
                    self.updateControlValue(self.XboxControls.DPAD, event.value)

                # button pressed and unpressed
                elif event.type == JOYBUTTONUP or event.type == JOYBUTTONDOWN:
                    # is this button on our xbox controller
                    if event.button in self.BUTTONCONTROLMAP:
                        # update control value
                        self.updateControlValue(self.BUTTONCONTROLMAP[event.button],
                                                self._sortOutButtonValue(event.type))


    # stops the controller
    def stop(self):
        self.running = False

    # updates a specific value in the control dictionary
    def updateControlValue(self, control, value):
        if self.controlValues[control] != value:  # make sure we only send changes on new data
            self.controlValues[control] = value
            signal = self.signals[control]
            signal.emit(value)

    # scales the axis values, applies the deadzone
    def _sortOutAxisValue(self, value, yAxis=False):
        # invert yAxis
        if yAxis and self.invertYAxis: value = value * -1
        # scale the value
        value = value * self.scale
        # apply the deadzone
        if value < self.upperDeadzone and value > self.lowerDeadzone: value = 0
        return value

    # turns the trigger value into something sensible and scales it
    def _sortOutTriggerValue(self, value):
        # trigger goes -1 to 1 (-1 is off, 1 is full on, half is 0) - I want this to be 0 - 1
        value = max(0, (value + 1) / 2)
        # scale the value
        value = value * self.scale
        return value

    # turns the event type (up/down) into a value
    def _sortOutButtonValue(self, eventType):
        # if the button is down its 1, if the button is up its 0
        value = 1 if eventType == JOYBUTTONDOWN else 0
        return value