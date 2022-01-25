from scipy.interpolate import interp1d
from numpy import interp

# # Distance from basket in cm
# X = [0, 122, 163, 198, 215, 233, 274, 290, 328, 380, 450, 470, 500, 525]  # [208, 270, 308]
# # Used thrower speed
# Y = [700, 750, 800, 900, 1050, 1075, 1175, 1200, 1275, 1375, 1525, 1750, 1850, 2047]  # [975, 1100, 1175]


# New thrower calibratrion
# close distance 0.6m-2.5m

# diagonal distance experimental
X = [67,98,122,144, 164, 184, 204, 224, 247, 267, 287, 307, 327, 347, 367, 387, 414, 434, 460, 500, 525]
# diagonal speed
Y = [725,700,735, 775, 800, 835, 880, 920, 960, 985, 1015, 1050, 1080, 1130, 1150, 1180, 1210, 1300, 1400, 1850, 2047]
# distance
#X = [67, 93, 104, 120, 160, 182, 202, 225, 247, 272, 297, 323, 353, 370, 411, 500, 525]


# speed
#Y = [710, 725, 745, 755, 770, 875, 900, 925, 950, 975, 1060,1125, 1150, 1200, 1300, 1850, 2047 ]

# long distance 2.5m-5.25m

# Experimental 1
# #distance
# X =[0,70, 101, 128, 139, 168, 200, 258, 295, 350, 400, 450]

# #speed
# Y = [700, 725, 740, 800, 825, 900, 990, 1100, 1200, 1350, 1800, 2047]
# Experimental 2
# #speed
# Y = [680,715, 800, 900, 980, 1070, 1180, 1280, 1340, 1400, 1680]

# #dist
# X = [95,121, 156,190, 220, 250, 290, 320, 355, 390, 450]
# Function that estimates the speed to use from robot's current distance from the basket
last_distance = 0


def thrower_speed(distance):
    global last_distance
    try:
        predicted_function = interp1d(X, Y, kind="linear")
        # Map duty cycle to distance because duty cycle is approximately equal to linear speed
        # 525 is max playing area (cm)
        # likely should use a map of [122,525] where min distance is where you can still score a basket and a motor map of [700, 2047]
        # where min speed is the minimum amount needed to score from min distance
        # duty_cycle = int(interp(distance*100, [0, 525], [48, 2047]))
        if distance*100 > 525:
            distance = 5.25
        if distance*100 < 67:
            distance = 0.67

        thrower_speed = int(predicted_function(distance * 100))# + 2012
        print("using speed", thrower_speed, "at", distance * 100, "cm")
        #last_distance = distance
        return thrower_speed
    except Exception as e:
        if distance is None:
            return 2000
            #return int(predicted_function(last_distance * 100))# + 2012

        elif distance > 450:
            return 2000#+2012


