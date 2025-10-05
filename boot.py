from machine import Pin, SPI
from rp2 import PIO, StateMachine, asm_pio
import time

# VIDEO
CSW = Pin(13, Pin.OUT)
CSR = Pin(14, Pin.OUT)
MODE = Pin(15, Pin.OUT)

@asm_pio(sideset_init=PIO.OUT_HIGH, out_init=(rp2.PIO.OUT_LOW,) * 8, out_shiftdir=PIO.SHIFT_RIGHT,
 autopull=True, pull_thresh=16)
def paral_write():
    pull()        
    out(pins, 8)  .side(0)
    nop()         .side(1)

@asm_pio(sideset_init=PIO.OUT_HIGH, in_shiftdir=rp2.PIO.SHIFT_LEFT,
 autopush=False, push_thresh=16)
def paral_read():
    nop()         .side(0)
    in_(pins, 8)
    push()        .side(1)

write_sm = StateMachine(0, paral_write, freq=1000000, sideset_base=CSW, out_base=Pin(5))
write_sm.active(1)

read_sm = StateMachine(1, paral_read, freq=1000000, sideset_base=CSR, in_base=Pin(5))
read_sm.active(1)

VDP_TRANSPARENT = 0
VDP_BLACK = 1
VDP_MED_GREEN = 2
VDP_LIGHT_GREEN = 3
VDP_DARK_BLUE = 4
VDP_LIGHT_BLUE = 5
VDP_DARK_RED = 6
VDP_CYAN = 7
VDP_MED_RED = 8
VDP_LIGHT_RED = 9
VDP_DARK_YELLOW = 10
VDP_LIGHT_YELLOW = 11
VDP_DARK_GREEN = 12
VDP_MAGENTA = 13
VDP_GRAY = 14
VDP_WHITE = 15

VDP_MODE_G1 = 0
VDP_MODE_G2 = 1
VDP_MODE_MULTICOLOR = 2
VDP_MODE_TEXT = 3

ASCII = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x10\x10\x10\x10\x10\x00\x10\x00(((\x00\x00\x00\x00\x00((|(|((\x008TP8\x14T8\x00`d\x08\x10 L\x0c\x00 PP TH4\x00\x08\x08\x10\x00\x00\x00\x00\x00\x08\x10   \x10\x08\x00 \x10\x08\x08\x08\x10 \x00\x00(\x10|\x10(\x00\x00\x00\x10\x10|\x10\x10\x00\x00\x00\x00\x00\x000\x10 \x00\x00\x00\x00|\x00\x00\x00\x00\x00\x00\x00\x00\x0000\x00\x00\x04\x08\x10 @\x00\x008DDDDD8\x00\x100\x10\x10\x10\x108\x008D\x04\x08\x10 |\x008D\x04\x18\x04D8\x00\x08\x18(H|\x08\x08\x00|@x\x04\x04D8\x00\x18 @xDD8\x00|\x04\x08\x10   \x008DD8DD8\x008DD<\x04\x080\x00\x0000\x0000\x00\x00\x0000\x000\x10 \x00\x08\x10 @ \x10\x08\x00\x00\x00|\x00|\x00\x00\x00 \x10\x08\x04\x08\x10 \x008D\x04\x08\x10\x00\x10\x008D\\T\\@8\x008DD|DDD\x00x$$8$$x\x008D@@@D8\x00x$$$$$x\x00|@@x@@|\x00|@@x@@@\x00<@@\\DD8\x00DDD|DDD\x008\x10\x10\x10\x10\x108\x00\x04\x04\x04\x04\x04D8\x00DHP`PHD\x00@@@@@@|\x00DlTTDDD\x00DddTLLD\x00|DDDDD|\x00xDDx@@@\x008DDDTH4\x00xDDxPHD\x008D@8\x04D8\x00|\x10\x10\x10\x10\x10\x10\x00DDDDDD8\x00DDD((\x10\x10\x00DDDTTT(\x00DD(\x10(DD\x00DD(\x10\x10\x10\x10\x00|\x04\x08\x10 @|\x008     8\x00\x00@ \x10\x08\x04\x00\x008\x08\x08\x08\x08\x088\x00\x00\x10(D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|')

color_table_size = 0
crsr_max_x = 31 # Overwritten in Text mode
crsr_max_y = 23

def write_byte(value):
    MODE.value(1)
    write_sm.put(value)

def write_byte_to_VRAM(value):    
    MODE.value(0)
    write_sm.put(value)

def read_byte_from_VRAM():
    MODE.value(0)
    if read_sm.rx_fifo():
        return read_sm.get()  # Obtener un byte (8 bits) desde el FIFO
    return None

def set_register(register_index, value):
    write_byte(value)
    write_byte(0x80 | register_index)

def set_write_address(address):
    write_byte(address & 0xff)
    write_byte(0x40 | (address >> 8) & 0x3f)

def set_read_address(address):
    write_byte(address & 0xff)
    write_byte((address >> 8) & 0x3f)

def vdp_set_bdcolor(color):
    set_register(7, color)

def vdp_textcolor(fg, bg):
    set_register(7, (fg << 4) + bg)

def vdp_set_sprite_pattern(number, sprite):
    if sprite_size_sel:
        set_write_address(SPRITE_PATTERNS + 32*number)
        for i in range(32):
            write_byte_to_VRAM(sprite[i])
    else:
        set_write_address(SPRITE_PATTERNS + 8*number)
        for i in range(8):
            write_byte_to_VRAM(sprite[i])

# CUSTOM API
def vdp_sprite_set_color(number, color):
    set_write_address(SPRITE_ATTRIBUTES + 4*number + 3)
    
    write_byte_to_VRAM(0x80 | (color & 0xF))

def vdp_sprite_set_position(number, x, y):
    set_write_address(SPRITE_ATTRIBUTES + 4*number)
    
    write_byte_to_VRAM(y)
    write_byte_to_VRAM(x+32)

def vdp_sprite_init(name, priority, color):
    addr = SPRITE_ATTRIBUTES + 4*priority
    set_write_address(addr)
    write_byte_to_VRAM(0)
    write_byte_to_VRAM(0)
    if sprite_size_sel:
        write_byte_to_VRAM(4*name)
    else:
        write_byte_to_VRAM(name)
    write_byte_to_VRAM(0x80 | (color & 0xF))

def vdp_set_pattern_color(index, fg, bg):
    if vdp_mode == VDP_MODE_G1:
        index &= 31
    
    set_write_address(COLOR_TABLE + index)
    write_byte_to_VRAM((fg << 4) + bg)

def vdp_print(text, x, y):
    text = str(text).upper()
    
    if vdp_mode == VDP_MODE_G1:
        set_write_address(NAME_TABLE + (x + (y * 32)))
        
        for i in range(len(str(text).splitlines())):
            if i>0:
                set_write_address(NAME_TABLE + (x + ((y + i) * 32)))
            for character in range(len(str(text).splitlines()[i]) - max(0, -32 + x + len(str(text).splitlines()[i]))):
                write_byte_to_VRAM(ord(str(text).splitlines()[i][character]))
    
    elif vdp_mode == VDP_MODE_TEXT:
        set_write_address(NAME_TABLE + (x + (y * 40)))
        
        for i in range(len(str(text).splitlines())):
            if i>0:
                set_write_address(NAME_TABLE + (x + ((y + i) * 40)))
            for character in range(len(str(text).splitlines()[i]) - max(0, -40 + x + len(str(text).splitlines()[i]))):
                write_byte_to_VRAM(ord(str(text).splitlines()[i][character]))

def vdp_text_wrap(text,x,y,color,w,h,border=None):
    # optional box border
    if border is not None:
        vdp_textcolor(color, border)
    cols = w
    # for each row
    j = 0
    for i in range(0, len(text), cols):
        # draw as many chars fit on the line
        vdp_print(text[i:i+cols], x, y + j)
        j += 1
        # dont overflow text outside the box
        if j >= h:
            break

def vdp_cls():
    set_write_address(NAME_TABLE)
    
    if vdp_mode == VDP_MODE_TEXT:
        for _ in range(960):
            write_byte_to_VRAM(0x20)
    elif vdp_mode == VDP_MODE_G1:
        for _ in range(768):
            write_byte_to_VRAM(0x20)

def vdp_mset(x, y, tile_id):
    x = int(x)
    y = int(y)
    tile_id = int(tile_id)
    
    if vdp_mode == VDP_MODE_G1:
        set_write_address(NAME_TABLE + (x + (y * 32)))
    elif vdp_mode == VDP_MODE_TEXT:
        set_write_address(NAME_TABLE + (x + (y * 40)))
    
    write_byte_to_VRAM(tile_id)

def vdp_pix(x, y, color):
    if vdp_mode == VDP_MODE_MULTICOLOR:
        addr = PATTERN_TABLE + 8 * (x // 2) + y % 8 + 256 * (y // 8)
        set_read_address(addr)
        dot = read_byte_from_VRAM()
        set_write_address(addr)
        if x & 1: # Odd columns
            write_byte_to_VRAM((dot & 0xf0) + (color & 0x0f))
        else:
            write_byte_to_VRAM((dot & 0x0f) + (color << 4))

ASSET_PATH = ""

def vdp_sync(mask=0, asset=0):
    if vdp_mode == VDP_MODE_G1:
        with open(f'{ASSET_PATH}/graphics/{asset}.mgb', 'rb') as file:
            # FILE HEADER
            header = file.read(2)
            if header != b'MG':
                raise Exception("Invalid header")
            
            version = file.read(2)
            if version != b'03':
                raise Exception("Invalid version")
            
            chunkFlag = file.read(1)
            if chunkFlag != b'\x0f':
                raise Exception(
                    f"Invalid chunkFlag; got {chunkFlag}, want 0x0f"
                )
            
            if mask == 0: mask = 0b1111
            
            # COLORSET CHUNK
            if 1<<0 & mask:
                file.seek(0x6)
                set_write_address(COLOR_TABLE)
                for byte in bytearray(file.read(0x20)):
                    write_byte_to_VRAM(byte)
            
            # CHARACTER CHUNK
            if 1<<1 & mask:
                file.seek(0x107)
                set_write_address(PATTERN_TABLE)
                for byte in bytearray(file.read(0x800)):
                    write_byte_to_VRAM(byte)
            
            # SPRITE CHUNK
            if 1<<2 & mask:
                file.seek(0x908)
                set_write_address(SPRITE_PATTERNS)
                for byte in bytearray(file.read(0x800)):
                    write_byte_to_VRAM(byte)
            
            # MAP DATA
            if 1<<3 & mask:
                file.seek(0x1119)
                set_write_address(NAME_TABLE)
                for byte in bytearray(file.read(0x300)):
                    write_byte_to_VRAM(byte)

def vdp_init(mode, color=VDP_BLACK, big_sprites=False, magnify=False):
    global SPRITE_ATTRIBUTES
    global SPRITE_PATTERNS
    global sprite_size_sel #0: 8x8 sprites 1: 16x16 sprites
    global NAME_TABLE
    global COLOR_TABLE
    global color_table_size
    global PATTERN_TABLE
    global crsr_max_x
    global crsr_max_y
    global vdp_mode
    
    vdp_mode = mode
    sprite_size_sel = big_sprites
    
    # Clear Ram
    set_write_address(0x0)
    for i in range(0x4000):
        write_byte_to_VRAM(0)
    
    # VDP_MODE_G1‎
    if mode == VDP_MODE_G1:
        set_register(0, 0x00)
        set_register(1, 0xC0 | (big_sprites << 1) | magnify) # Ram size 16k, activate video output
        set_register(2, 0x05) # Name table at 0x1400
        set_register(3, 0x80) # Color, start at 0x2000
        set_register(4, 0x01) # Pattern generator start at 0x800
        set_register(5, 0x20) # Sprite attributes start at 0x1000
        set_register(6, 0x00) # Sprite pattern table at 0x000
        SPRITE_PATTERNS = 0x00
        PATTERN_TABLE = 0x800
        SPRITE_ATTRIBUTES = 0x1000
        NAME_TABLE = 0x1400
        COLOR_TABLE = 0x2000
        color_table_size = 32
        # Initialize pattern table with ASCII patterns
        set_write_address(PATTERN_TABLE + 0x100)
        for b in ASCII:
            write_byte_to_VRAM(b)
        vdp_set_bdcolor(color)
    
    # VDP_MODE_TEXT
    elif mode == VDP_MODE_TEXT:
        set_register(0, 0x00)
        set_register(1, 0xD0) # Ram size 16k, Disable Int
        set_register(2, 0x02) # Name table at 0x800
        set_register(4, 0x00) # Pattern table start at 0x0
        PATTERN_TABLE = 0x00
        NAME_TABLE = 0x800
        crsr_max_x = 39
        # Initialize pattern table with ASCII patterns
        set_write_address(PATTERN_TABLE + 0x100)
        for b in ASCII:
            write_byte_to_VRAM(b)
        vdp_textcolor(VDP_WHITE, color)
    
    elif mode == VDP_MODE_MULTICOLOR:
        set_register(0, 0x00)
        set_register(1, 0xC8 | (big_sprites << 1) | magnify) # Ram size 16k, Multicolor
        set_register(2, 0x05) # Name table at 0x1400
        # set_register(3, 0xFF) # Color table not available
        set_register(4, 0x01) # Pattern table start at 0x800
        set_register(5, 0x76) # Sprite Attribute table at 0x1000
        set_register(6, 0x03) # Sprites Pattern Table at 0x0
        PATTERN_TABLE = 0x800
        NAME_TABLE = 0x1400
        set_write_address(NAME_TABLE) # Init name table
        for j in range(24):
            for i in range(32):
                write_byte_to_VRAM(i + 32 * (j // 4))

vdp_init(VDP_MODE_TEXT, VDP_BLACK, True, False)

vdp_print("""MICRO JOY HOME VIDEO COMPUTER\nVERSION 2025.08.16\nCOPYRIGHT (C) 2024-2025 KYUCHUMIMO

THIS SOFTWARE COMES WITH ABSOLUTELY NO
WARRANTY, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.
""", 0, 0)

# AUDIO
import music810_spi

sck = Pin(2, Pin.OUT)
sck.high()
sck.low()
sck.high()
time.sleep(1)

music = music810_spi.Music810(SPI(0, baudrate=10_000_000, sck=Pin(2), mosi=Pin(3)), Pin(4, Pin.OUT))

music.play_notes("SO4GGO5CEQG")

# INPUT
dataPin0 = Pin(22, Pin.IN, Pin.PULL_UP)
dataPin1 = Pin(26, Pin.IN, Pin.PULL_UP)
clockPin = Pin(20, Pin.OUT)
latchPin = Pin(21, Pin.OUT)

btn0 = [False] * 8
btn1 = [False] * 8

def read_input():
    # Step 1: Sample
    latchPin.high()
    latchPin.low()
    
    # Step 2: Shift
    for i in range(8):
        bit0 = dataPin0.value()
        bit1 = dataPin1.value()
        
        if not(bit0) and not btn0[i]:
            btn0[i] = True
            return i, None
        elif bit0 and btn0[i]:
            btn0[i] = False
        
        if not(bit1) and not btn1[i]:
            btn1[i] = True
            return None, i
        elif bit1 and btn1[i]:
            btn1[i] = False
        
        clockPin.high() # Shift out the next bit
        clockPin.low()
    return None, None

# in_shiftdir=rp2.PIO.SHIFT_RIGHT -> shift received bits to right
# autopush=True, push_thresh=11   -> push to receive queue when 11 bits are shifted
# fifo_join=rp2.PIO.JOIN_RX       -> join tx queue into rx queue
@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_RIGHT, autopush=True, push_thresh=11, fifo_join=rp2.PIO.JOIN_RX)
def rdKbd():
    wrap_target()
    wait (1, pin, 1)
    wait (0, pin, 1)
    in_ (pins, 1)
    wrap()

# Configure input pins
pin27 = Pin(27, Pin.IN, Pin.PULL_UP)
pin28 = Pin(28, Pin.IN, Pin.PULL_UP)

# A 100kHz clock for the State Machine is enough for the (around) 12kHz clock of the keyboard
# Input pin numbers for the State Machine start at pin 14
kb_sm = rp2.StateMachine(2, rdKbd, freq=120000, in_base=pin27)

# Activate the State Machine
kb_sm.active(1)

# PERSISTENT MEMORY
SAVEID = ""

# TIC-80'S PMEM() FUNCTION, https://github.com/nesbox/TIC-80/wiki/pmem
def pmem(index, val32=None):
    """
    Usage:
            pmem index -> val32 Retrieve data from persistent memory file
            pmem index val32 Save new value to persistent memory file
    Parameters:
            index : an index (0..255) into the persistent memory file.
            val32 : the 32-bit integer value you want to store. Omit this parameter to read vs write.
    Returns:
            val32 : the current value saved to the specified memory slot.
    Description:
            This function allows you to save and retrieve data in one of the 256 individual 32-bit slots available in the file's persistent memory. This is useful for saving high-scores, level advancement or achievements. Data is stored as unsigned 32-bit integer (from 0 to 4294967295).
    """
    import json
    
    index = int(index)
    if val32 is not None: int(val32)
    
    if val32 == None:
        try:
            with open(f'/{SAVEID}', 'r') as file:
                data = json.load(file)
                return data[f"{index%256}"]
        except (OSError, KeyError) as e:
            return 0
    else:
        try:
            with open(f'/{SAVEID}', 'r') as file:
                data = json.load(file)
                prior_val32 = data[f"{index%256}"]
        except (OSError, KeyError) as e:
            prior_val32 = 0
        
        try:
            with open(f'/{SAVEID}', 'r') as file:
                data = json.load(file)
                data[f"{index%256}"] = val32%2**32
            with open(f'/{SAVEID}', 'w') as file:
                json.dump(data,file)
        except (OSError, KeyError) as e:
            with open(f'/{SAVEID}', 'w') as file:
                data = dict()
                data[f"{index%256}"] = val32%2**32
                json.dump(data,file)
        
        return prior_val32




