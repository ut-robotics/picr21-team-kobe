from os import lseek


def ReadThreshold(filename):
    try:
        with open(filename, 'r') as reader:
            values = reader.readline().split(",")

            # only read from the file if there are enough items to read
            if len(values) >= 6: 
                lHue = int(values[0])
                lSaturation = int(values[1])
                lValue = int(values[2])
                hHue = int(values[3])
                hSaturation = int(values[4])
                hValue = int(values[5])
    except Exception as e:
        print(e)
    return lHue, lSaturation, lValue, hHue, hSaturation, hValue