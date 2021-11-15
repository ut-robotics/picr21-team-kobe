from inputs import get_gamepad
import Movement

max_value = 1.0
min_value = -1.0
def gamepad():

    x=0
    y=0
    rx=0
    ry=0
    events = get_gamepad()
    for event in events:
        if event.code == "ABS_Y":
            y = event.state/32768
        if event.code == "ABS_X":
            x = event.state/32768
        if event.code == "ABS_RX":
            rx = event.state/32768
            
        front_speed = int(y * 10)
        side_speed = int(x * 10)
        rot_speed = int(rx * 10)
        return side_speed, front_speed, rot_speed