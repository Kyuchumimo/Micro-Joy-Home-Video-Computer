from machine import SPI, Pin
from flash_spi import FLASH
import time

import machine
import sdcard
import uos

# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(1, machine.Pin.OUT)

# Intialize SPI peripheral (start with 1 MHz)
spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=Pin(2),
                  mosi=Pin(3),
                  miso=Pin(4))

# Initialize SD card
sd = sdcard.SDCard(spi, cs)

# Mount filesystem
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

####################################

cspins = [Pin(13, Pin.OUT, value=1)]
flash = FLASH(SPI(1, baudrate=20_000_000, sck=Pin(14), miso=Pin(12), mosi=Pin(11)), cspins)

filename = "/sd/filename.winproj.bin"
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
        flash[start:end] = data
        
        
        if flash[start:end] == data:
            print(f"flash[{start}:{end}]: OK")
        else:
            print(f"flash[{start}:{end}]: ERR")
            print('An error has occurred during the data verification process. Process has been terminated.')
            
            break

        # Updates the starting position for the next block
        start = end


Pin(11, mode=Pin.IN, pull=None)
Pin(12, mode=Pin.IN, pull=None)
Pin(13, mode=Pin.IN, pull=None)
Pin(14, mode=Pin.IN, pull=None)
