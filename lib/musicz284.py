import struct
import time

from sr_74hc595_spi import SR #K: adafruit_74hc595 Library Replacement
import machine #K: same or similar as board module
from machine import SPI #K: Serial protocols library, same as busio.SPI class
from machine import Pin #K: Digital input/output library, same as digitalio

__docformat__ = "restructuredtext"

class Musicz284:
    """
    Class to play music on an YMZ284 chip
    """
    def __init__(self):
        self._offset = 0
        self._data = bytearray()
        self._should_loop = False
        self._loop_offset = 0
        self._prev_time = time.ticks_ms()/1000 #K: same behavior as time.monotonic()
        self._ticks_to_wait = 0
        self._end_of_song = False

        self._spi = SPI(1, sck=Pin(10), mosi=Pin(11)) #K: SPI protocol pin assignment, same as busio.SPI(Clock, MOSI/TX(Optional)=board.pin, MISO/RX(Optional)=board.pin)
        self._latch_pin = Pin(12) #K: Pin A3 digital assignment, same as digitalio.DigitalInOut(board.pin) (rclk)
        self._sr = SR(self._spi, self._latch_pin) #K: adafruit_74hc595 ShiftRegister74HC595 class __init__ Replacement
        self._ymz284_wr = Pin(13, Pin.OUT) #K: Pin digital OUTPUT assignment, same as .direction = digitalio.Direction.OUTPUT
        self._ymz284_a0 = Pin(9, Pin.OUT) #K: Pin digital OUTPUT assignment, same as .direction = digitalio.Direction.OUTPUT

        self._ymz284_wr.value(True) #K: same as '.value = True'

        self.reset()

    def load_vgm(self, filename: str) -> None:
        """
        Load a VGM song.

        The loaded song does not play automatically. In order to play the song
        the user must call "tick()" every 1/60s.

        :param str filename: The VGM song to load.
        """
        with open(filename, "rb") as file:
            # Assuming VGM from Furnace (256 bytes of header)
            header = bytearray(file.read(0x100))

            # 0x00: "Vgm " (0x56 0x67 0x6d 0x20) file identification (32 bits)
            if header[:4].decode("utf-8") != "Vgm ":
                raise Exception("Invalid header")

            # 0x08: Version number (32 bits)
            #  This is used for backwards compatibility in players, and defines which
            #  header values are valid.
            vgm_version = struct.unpack_from("<I", header, 8)[0]
            if vgm_version <= 0x161:
                raise Exception(
                    f"Invalid VGM version format; got {vgm_version:x}, want <= 0x161"
                )

            # 0x04: Eof offset (32 bits)
            #  Relative offset to end of file (i.e. file length - 4).
            #  This is mainly used to find the next track when concatanating
            #  player stubs and multiple files.
            file_len = struct.unpack_from("<I", header, 4)[0]
            self._data = bytearray(file.read(file_len + 4 - 0x100))

            # 0x1c: Loop offset (32 bits)
            #  Relative offset to loop point, or 0 if no loop.
            #  For example, if the data for the one-off intro to a song was in bytes
            #  0x0040-0x3fff of the file, but the main looping section started at
            #  0x4000, this would contain the value 0x4000-0x1c = 0x00003fe4.
            loop = struct.unpack_from("<I", header, 0x1C)[0]
            self._should_loop = bool(loop != 0)
            self._loop_offset = loop + 0x1C - 0x100
            
            # 0x74: AY8910 clock (32 bits)
            #  Input clock rate in Hz for the AY-3-8910 PSG chip. A typical value is
            #  1789772. It should be 0 if there is no PSG chip used.
            ay8910_clock = struct.unpack_from("<I", header, 0x74)[0]
            if sn76489_clock != 1789772:
                raise Exception(
                    f"Invalid VGM clock freq; got {ay8910_clock}, want 1789772"
                )

    def tick(self) -> None:
        """
        Play the loaded VGM song.

        Must be called at 1/60s frequency.
        Example:
        m.load_vgm('my_song.vgm')
        while True:
          # game main loop
          # do something
          m.tick()
          time.sleep(1/60)
        """
        if self._end_of_song:
            raise Exception("End of song reached")

        self._ticks_to_wait -= 1
        if self._ticks_to_wait > 0:
            return

        # Convert to local variables (easier to ready... and tiny bit faster?)
        data = self._data
        i = self._offset
        while True:
            if i >= len(data):
                raise Exception(f"unexpected offset: {i} >= {len(data)}")

            # Valid commands
            #  0x4f dd    : Game Gear PSG stereo, write dd to port 0x06
            #  0x50 dd    : PSG (SN76489/SN76496) write value dd
            #  0x51 aa dd : YM2413, write value dd to register aa
            #  0x52 aa dd : YM2612 port 0, write value dd to register aa
            #  0x53 aa dd : YM2612 port 1, write value dd to register aa
            #  0x54 aa dd : YM2151, write value dd to register aa
            #  0x61 nn nn : Wait n samples, n can range from 0 to 65535 (approx 1.49
            #               seconds). Longer pauses than this are represented by multiple
            #               wait commands.
            #  0x62       : wait 735 samples (60th of a second), a shortcut for
            #               0x61 0xdf 0x02
            #  0x63       : wait 882 samples (50th of a second), a shortcut for
            #               0x61 0x72 0x03
            #  0x66       : end of sound data
            #  0x67 ...   : data block: see below
            #  0x7n       : wait n+1 samples, n can range from 0 to 15.
            #  0x8n       : YM2612 port 0 address 2A write from the data bank, then wait
            #               n samples; n can range from 0 to 15. Note that the wait is n,
            #               NOT n+1.
            #  0x94 ss    : DAC Stream Control Write: Stop Stream
            #  0xa0 aa dd : AY-3-8910, write value dd to register aa
            #  0xe0 dddddddd : seek to offset dddddddd (Intel byte order) in PCM data bank

            # print(f'data: 0x{data[i]:02x}')

            #  0x61 nn nn : Wait n samples, n can range from 0 to 65535 (approx 1.49
            #               seconds). Longer pauses than this are represented by multiple
            #               wait commands.
            if data[i] == 0x61:
                # unpack little endian unsigned short
                delay = struct.unpack_from("<H", data, i + 1)[0]
                self._delay_n(delay)
                i = i + 3
                break

            #  0x62       : wait 735 samples (60th of a second), a shortcut for
            #               0x61 0xdf 0x02
            elif data[i] == 0x62:
                self._delay_one()
                i = i + 1
                break
            
            #  0x63       : wait 882 samples (50th of a second), a shortcut for
            #               0x61 0x72 0x03
            elif data[i] == 0x63:
                # omited
                i = i + 1
                break

            #  0x66       : end of sound data
            elif data[i] == 0x66:
                if self._should_loop:
                    i = self._loop_offset
                else:
                    self._end_of_song = True
                    break

            #  0x94 ss    : DAC Stream Control Write: Stop Stream
            elif data[i] == 0x94:
                i = i + 2

            #  0xa0 aa dd : AY-3-8910, write value dd to register aa
            elif data[i] == 0xa0:
                self._ymz284_a0.value(False)
                self._write_port_data(data[i + 1])
                self._ymz284_a0.value(True)
                self._write_port_data(data[i + 2])
                i += 3

            else:
                raise Exception("Unknown value: data[0x%x] = 0x%x" % (i, data[i]))
            
        # update offset
        self._offset = i
    
    def _delay_one(self) -> None:
        self._ticks_to_wait += 1

    def _delay_n(self, samples: int) -> None:
        # 735 samples == 1/60s
        self._ticks_to_wait += samples // 735
    
    def _write_port_data(self, byte_data) -> None:
        # Send data
        self._sr[0] = byte_data #K: sr.gpio replacement

        # Enable YMZ284
        self._ymz284_wr.value(False) #K: same as '.value = False'
        # Disable YMZ284
        self._ymz284_wr.value(True) #K: same as '.value = True'

    def reset(self) -> None:
        """
        Reset the YMZ284 chip.
        Set volume to 0 in all channels.
        """
        for i in range(0x8, 0xB):
            self._ymz284_a0.value(False)
            self._write_port_data(i)
            self._ymz284_a0.value(True)
            self._write_port_data(0)
        self._offset = 0
        self._data = bytearray()
