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
                  sck=machine.Pin(2),
                  mosi=machine.Pin(3),
                  miso=machine.Pin(4))

# Initialize SD card
sd = sdcard.SDCard(spi, cs)

# Mount filesystem
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

####################################

cspins = [Pin(13, Pin.OUT, value=1)]
flash = FLASH(SPI(1, baudrate=20_000_000, sck=Pin(14), miso=Pin(12), mosi=Pin(11)), cspins)

filename = "/sd/snspell.winproj.bin"
block_size = 1024

with open(filename, "rb") as f:
    start = 0  # Starting position for each block in flash

    while True:
        # Read the following block of the file
        data = f.read(block_size)
        
        # If there is no more data, exit the loop
        if data == b'':
            break

        # Calculates the final position based on the actual size of `data`
        end = start + len(data)

        # Ensures that flash has the necessary size to write the block
        flash[start:end] = data
        print(f"flash[{start}:{end}]: OK") if flash[start:end] == data else print(f"flash[{start}:{end}]: ERR")

        # Updates the starting position for the next block
        start = end

print('OK')