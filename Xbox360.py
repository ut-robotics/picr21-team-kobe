from inputs import get_gamepad

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
            #print(x,y)
                
            front_speed = y#math.sqrt(x**2+y**2)
            side_speed = x
            rot_speed = rx
            
            print(ry, "ry")
            print(x, "x")
            #angle = math.degrees(math.atan2(y,x))
            #print(speed)#print(normalized)#print(event.ev_type, event.code, event.state)