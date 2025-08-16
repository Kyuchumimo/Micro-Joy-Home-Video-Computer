import struct
import time

__docformat__ = "restructuredtext"

class Music810:
    """
    Class to play music on an LPC810 chip
    """
    def __init__(self, i2c):
        self._offset = 0
        self._data = bytearray()
        self._should_loop = False
        self._loop_offset = 0
        self._prev_time = time.ticks_ms()/1000 #K: same behavior as time.monotonic()
        self._ticks_to_wait = 0
        self._end_of_song = False

        self._i2c = i2c

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
            if vgm_version != 0x171:
                raise Exception(
                    f"Invalid VGM version format; got {vgm_version:x}, want 0x171"
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
            if ay8910_clock != 1789772:
                raise Exception(
                    f"Invalid VGM clock freq; got {ay8910_clock}, want 1789772"
                )
            
            # 0x9c: K051649/K052539 clock (32 bits)
            #  Input clock rate in Hz for the K051649 chip. A typical value is
            #  1789772. It should be 0 if there is no K051649 chip used.
            #  If bit 31 is set it is a K052539.
            k051649_clock = struct.unpack_from("<I", header, 0x9C)[0]
            if k051649_clock != 1789772 and k051649_clock != 2149273420 and k051649_clock != 0:
                raise Exception(
                    f"Invalid VGM clock freq; got {k051649_clock}, want 1789772 or 2149273420 or 0"
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
            #  0xd2 aa dd : SCC, write value dd to register aa
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
                self._i2c.writeto(0x50, data[i + 1].to_bytes(1, None) + data[i + 2].to_bytes(1, None))
                i += 3
            
            #  0xd2 aa dd : SCC, write value dd to register aa
            elif data[i] == 0xd2:
                self._i2c.writeto(0x51, data[i + 1].to_bytes(1, None) + data[i + 2].to_bytes(1, None))
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
    
    def play_freq(self, channel: int, freq: float) -> None:
        """
        Play a certain frequency.

        :param int channel: One of the 3 available channels:0, 1 or 2.
        :param float freq: Frequency to play. Valid range: 41.203 - 15804.264
        """
        # Supported frequency range: [41.203 - 15804.264]
        # Although freqs > 3951.066 shouldn't be used
        # In terms of musical notes the range is: [E1 - B7+]
        assert 0 <= channel <= 2
        
        clock = 3579545  # Hz
        reg = int(clock // (freq * 2 * 16))

        lsb = reg & 255
        msb = reg >> 8

        #mixer = int.from_bytes(self._i2c.readfrom_mem(0x50, 7, 2), "big")
        self._i2c.writeto(0x50, bytes(b"\x07") + (0x3F & ~(1 << channel) | (1 << channel + 3)).to_bytes(1, None))
        #self._i2c.writeto(0x50, bytes(b"\x07\x38"))
        #print(f"{bytes(b'\x07') + (mixer & ~(1 << channel) | (1 << channel + 3)).to_bytes(1, None)}")

        self._i2c.writeto(0x50, (channel*2).to_bytes(1, None) + lsb.to_bytes(1, None))
        self._i2c.writeto(0x50, (channel*2+1).to_bytes(1, None) + msb.to_bytes(1, None))

    def _play_note(self, voice: int, note: int, octave: int) -> None:
        # Initial note C0:
        # https://www.liutaiomottola.com/formulae/freqtab.htm
        note_c0 = 16.35
        distance = octave * 12 + note
        freq = note_c0 * (2 ** (distance / 12))
        self.play_freq(voice, freq)

    def play_notes(self, notes: str) -> None:
        """
        Play music notes.

        Supported values are:

        Notes: C, C#, D, D#, E, F, F#, G, G#, A, A#, B
        Voice: Vn, where n is:0, 1 or 2
        Octave: On, where n is: 0-9
        Volume: Un, where n is: 0-9
        Note duration: W, H, Q, I or S
         W: Whole,
         H: Half,
         Q: Quarter
         I: Eighth
         S: Sixteenth

        Example: TODO

        :param str notes: Notes to play.
        """
        # Inspired by C128 "play" BASIC command:
        # https://www.commodore.ca/manuals/128_system_guide/sect-07b.htm#7.3.html

        # Defaults
        voice = 0
        octave = 4
        duration = 16

        # Hack
        notes = notes + " "

        i = 0
        while i < len(notes):
            n = notes[i]
            if n == "V":
                # Voice: voices go from 0-2
                voice = int(notes[i + 1])
                i += 2
            elif n == "O":
                octave = int(notes[i + 1])
                i += 2
            elif n in "CDEFGAB":
                # Notes that belong to the chromatic scale:
                # C, C#, D, D#, E, F, F#, G, G#, A, A#, B
                chromatic = {
                    "C": 0,
                    "C#": 1,
                    "D": 2,
                    "D#": 3,
                    "E": 4,
                    "F": 5,
                    "F#": 6,
                    "G": 7,
                    "G#": 8,
                    "A": 9,
                    "A#": 10,
                    "B": 11,
                }
                if notes[i + 1] == "#":
                    n = n + "#"
                    i += 1
                note = chromatic[n]
                self.set_vol(voice, 15)
                self._play_note(voice, note, octave)
                i += 1
                # TODO: support envelops
                time.sleep(0.016666 * duration * 2)
                self.set_vol(voice, 0)
                time.sleep(0.016666)

            elif n == "U":
                # TODO: Remove volument support in favor of envelops
                # Volume
                vol = int(notes[i + 1])
                self.set_vol(voice, vol)
                i += 2
            elif n in "WHQIS":
                dur_dict = {
                    "W": 64,  # Whole
                    "H": 32,  # Half
                    "Q": 16,  # Quarter
                    "I": 8,  # Eighth
                    "S": 4,  # Sixteenth
                }
                duration = dur_dict[n]
                i += 1
            elif n in " ,":
                i += 1
        self.set_vol(0, 0)
    
    def set_vol(self, channel: int, vol: int) -> None:
        """
        Set the volume for the given channel.

        :param int channel: Channel to be used. Valid values: 0-2.
        :param int vol: Volume to set. Values:0-15, where 0 is silence and 15 max volume.
        """
        assert 0 <= channel <= 2
        assert 0 <= vol <= 15
        
        self._i2c.writeto(0x50, (8+channel).to_bytes(1, None) + vol.to_bytes(1, None))
    
    def reset(self) -> None:
        """
        Reset the LPC810 chip.
        Turn off all audio channels.
        """
        self._i2c.writeto(0x50, b"\x07\x3F")
        self._i2c.writeto(0x51, b"\xAF\x00")
        self._offset = 0
        self._data = bytearray()
