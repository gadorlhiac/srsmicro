"""!
@brief Definition of the OlympusAppController class which has hard-coded routines
for managing the proprietary FV1200 Olympus software, without user input.
"""

import pyautogui

class OlympusAppController():
    """The OlympusAppController class for provides tools for controlling the
    proprietary Olympus FV1200 software without user input. The software must be
    running, but this class facilitates its blind manipulation.
    """
    def __init__(self):
        """! The OlympusAppController constructor."""
        # Status variables - maybe turn to a status dict like devices
        self._brightfield = False
        self._pixeldwell = 10
        self._zoom = 1
        # A variable for depth vs time vs single frame acquisition
        self._mode = 'single'
        self._nframes = 1

        # Is the focus knob on
        self._focus_on = True

    def toggle_fvbutton(self, x, y):
        """! Function to click buttons on FV1200 software GUI. Controls
        switching between open applications to select the FV1200 GUI and then
        return to the calling software.
        @param x (int) x position of the button on screen.
        @param y (int) y position of the button on screen.
        """
        pyautogui.hotkey('alt', 'tab')
        pyautogui.moveTo(x, y)
        pyautogui.click(interval=0.1)
        pyautogui.hotkey(x, y)

    def toggle_brightfield(self):
        """! Function to toggle between brightfield and laser scanning modes."""
        self.toggle_fvbutton(x = 346, y = 116)
        self._brightfield = not self._brightfield

    def set_scan_type(self, mode, n=1):
        """! Function to toggle between different laser scanning modes.
        @param mode (str) Indicates the type of scanning mode to use. (xy, xyz
        xyt, xyzt)
        """
        self._mode = mode
        self._nframes = n
        if mode == 'xyz':
            self.toggle_fvbutton(x = 588, y = 167)
        elif mode == 'xyt':
            self.toggle_fvbutton(x = 635, y = 167)


# pyautogui.hotkey('alt', 'tab')
# pyautogui.confirm(text='', title='')
# pyautogui.alert(text='', title='')

# pyautogui.postion()
# pyautogui.moveTo(x,y,t) where t is time it takes


# pyautogui.dragTo(100, 200, button='left')     # drag mouse to X of 100, Y of 200 while holding down left mouse button
# pyautogui.dragTo(300, 400, 2, button='left')  # drag mouse to X of 300, Y of 400 over 2 seconds while holding down left mouse button
# pyautogui.drag(30, 0, 2, button='right')   # drag the mouse left 30 pixels over 2 seconds while holding down the right mouse button

# pyautogui.doubleClick()  # perform a left-button double click


# pyautogui.click(clicks=2)  # double-click the left mouse button
# pyautogui.click(clicks=2, interval=0.25)  # double-click the left mouse button, but with a quarter second pause in between clicks
# pyautogui.click(button='right', clicks=3, interval=0.25)  ## triple-click the right mouse button with a quarter second pause in between clicks


# pyautogui.press('enter')  # press the Enter key
# pyautogui.press('f1')     # press the F1 key
# pyautogui.press('left')   # press the left arrow key

# pyautogui.press(['left', 'left', 'left'])

# pyautogui.press('left', presses=3)


# Values found for Olympus
################################################################################

# pyautogui.position(): 2560 x 1600
# 2 us position: Point(x=43, y=193)
# 4 us position: Point(x=55, y=193)
# 8 us position: Point(x=67, y=193)
# 10 us position: Point(x=79, y=193)
# 12.5 us position: Point(x=91, y=193)
# 20 us position: Point(x=103, y=193)
# 40 us position: Point(x=115, y=193)
# 100 us position: Point(x=127, y=193)
# 200 us position: Point(x=139, y=193)
# 1000 us position: Point(x=151, y=193)
# 2000 us position: Point(x=163, y=193)
# 4000 us position: Point(x=175, y=193)
# 5000 us position: Point(x=187, y=193)

# using 10us to 2us as eg
# need to store positions
# def change_dwell_time(time):
#     pyautogui.hotkey('alt', 'tab')
#     pyautogui.moveTo(67, 193)
#     pyautogui.dragTo(43, 193)
#     pyautogui.hotkey('alt', 'tab')

# Analog In Channels, won't use but need to be selected to scan
###############################################################
# Alg1: Point(x=1323, y=211)
# Alg2: Point(x=1401, y=211)
# can use pyautogui.click(clicks=3) to select/deselect

# Begin scan/set type
#####################
# XY-repeat: Point(x=478, y=129)
# XY: Point(x=555, y=129)
# Depth: Point(x=588, y=167)
# Time: Point(x=635, y=167)

# Brightfield: Point(x=346, y=116)
# Can have a brightfield status that is checked before trying to scan
# def brightfield():
#     pyautogui.hotkey('alt', 'tab')
#     pyautogui.moveTo(346, 116)
#     pyautogui.click(interval=0.1)
#     pyautogui.hotkey('alt', 'tab')

# Settings for depth/time and focus
###################################
# Can have a focus knob status which auto turns off before acquisition and
# turns back on afterwards
# Focus Knob Off: Point(x=73, y=852)

# Zoom
######
# Zoom decrease Point(x=247, y=394)
# Zoom increase Point(x=247, y=340)

# def change_zoom(inc=True, amt=10):
#     pyautogui.hotkey('alt', 'tab')
#     if inc:
#         pyautogui.moveTo(247, 340)
#     else:
#         pyautogui.moveTo(247, 394)
#     pyautogui.click(clicks=amt, interval=0.1)
#     pyautogui.hotkey('alt', 'tab')
