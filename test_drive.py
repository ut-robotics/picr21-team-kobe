import serialcomms

i = 0

while i < 10:
    #motor 1 is the top wheel motor2 is left motor3 is right
    #this should send the command to move the side wheels
    #order: motor1, motor2, motor3, thrower, failsafe
    serialcomms.WriteCommand(0,100,100,0,0)
    i += 1

