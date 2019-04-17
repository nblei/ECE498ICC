import spidev
import os
import time
delay = 1.2

spi = spidev.SpiDev()
spi.open(0, 0)

def readChannel(channel):
        START_BIT = 1
        SELECT_SINGLE = 1
        #spi.max_speed_hz = 500000
        input_seq = [START_BIT, (SELECT_SINGLE*8 + channel) << 4, 0]
        #input_seq = [255, 255, 255]

        val = spi.xfer2([1, (channel + 8) << 4, 0])
        print(val)
        data = ((val[1]&3) << 8) + val[2]
        return data

if __name__ == "__main__":
        while True:
                val = readChannel(7)
                #if (val != 0):
                print(val)
                time.sleep(delay)

