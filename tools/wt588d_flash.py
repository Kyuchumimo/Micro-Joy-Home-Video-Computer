from machine import SPI, Pin
from spiram import SPIRAM

import sdcard
import uos

# Initialize SD card
sd = sdcard.SDCard(SPI(0, baudrate=1_320_000, sck=Pin(2), mosi=Pin(3), miso=Pin(4)), Pin(1, Pin.OUT, value=1))

# Mount filesystem
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

####################################

rst = Pin(0, Pin.OUT, value=0)           # reset the IC

cspins = [Pin(17, Pin.OUT, value=1)]
#flash = FLASH(SPI(1, baudrate=20_000_000, sck=Pin(14), mosi=Pin(11), miso=Pin(12)), cspins)
ram = SPIRAM(SPI(0, baudrate=20_000_000, sck=Pin(18), mosi=Pin(19), miso=Pin(16)), cspins)

filename = "snspell.winproj.bin"
block_size = 4096

with open(filename, "rb") as f:
    start = 0  # Starting position for each block in flash

    while True:
        # Read the following block of the file
        data = f.read(block_size)
        
        # If there is no more data, exit the loop
        if data == b'':
            print('Process has been successfully completed.')
            
            break

        # Calculates the final position based on the actual size of `data`
        end = start + len(data)

        # Ensures that flash has the necessary size to write the block
        ram[start:end] = data
        
        
        if ram[start:end] == data:
            print(f"flash[{start}:{end}]: OK")
        else:
            print(f"flash[{start}:{end}]: ERR")
            print('An error has occurred during the data verification process. Process has been terminated.')
            
            break

        # Updates the starting position for the next block
        start = end

Pin(0, mode=Pin.IN, pull=None)
Pin(16, mode=Pin.IN, pull=None)
Pin(17, mode=Pin.IN, pull=None)
Pin(18, mode=Pin.IN, pull=None)
Pin(19, mode=Pin.IN, pull=None)
