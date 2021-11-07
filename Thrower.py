from scipy.interpolate import interp1d

#Distance from basket in cm
X = [0,122,163,198, 233, 328, 450, 600]
#Used thrower speed
Y = [700,700,800,900, 1000, 1200, 1600, 2400]
#Function that estimates the speed to use from robot's current distance from the basket
def ThrowerSpeed(distance):
    predicted_function = interp1d(X,Y, kind="linear")
    thrower_speed = int(predicted_function(distance*100))
    return thrower_speed