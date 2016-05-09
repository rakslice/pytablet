import win32api, win32con


class ControlInterface(object):
    def __init__(self):
        self.screen_x = win32api.GetSystemMetrics(0)
        self.screen_y = win32api.GetSystemMetrics(1)

        self.but_prev = 0
        self.last_x = None
        self.last_y = None

    def mouse_move(self, x_float, y_float):
        x = int(x_float * self.screen_x)
        y = int(y_float * self.screen_y)
        self.last_x = x
        self.last_y = y

        win32api.SetCursorPos((x, y))

    def touch_change(self, touch_state, pressure):

        but = touch_state
        if but != self.but_prev and self.last_x is not None:
            events = []
            changed_buttons = but ^ self.but_prev
            if changed_buttons & 8:  # left
                events.append(win32con.MOUSEEVENTF_LEFTDOWN if but & 8 else win32con.MOUSEEVENTF_LEFTUP)
            if changed_buttons & 32:  # right
                events.append(win32con.MOUSEEVENTF_RIGHTDOWN if but & 32 else win32con.MOUSEEVENTF_RIGHTUP)
            if changed_buttons & 16:
                events.append(win32con.MOUSEEVENTF_MIDDLEDOWN if but & 16 else win32con.MOUSEEVENTF_MIDDLEUP)
            self.but_prev = but

            for event in events:
                win32api.mouse_event(event, self.last_x, self.last_y, 0, 0)
        # print touch_state, pressure

