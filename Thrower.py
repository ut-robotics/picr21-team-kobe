from scipy.interpolate import interp1d

#Distance from basket in cm
X = [0,122,163,198,215, 233, 274, 328, 380, 450, 600] #[208, 270, 308]
#Used thrower speed
Y = [700,700,800,925,1050, 1050, 1111, 1225, 1635, 1625, 2400] #[975, 1100, 1175]
#Function that estimates the speed to use from robot's current distance from the basket
def ThrowerSpeed(distance):
    try:
        predicted_function = interp1d(X,Y, kind="linear")
        if distance is None:
            return 700
        else:
            thrower_speed = int(predicted_function(distance*100))
            print("using speed", thrower_speed, "at", distance, "cm")
        return thrower_speed
    except Exception as e:
        if distance > 600:
            return 2400
        else:
            return 675