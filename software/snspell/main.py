from machine import SPI, Pin

try:
    from spiram import SPIRAM
except (ImportError):
    raise ImportError("spiram lib not found. see: https://github.com/peterhinch/micropython_eeprom/blob/master/spiram/SPIRAM.md")

def mem_load_bin(filename, block_size=4096, verify=False):
    # LOADING...
    for i in range(248, 256):
        vdp_mset(i-248, 23, i)
    vdp_mset(8, 23, 255)
    vdp_mset(9, 23, 255)

    rst = Pin(0, Pin.OUT, value=0)           # reset the IC

    cspins = [Pin(17, Pin.OUT, value=1)]
    ram = SPIRAM(spi=SPI(0, baudrate=20_000_000, sck=Pin(18), mosi=Pin(19), miso=Pin(16)), cspins=cspins, verbose=False)
    
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

            # Ensures that the memory has the necessary size to write the block
            ram[start:end] = data
            
            if verify:
                if ram[start:end] == data:
                    print(f"mem[{start:06x}:{end:06x}] OK")
                else:
                    print(f"mem[{start:06x}:{end:06x}] BAD")
                    print('Verification failed')
                    
                    break

            # Updates the starting position for the next block
            start = end

    Pin(0, mode=Pin.IN, pull=None)
    Pin(16, mode=Pin.IN, pull=None)
    Pin(17, mode=Pin.IN, pull=None)
    Pin(18, mode=Pin.IN, pull=None)
    Pin(19, mode=Pin.IN, pull=None)
    
    print('Done')
    for i in range(10):
        vdp_mset(i, 23, 0)

import random
#####################################
vdp_init(VDP_MODE_G1, VDP_BLACK, True, False)

ASSET_PATH = '/snspell/assets'

vdp_sync(0, 0)

#####################################

keymap  = {0x01:"F9", 0x03:"F5", 0x04:"F3", 0x05:"F1", 0x06:"F2", 0x07:"F12", 0x09:"F10", 0x0A:"F8", 0x0B:"F6", 0x0C:"F4", 0x0D:"Tab", 0x0E:"`", 0x11:"Alt", 0x12:"Shift (Left)", 0x14:"Ctrl", 0x15:"Q", 0x16:"1", 0x1A:"Z", 0x1B:"S", 0x1C:"A", 0x1D:"W", 0x1E:"2", 0x1F:"Windows (left)", 0x21:"C", 0x22:"X", 0x23:"D", 0x24:"E", 0x25:"4", 0x26:"3", 0x27:"Windows (right)", 0x29:"Spacebar", 0x2A:"V", 0x2B:"F", 0x2C:"T", 0x2D:"R", 0x2E:"5", 0x2F:"Menus", 0x31:"N", 0x32:"B", 0x33:"H", 0x34:"G", 0x35:"Y", 0x36:"6", 0x3A:"M", 0x3B:"J", 0x3C:"U", 0x3D:"7", 0x3E:"8", 0x41:",", 0x42:"K", 0x43:"I", 0x44:"O", 0x45:"0", 0x46:"9", 0x49:".", 0x4A:"/", 0x4B:"L", 0x4C:";", 0x4D:"P", 0x4E:"-", 0x52:"'", 0x54:"[", 0x55:"=", 0x58:"Caps Lock", 0x59:"Shift (Right)", 0x5A:"Enter", 0x5B:"]", 0x5D:"\\", 0x66:"Backspace", 0x69:"1", 0x6B:"4", 0x6C:"7", 0x70:"0", 0x71:".", 0x72:"2", 0x73:"5", 0x74:"6", 0x75:"8", 0x76:"ESC", 0x77:"Num Lock", 0x78:"F11", 0x79:"+", 0x7A:"3", 0x7B:"-", 0x7C:"*", 0x7D:"9", 0x7E:"Scroll Lock", 0x83:"F7", 0xE0:"Extended", 0xF0:"Release"}

RELEASE = False
EXTENDED = False
CAPS = False

####################################################
try:
    import wt588d
except (ImportError):
    raise ImportError("wt588d lib not found. see: https://github.com/Kyuchumimo/Micro-Joy-Home-Video-Computer/blob/main/lib/wt588d.py")

rstPin = Pin(0)
sdaPin = Pin(1)

voice = wt588d.WT588D(rstPin, sdaPin)

# Pinout setup
BUSY_PIN = 5
LED_PIN = 'LED'

led = Pin(LED_PIN, Pin.OUT, value=0)
busy = Pin(BUSY_PIN, Pin.IN)

# Interrupt function to handle busy status changes
def busy_irq_handler(pin):
    led.value(not pin.value())  # Changes the LED status to reflect busy status
    vdp_set_bdcolor(not pin.value() and 9 or 1)

# Configures the interrupt to detect edge changes (positive and negative)
busy.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=busy_irq_handler)

def snspell_disp(word):
    for count, value in enumerate(f"{word:8s}"[:8].upper()):
        vdp_mset(14+count, 8, ord(value))
        vdp_mset(14+count, 9, ord(value)+64)

def random_list(n):
    # Fill list with values from 0 to n-1
    l = list(range(n))

    # Shuffling with Fisher-Yates
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)
        l[i], l[j] = l[j], l[i]

    return l

# SCANCODE TO ASSIGNED VOICE LOOK-UP TABLE
letters = {
0x52:0,   # '
0x1C:1,   # A
0x32:2,   # B
0x21:3,   # C
0x23:4,   # D
0x24:5,   # E
0x2B:6,   # F
0x34:7,   # G
0x33:8,   # H
0x43:9,   # I
0x3B:10,  # J
0x42:11,  # K
0x4B:12,  # L
0x3A:13,  # M
0x31:14,  # N
0x44:15,  # O
0x4D:16,  # P
0x15:17,  # Q
0x2D:18,  # R
0x1B:19,  # S
0x2C:20,  # T
0x3C:21,  # U
0x2A:22,  # V
0x1D:23,  # W
0x22:24,  # X
0x35:25,  # Y
0x1A:26   # Z
}

# ENCODER LOOK-UP TABLE
encoder = {
'@':'@',
'A':'F',
'B':'E',
'C':'D',
'D':'C',
'E':'B',
'F':'A',
'G':'Z',
'H':'Y',
'I':'X',
'J':'W',
'K':'V',
'L':'U',
'M':'T',
'N':'S',
'O':'R',
'P':'Q',
'Q':'P',
'R':'O',
'S':'N',
'T':'M',
'U':'L',
'V':'K',
'W':'J',
'X':'I',
'Y':'H',
'Z':'G'
}
    
# WORD LIST DIVIDED INTO FOUR LEVELS OF DIFFICULTY
word_list = (
(
'ABOVE',  # LEVEL A
'ANGEL',
'ANSWER',
'CALF',
'DOES',
'EARTH',
'ECHO',
'EXTRA',
'FIVE',
'FOR',
'FOUR',
'GUESS',
'HALF',
'HEALTH',
'IRON',
'LEARN',
'NINE',
'OCEAN',
'ONCE',
'ONE',
'OVEN',
'PINT',
'PULL',
'RANGE',
'SAYS',
'SIX',
'SKI',
'SURE',
'SWAP',
'TALK',
'TEN',
'THREE',
'TO',
'TOUCH',
'TWO',
'VIEW',
'WARM',
'WAS',
'WASH',
'WORD',
'ZERO'
),
           
(
'ANOTHER',  # LEVEL B
'BEAUTY',
'BEIGE',
'BLOOD',
'BULLET',
'CARRY',
'CHALK',
'CHILD',
'DANGER',
'EARLY',
'EIGHT',
'FLOOD',
'FLOOR',
'FRONT',
'GUIDE',
'HASTE',
'HEAVEN',
'LINGER',
'MIRROR',
'OTHER',
'PRIEST',
'READY',
'RURAL',
'SCHOOL',
'SEVEN',
'SQUAD',
'SQUAT',
'SUGAR',
'TODAY',
'UNION',
'WATCH',
'WATER',
'YIELD'
),
           
(
'ALREADY',  # LEVEL C
'BELIEVE',
'BUILT',
'BUSHEL',
'COMFORT',
'COMING',
'COUPLE',
'COUSIN',
'ENOUGH',
'FINGER',
'GUARD',
'HEALTHY',
'HEAVY',
'INSTEAD',
'LAUGH',
'MEASURE',
'MOTHER',
'NIECE',
'OUTDOOR',
'PERIOD',
'PLAGUE',
'POLICE',
'PROMISE',
'QUIET',
'RANGER',
'RELIEF',
'REMOVE',
'SEARCH',
'SHIELD',
'SHOULD',
'SHOVEL',
'SOMEONE',
'SOURCE',
'STATUE',
'TERROR',
'TROUBLE',
'WELCOME',
'WOLVES',
'WOMAN',
'WONDER',
'WORTH'
),
           
(
'ABSCESS',  # LEVEL D
'ANCIENT',
'ANYTHING',
'BROTHER',
'BUREAU',
'BUTCHER',
'CARAVAN',
'CIRCUIT',
'CORSAGE',
"COULDN@T",
'COURAGE',
'DISCOVER',
'DUNGEON',
'EARNEST',
'FEATHER',
'GREATER',
'JEALOUS',
'JOURNEY',
'LANGUAGE',
'LAUGHTER',
'LEISURE',
'LETTUCE',
'MACHINE',
'MINUTE',
'PIERCE',
'PLEASURE',
'PLUNGER',
'POULTRY',
'QUOTIENT',
'RHYTHM',
'SCHEDULE',
'SCISSORS',
'SERIOUS',
'SHOULDER',
'STOMACH',
'STRANGER',
'SURGEON',
'TOMORROW',
'TREASURE',
'WORKMAN',
'YACHT'
)
)

power = False
go = False
mode = ''
word = ''
word_input = ''
words_group = []
level = 0
lives = 7
spelling = 0
score = 0

while True:
    # sm.get() waits for a value in the rx queue and returns it
    # The shift and and discard the start, parity and stop bits and align the scan code to the right
    kbdat = (kb_sm.get() >> 22) & 0xFF
    
    try:
        if RELEASE:
            EXTENDED = False
            RELEASE = False
        else:
            if kbdat in (0xE0, 0xF0):
                if kbdat == 0xF0:
                    RELEASE = True
                elif kbdat == 0xE0:
                    EXTENDED = True
                
                continue
            
            print(f'{kbdat:02X} - {keymap[kbdat]}')
            
            rng = random.randint(0, 255)
            if kbdat == 0x46:  # 9
                mode = 'spell'
                go = False
                
                snspell_disp(f"{mode:<7}{chr(level+65)}")
                
                if power:                    
                    voice.send_oneline((216, 217, 218, 219)[rng%4])
                    time.sleep_ms(32)
                    
                    while not busy.value():
                        pass
                else:
                    mem_load_bin("/snspell/assets/voices/snspell1.winproj.bin")
                    time.sleep_ms(20)
                    
                    voice.send_oneline(216)
                    time.sleep_ms(32)
                    
                    while not busy.value():
                        pass
                
                power = True
            
            if power:
                if go and mode == 'say it' and kbdat in (0x2E, 0x36, 0x3D, 0x3E, 0x46):
                    mem_load_bin("/snspell/assets/voices/snspell1.winproj.bin")
                    time.sleep_ms(20)
                
                if kbdat == 0x16:  # 1: GO
                    go = True
                    
                    if mode == 'say it' or mode == 'spell':
                        if level == 0:
                            mem_load_bin("/snspell/assets/voices/snspell2.winproj.bin")
                        elif level == 1:
                            mem_load_bin("/snspell/assets/voices/snspell3.winproj.bin")
                        elif level == 2:
                            mem_load_bin("/snspell/assets/voices/snspell4.winproj.bin")
                        elif level == 3:
                            mem_load_bin("/snspell/assets/voices/snspell5.winproj.bin")
                        time.sleep_ms(20)
                        
                        spelling = 0
                        words_group = random_list(len(word_list[level]))[:10]
                        word = word_list[level][words_group[spelling]]
                    
                    if mode == 'spell':
                        lives = 2
                        score = 0
                        
                        word_input = ''
                        snspell_disp((word_input + "_")[:8])
                        
                        voice.send_oneline(214)  # "SPELL"
                        time.sleep_ms(32)
                        time.sleep(1)
                        
                        while not busy.value():
                            pass
                        
                        voice.send_oneline(word_list[level].index(word))  # "..."
                        time.sleep_ms(32)
                        
                        while not busy.value():
                            pass
                        
                        mem_load_bin("/snspell/assets/voices/snspell1.winproj.bin")
                        time.sleep_ms(20)
                
                elif kbdat == 0x1E:  # 2: REPLAY
                    if mode == 'spell':
                        if level == 0:
                            mem_load_bin("/snspell/assets/voices/snspell2.winproj.bin")
                        elif level == 1:
                            mem_load_bin("/snspell/assets/voices/snspell3.winproj.bin")
                        elif level == 2:
                            mem_load_bin("/snspell/assets/voices/snspell4.winproj.bin")
                        elif level == 3:
                            mem_load_bin("/snspell/assets/voices/snspell5.winproj.bin")
                        time.sleep_ms(20)
                        
                        lives = 2
                        spelling = 0
                        score = 0
                        
                        word = word_list[level][words_group[spelling]]
                        word_input = ''
                        snspell_disp((word_input + "_")[:8])
                        
                        voice.send_oneline(214)  # "SPELL"
                        time.sleep_ms(32)
                        time.sleep(1)
                        
                        while not busy.value():
                            pass
                        
                        voice.send_oneline(word_list[level].index(word))  # "..."
                        time.sleep_ms(32)
                        
                        while not busy.value():
                            pass
                        
                        mem_load_bin("/snspell/assets/voices/snspell1.winproj.bin")
                        time.sleep_ms(20)
                elif kbdat == 0x26:  # 3: REPEAT
                    if mode == 'spell':
                        if level == 0:
                            mem_load_bin("/snspell/assets/voices/snspell2.winproj.bin")
                        elif level == 1:
                            mem_load_bin("/snspell/assets/voices/snspell3.winproj.bin")
                        elif level == 2:
                            mem_load_bin("/snspell/assets/voices/snspell4.winproj.bin")
                        elif level == 3:
                            mem_load_bin("/snspell/assets/voices/snspell5.winproj.bin")
                        time.sleep_ms(20)
                        
                        voice.send_oneline(word_list[level].index(word)) # "..."
                        time.sleep_ms(32)
                        
                        while not busy.value():
                            pass
                        
                        mem_load_bin("/snspell/assets/voices/snspell1.winproj.bin")
                        time.sleep_ms(20)
                
                elif kbdat == 0x25:  # 4: CLUE
                    if mode == 'mystery word' and lives > 0 and not(word == ''.join(word_input)):
                        lives = max(lives-2, 0)
                        
                        if lives > 0:
                            matching_indices = [i for i, val in enumerate(word_input) if val == '_']

                            target_value = ord(word[matching_indices[rng%len(matching_indices)]])-64

                            for key, value in letters.items():
                             if value == target_value:
                                 found_key = key
                                 break

                            kbdat = found_key
                        else:
                            snspell_disp(word)
                            
                            voice.send_oneline(203) # "I WIN"
                            time.sleep_ms(32)
                            time.sleep(1)
                            
                            while not busy.value():
                                pass
                
                elif kbdat == 0x2E:  # 5
                    mode = 'mystery word'
                    go = True
                    
                    lives = 7
                    
                    word = word_list[(rng%2)+2][rng%len(word_list[(rng%2)+2])]
                    word_input = ['_']*len(word)
                    snspell_disp(''.join(word_input))
                    
                    voice.send_oneline((216, 217, 218, 219)[rng%4])
                    time.sleep_ms(32)
                    time.sleep(1)
                    
                    while not busy.value():
                        pass
                
                elif kbdat == 0x36:  # 6
                    mode = 'secret code'
                    go = True
                    
                    word = ''
                    word_input = []
                    
                    snspell_disp((''.join(word_input) + "_")[:8])
                    
                    voice.send_oneline((216, 217, 218, 219)[rng%4])
                    time.sleep_ms(32)
                    
                    while not busy.value():
                        pass
                
                elif kbdat == 0x3D:  # 7
                    mode = 'letter'
                    go = True
                    
                    word_input = chr((rng%26+1)+64)
                    snspell_disp(word_input + "_")
                    
                    voice.send_oneline(rng%26+1)
                    time.sleep_ms(32)
                    
                    while not busy.value():
                        pass
                
                elif kbdat == 0x3E:  # 8
                    mode = 'say it'
                    go = False
                    
                    snspell_disp(f"{mode:<7}{chr(level+65)}")
                    
                    voice.send_oneline((216, 217, 218, 219)[rng%4])
                    time.sleep_ms(32)
                    
                    while not busy.value():
                        pass
                
                # RUNNING
                if go:
                    if mode == "mystery word":
                        if kbdat in letters:
                            voice.send_oneline(letters[kbdat])
                            time.sleep_ms(32)
                            time.sleep(1)
                        
                            while not busy.value():
                                pass
                        
                            if lives > 0 and not(word == ''.join(word_input)):
                                if (chr(letters[kbdat]+64) in word) and not (chr(letters[kbdat]+64) in word_input):
                                    for i, c in enumerate(word):
                                        if c == chr(letters[kbdat]+64):
                                            word_input[i] = c
                                    
                                    snspell_disp(''.join(word_input))
                                    
                                    if word == ''.join(word_input):
                                        voice.send_oneline(215) # "YOU WIN"
                                        time.sleep_ms(32)
                                        time.sleep(1)
                                    
                                        while not busy.value():
                                            pass
                                    else:
                                        voice.send_oneline((216, 217, 218, 219)[rng%4]) # MELODY
                                        time.sleep_ms(32)
                                        time.sleep(1)
                                    
                                        while not busy.value():
                                            pass
                                    
                                    time.sleep_ms(32)
                                    
                                    while not busy.value():
                                        pass
                                    
                                else:
                                    lives -= 1
                                
                                if lives == 0:
                                    snspell_disp(word)
                                    
                                    voice.send_oneline(203) # "I WIN"
                                    time.sleep_ms(32)
                                    time.sleep(1)
                                    
                                    while not busy.value():
                                        pass
                    
                    elif mode == 'secret code':
                        if kbdat == 0x66:     # BACKSPACE
                            word_input = []
                            snspell_disp((''.join(word_input) + "_")[:8])
                        elif kbdat == 0x5A:   # ENTER
                            for i, c in enumerate(word_input):
                                word_input[i] = encoder[c]
                            snspell_disp(''.join(word_input)[:8])
                            
                            voice.send_oneline((216, 217, 218, 219)[rng%4]) # MELODY
                            time.sleep_ms(32)
                            
                            while not busy.value():
                                pass
                        
                        if kbdat in letters and len(word_input)<8:
                            word_input.append(chr(letters[kbdat]+64))
                            snspell_disp((''.join(word_input) + "_")[:8])

                            voice.send_oneline(letters[kbdat])
                            time.sleep_ms(32)
                            
                            while not busy.value():
                                pass
                    
                    elif mode == 'letter':
                        if kbdat == 0x66:     # BACKSPACE
                            word_input = ''
                            snspell_disp((word_input + "_")[:8])
                        
                        if kbdat in letters and len(word_input)<8:
                            word_input += chr(letters[kbdat]+64)
                            snspell_disp((word_input + "_")[:8])
                            
                            voice.send_oneline(letters[kbdat])
                            time.sleep_ms(32)
                            
                            while not busy.value():
                                pass
                    
                    elif mode == 'say it':
                        for i in range(10):
                            word = word_list[level][words_group[spelling]]
                            snspell_disp(word)
                            
                            voice.send_oneline(213) # "SAY IT"
                            time.sleep_ms(32)
                            time.sleep(1.5)
                            
                            while not busy.value():
                                pass
                            
                            voice.send_oneline(word_list[level].index(word))  # "..."
                            time.sleep_ms(32)
                            time.sleep(2)
                            
                            while not busy.value():
                                pass
                            
                            spelling += 1
                        
                        mode = 'spell'
                        
                        lives = 2
                        spelling = 0
                        score = 0
                        
                        word = word_list[level][words_group[spelling]]
                        word_input = ''
                        snspell_disp((word_input + "_")[:8])
                        
                        voice.send_oneline(214)  # "SPELL"
                        time.sleep_ms(32)
                        time.sleep(1)
                        
                        while not busy.value():
                            pass
                        
                        voice.send_oneline(word_list[level].index(word))  # "..."
                        time.sleep_ms(32)
                        
                        while not busy.value():
                            pass
                        
                        mem_load_bin("/snspell/assets/voices/snspell1.winproj.bin")
                        time.sleep_ms(20)
                    elif mode == 'spell':
                        if kbdat == 0x66:    # BACKSPACE
                            word_input = ''
                            snspell_disp((word_input + "_")[:8])
                        elif kbdat == 0x5A:  # ENTER
                            snspell_disp((word_input)[:8])
                            
                            if word == word_input:  # OK
                                voice.send_oneline((207, 209, 213, 214)[rng%4])
                                time.sleep_ms(32)
                                
                                while not busy.value():
                                    pass
                                
                                lives = 2
                                spelling += 1
                                score += 1
                                
                                if spelling < 10:
                                    word = word_list[level][words_group[spelling]]
                            else:  # BAD
                                if lives > 0:
                                    lives -= 1
                                
                                voice.send_oneline((208, 212)[lives])  # "THAT IS INCORRECT/WRONG, TRY AGAIN"
                                time.sleep_ms(32)
                                time.sleep(1)
                                
                                while not busy.value():
                                    pass
                                
                                if lives == 0:
                                    voice.send_oneline(210)  # "THE CORRECT SPELLING OF"
                                    time.sleep_ms(32)
                                    time.sleep(1)
                                    
                                    while not busy.value():
                                        pass
                                    
                                    if level == 0:
                                        mem_load_bin("/snspell/assets/voices/snspell2.winproj.bin")
                                    elif level == 1:
                                        mem_load_bin("/snspell/assets/voices/snspell3.winproj.bin")
                                    elif level == 2:
                                        mem_load_bin("/snspell/assets/voices/snspell4.winproj.bin")
                                    elif level == 3:
                                        mem_load_bin("/snspell/assets/voices/snspell5.winproj.bin")
                                    time.sleep_ms(20)
                                    
                                    voice.send_oneline(word_list[level].index(word))  # "..."
                                    time.sleep_ms(32)
                                
                                    while not busy.value():
                                        pass
                                    
                                    mem_load_bin("/snspell/assets/voices/snspell1.winproj.bin")
                                    time.sleep_ms(20)
                                    
                                    voice.send_oneline(204)  # "IS"
                                    time.sleep_ms(32)
                                    time.sleep(1)
                                    
                                    while not busy.value():
                                        pass
                                    
                                    for i, c in enumerate(word):
                                        snspell_disp(word[:i+1])
                                        
                                        voice.send_oneline(ord(c)-64)  # "ABC"
                                        time.sleep_ms(32)
                                        time.sleep(0.75)
                                        
                                        while not busy.value():
                                            pass
                                    
                                    if level == 0:
                                        mem_load_bin("/snspell/assets/voices/snspell2.winproj.bin")
                                    elif level == 1:
                                        mem_load_bin("/snspell/assets/voices/snspell3.winproj.bin")
                                    elif level == 2:
                                        mem_load_bin("/snspell/assets/voices/snspell4.winproj.bin")
                                    elif level == 3:
                                        mem_load_bin("/snspell/assets/voices/snspell5.winproj.bin")
                                    time.sleep_ms(20)
                                    
                                    voice.send_oneline(word_list[level].index(word))  # "..."
                                    time.sleep_ms(32)
                                    time.sleep(1)
                                
                                    while not busy.value():
                                        pass
                                    
                                    lives = 2
                                    spelling += 1
                                    
                                    if spelling < 10:
                                        word = word_list[level][rng%len(word_list[level])]
                            
                            if spelling<10:
                                if level == 0:
                                    mem_load_bin("/snspell/assets/voices/snspell2.winproj.bin")
                                elif level == 1:
                                    mem_load_bin("/snspell/assets/voices/snspell3.winproj.bin")
                                elif level == 2:
                                    mem_load_bin("/snspell/assets/voices/snspell4.winproj.bin")
                                elif level == 3:
                                    mem_load_bin("/snspell/assets/voices/snspell5.winproj.bin")
                                time.sleep_ms(20)
                                
                                word_input = ''
                                snspell_disp((word_input + "_")[:8])
                                
                                if lives>1:
                                    voice.send_oneline((210, 211, 212)[rng%3]) # "NEXT SPELL/NOW SPELL/NOW TRY"
                                    time.sleep_ms(32)
                                    time.sleep(1)
                                    
                                    while not busy.value():
                                        pass
                                
                                voice.send_oneline(word_list[level].index(word)) # "..."
                                time.sleep_ms(32)
                                
                                while not busy.value():
                                    pass
                                
                                mem_load_bin("/snspell/assets/voices/snspell1.winproj.bin")
                                time.sleep_ms(20)
                            else:
                                mem_load_bin("/snspell/assets/voices/snspell1.winproj.bin")
                                time.sleep_ms(20)
                                
                                snspell_disp(f"{'+'+str(score):<4}{'-'+str(10-score):>4}"[:8])  # SCORE
                                
                                voice.send_oneline((216, 217, 218, 219)[rng%4]) # MELODY
                                time.sleep_ms(32)
                                time.sleep(1)
                                
                                while not busy.value():
                                    pass
                                
                                voice.send_oneline((216, 217, 218, 219)[rng%4]) # MELODY
                                time.sleep_ms(32)
                                time.sleep(1)
                                
                                while not busy.value():
                                    pass
                                
                                if score < 10:
                                    voice.send_oneline(202) # "HERE IS YOUR SCORE"
                                    time.sleep_ms(32)
                                    time.sleep(1)
                                    
                                    while not busy.value():
                                        pass
                                    
                                    voice.send_oneline(190+score)  # NUMBER CORRECT
                                    time.sleep_ms(32)
                                    time.sleep(1)
                                    
                                    while not busy.value():
                                        pass
                                    
                                    voice.send_oneline(201)  # "CORRECT"
                                    time.sleep_ms(32)
                                    time.sleep(1)
                                    
                                    while not busy.value():
                                        pass
                                    
                                    voice.send_oneline(190+(10-score))  # NUMBER WRONG
                                    time.sleep_ms(32)
                                    time.sleep(1)
                                    
                                    while not busy.value():
                                        pass
                                    
                                    voice.send_oneline(211)  # "WRONG"
                                    time.sleep_ms(32)
                                    
                                    while not busy.value():
                                        pass
                                else:
                                    voice.send_oneline(205) # "PERFECT SCORE"
                                    time.sleep_ms(32)
                                    
                                    while not busy.value():
                                        pass
                                
                                go = False
                        
                        if kbdat in letters and len(word_input)<8:
                            word_input += chr(letters[kbdat]+64)
                            snspell_disp((word_input + "_")[:8])
                            
                            voice.send_oneline(letters[kbdat])
                            time.sleep_ms(32)
                            
                            while not busy.value():
                                pass
                else:
                    if kbdat == 0x1C:    # LEVEL A
                        level = 0
                    elif kbdat == 0x32:  # LEVEL B
                        level = 1
                    elif kbdat == 0x21:  # LEVEL C
                        level = 2
                    elif kbdat == 0x23:  # LEVEL D
                        level = 3
                    
                    if not mode == '':
                        snspell_disp(f"{mode:<7}{chr(level+65)}")
                        if kbdat in letters:
                            voice.send_oneline(letters[kbdat])
                            time.sleep_ms(32)
                            
                            while not busy.value():
                                pass
    except KeyError:
        print(f"Unknown scancode: {kbdat:02X}")
