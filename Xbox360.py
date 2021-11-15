from inputs import get_gamepad
import Movement

max_value = 1.0
min_value = -1.0
def gamepad():

    x=0
    y=0
    rx=0
    ry=0
    while True:
        events = get_gamepad()
        for event in events:
            if event.code == "ABS_Y":
                y = event.state/32768
                #print(max(min(float(event.state), max_value), min_value))
            if event.code == "ABS_X":
                x = event.state/32768
            if event.code == "ABS_RX":
                rx = event.state/32768
            if event.code == "ABS_RY":
                ry= event.state/32768
            print(x,y)
                
            front_speed = int(y * 10)#math.sqrt(x**2+y**2)
            side_speed = int(x * 10)
            rot_speed = int(rx * 10)
            #return side_speed, front_speed, rot_speed
            Movement.Move2(side_speed, front_speed, rot_speed, 0)
            #angle = math.degrees(math.atan2(y,x))
            #print(speed)#print(normalized)#print(event.ev_type, event.code, event.state)

gamepad()