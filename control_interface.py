import win32api, win32con


class ControlInterface(object):
    """
    Based on event calls for stuff we want to happen, simulate mouse interaction on win32
    """

    def __init__(self):
        self.screen_x = win32api.GetSystemMetrics(0)
        self.screen_y = win32api.GetSystemMetrics(1)

        self.but_prev = 0
        self.last_x = None
        self.last_y = None

    def mouse_move(self, x_float, y_float):
        """
        Move the mouse cursor to the given location
        :param x_float: fraction of the screen horizontally 0.0 - 1.0
        :type x_float: float
        :param y_float: fraction of the screen vertically 0.0 - 1.0
        :type y_float: float
        """
        x = int(x_float * self.screen_x)
        y = int(y_float * self.screen_y)
        self.last_x = x
        self.last_y = y

        win32api.SetCursorPos((x, y))

    def touch_change(self, touch_state, pressure):
        """
        Simulate button clicks / pressure at the last moved-to point
        :param touch_state: bitmask of buttons
        :type touch_state: int
        :param pressure: current pen pressure value
        :type pressure: int
        """

        but = touch_state
        if but != self.but_prev and self.last_x is not None:
            events = []
            changed_buttons = but ^ self.but_prev
            if changed_buttons & 8:  # left
                events.append(win32con.MOUSEEVENTF_LEFTDOWN if but & 8 else win32con.MOUSEEVENTF_LEFTUP)
            if changed_buttons & 32:  # right
                events.append(win32con.MOUSEEVENTF_RIGHTDOWN if but & 32 else win32con.MOUSEEVENTF_RIGHTUP)
            if changed_buttons & 16:  # middle
                events.append(win32con.MOUSEEVENTF_MIDDLEDOWN if but & 16 else win32con.MOUSEEVENTF_MIDDLEUP)
            self.but_prev = but

            for event in events:
                # TODO can we combine these events into one call?
                win32api.mouse_event(event, self.last_x, self.last_y, 0, 0)
        # print touch_state, pressure

