vdp_init(VDP_MODE_G1, VDP_BLACK, False, False)

ASSET_PATH = '/galaxy_beam/assets'
SAVEID = 'galaxy_beam'

vdp_sync()

vdp_print(f"{0:<5d}",7,1)
vdp_print(f"{0:<5d}",7,3)
vdp_print(f"{1:<4d}",7,4)
vdp_print(1,7,5)

stars = (bytearray(b' p\xf8p \x00\x00\x00'), bytearray(b'  \xf8  \x00\x00\x00'), bytearray(b'\x00 p \x00\x00\x00\x00'), bytearray(b'\x00\x00 \x00\x00\x00\x00\x00'), bytearray(b'\x00 p \x00\x00\x00\x00'), bytearray(b'  \xf8  \x00\x00\x00'))

#####################################

import random
import math

hi_score=0
shake=0
d=2
v=0
t=0
fade=0
fade_frame=0
menu_selection=0
music_on=True

# Reset general variables

def init():
    global b
    global e
    global beam_generators
    global level_points
    global lose_tile
    global mode
    
    b={
        "x":16*8,
        "y":12*8,
        "dir":'none',
        "s":4
    }
    e={
        "x":-8,
        "y":-8,
        "dir":'none',
        "initial_s":0.3,
        "s":0.3,
        "type":1,
        "h":1,
        "oldx":-8,
        "oldy":-8,
        "f":0
    }
    level_points=0
    beam_generators=3
    lose_tile=5
    mode='title'
    
    new_e()

# Reset score variables

def reset_stats():
    global points
    global level
    global wave
    
    points=0
    level=1
    wave=1

# Generate a new enemy

def new_e():
    global e
    global new_dir
    
    # Set enemy type
    
    v=random.randint(1,8)
    if v<3:
        e["type"]=2
    else:
        e["type"]=1
    
    if e["type"]==1:
        e["h"]=1
    elif e["type"]==2:
        e["h"]=2
    
    vdp_mset(e["x"]/8,e["y"]/8,1)
    
    # Set enemy direction
    
    new_dir=random.randint(1,4)
    
    if new_dir==1:
        e["x"]=16*8
        e["y"]=4*8
        e["dir"]='d'
    
    elif new_dir==2:
        e["x"]=16*8
        e["y"]=20*8
        e["dir"]='u'
    
    elif new_dir==3:
        e["x"]=8*8
        e["y"]=12*8
        e["dir"]='r'
    
    elif new_dir==4:
        e["x"]=24*8+7
        e["y"]=12*8
        e["dir"]='l'

#Beam generator controls
# BUTTONMAP: A, B, SELECT, START, UP, DOWN, LEFT, RIGHT
def controls():
    global b
    global sfx, sfx_frame

    if btnp0 == 4:
        b["x"]=16*8
        b["y"]=9*8-1
        b["dir"]='u'
        
        sfx = 0
        sfx_frame = 0
        
    elif btnp0 == 5:
        b["x"]=16*8
        b["y"]=15*8+1
        b["dir"]='d'

        sfx = 0
        sfx_frame = 0
        
    elif btnp0 == 6:
        b["x"]=13*8+1
        b["y"]=12*8
        b["dir"]='l'

        sfx = 0
        sfx_frame = 0
        
    elif btnp0 == 7:
        b["x"]=19*8-1
        b["y"]=12*8
        b["dir"]='r'

        sfx = 0
        sfx_frame = 0

#Beam direction and movement

def beam():
    global b
    
    if b["dir"]=='u':
        b["y"]=b["y"]-b["s"]
    
    elif b["dir"]=='d':
        b["y"]=b["y"]+b["s"]
    
    elif b["dir"]=='l':
        b["x"]=b["x"]-b["s"]
    
    elif b["dir"]=='r':
        b["x"]=b["x"]+b["s"]
    
    elif b["dir"]=='none':
        b["x"]=16*8
        b["y"]=12*8
    
    if b["x"]>24*8 or b["x"]<8*8 or b["y"]>20*8 or b["y"]<4*8:
        b["dir"]='none'

#Enemy movement

def enemy():
    global e
    
    vdp_mset(e["x"]/8,e["y"]/8,1)
    
    if e["dir"]=='u':
        e["y"]=e["y"]-e["s"]
    
    elif e["dir"]=='d':
        e["y"]=e["y"]+e["s"]
    
    elif e["dir"]=='l':
        e["x"]=e["x"]-e["s"]
    
    elif e["dir"]=='r':
        e["x"]=e["x"]+e["s"]
    
    vdp_mset(math.floor(e["x"]/8),math.floor(e["y"]/8),4)

#Win/lose

def winlose():
    global b
    global beam_generators
    global e
    global fade
    global hi_score
    global lose_tile
    global points
    global shake
    global sfx, sfx_frame
    
    #Win
    
    if (b["x"]//8 == e["x"]//8) and (b["y"]//8 == e["y"]//8) or ((b["x"]+4)//8 == e["x"]//8) and (b["y"]//8 == e["y"]//8) or (b["x"]//8 == e["x"]//8) and ((b["y"]+4)//8 == e["y"]//8):
        b["dir"]='none'
        e["h"]=e["h"]-1
        points=points+1
        vdp_print(f"{points:<5d}",2,7)
        
        sfx = 1
        sfx_frame = 0
        
        if points>hi_score:
            hi_score=points
            vdp_print(f"{hi_score:<5d}",26,7)
        
        if e["h"]==0:
            e["s"]=e["s"]+0.005
            vdp_mset(e["oldx"]/8,e["oldy"]/8,1)
            e["oldx"]=e["x"]
            e["oldy"]=e["y"]
            e["oldtype"]=e["type"]
            e["f"]=0
            new_e()
            shake=4
     
    #Lose
    
    elif (e["y"]//8) == 9 or (e["x"]//8) == 19 or (e["y"]//8) == 15 or (e["x"]//8) == 13:
        
        sfx = 2
        sfx_frame = 0
        
        if beam_generators>0:
            beam_generators=beam_generators-1
            new_e()
            vdp_mset(lose_tile,12,4)
            lose_tile=lose_tile-1
            if beam_generators==0 and music_on==True:
                music.load_vgm(f"{ASSET_PATH}/music/7.vgm")
        else:
            e["s"]=0
            new_e()
            fade=1
        shake=20

init()
music.load_vgm(f"{ASSET_PATH}/music/5.vgm")

# channel, note, octave, vol
sfx_banks = [((1,4,5,15),
              (1,4,5,15),
              (1,4,6,14),
              (1,4,6,14),
              (1,5,6,13),
              (1,4,6,13),
              (1,1,6,12),
              (1,10,5,12),
              (1,6,5,11),
              (1,5,5,11),
              (1,9,11,0)),
             
             ((1,6,4,15),
              (1,5,4,14),
              (1,9,11,0)),
             
             ((1,7,3,15),
              (1,6,3,14),
              (1,5,3,13),
              (1,4,3,12),
              (1,3,3,11),
              (1,2,3,10),
              (1,1,3,9),
              (1,0,3,8),
              (1,11,2,7),
              (1,10,2,6),
              (1,9,2,5),
              (1,8,2,4),
              (1,7,2,3),
              (1,6,2,2),
              (1,5,2,1),
              (1,9,11,0)),
             
             ((1,6,4,15),
              (1,5,4,14),
              (1,0,0,0),
              (1,0,0,0),
              (1,0,0,0),
              (1,0,0,0),
              (1,0,0,0),
              (1,4,4,15),
              (1,4,4,15),
              (1,4,4,15),
              (1,4,4,15),
              (1,11,4,14),
              (1,11,4,14),
              (1,11,4,14),
              (1,11,4,14),
              (1,8,4,13),
              (1,8,4,13),
              (1,8,4,13),
              (1,8,4,13),
              (1,3,5,12),
              (1,3,5,12),
              (1,3,5,12),
              (1,3,5,12),
              (1,8,4,11),
              (1,8,4,11),
              (1,8,4,11),
              (1,8,4,11),
              (1,9,11,0)),
             
             ((1,2,4,14),
              (1,3,4,15),
              (1,4,4,15),
              (1,5,4,15),
              (1,6,4,15),
              (1,2,4,15),
              (1,3,4,15),
              (1,4,4,15),
              (1,5,4,15),
              (1,6,4,15),
              (1,7,4,15),
              (1,8,4,15),
              (1,9,4,15),
              (1,10,4,15),
              (1,2,4,15),
              (1,3,4,15),
              (1,4,4,15),
              (1,5,4,15),
              (1,6,4,15),
              (1,7,4,15),
              (1,8,4,15),
              (1,9,4,15),
              (1,10,4,15),
              (1,11,4,15),
              (1,0,5,15),
              (1,1,5,15),
              (1,2,5,15),
              (1,3,5,15),
              (1,4,5,15),
              (1,5,5,15),
              (1,9,11,0)),
             
             ((1,6,4,15),
              (1,5,4,14),
              (1,0,0,0),
              (1,0,0,0),
              (1,0,0,0),
              (1,0,0,0),
              (1,0,0,0),
              (1,8,4,15),
              (1,8,4,15),
              (1,8,4,15),
              (1,8,4,15),
              (1,3,5,14),
              (1,3,5,14),
              (1,3,5,14),
              (1,3,5,14),
              (1,8,4,13),
              (1,8,4,13),
              (1,8,4,13),
              (1,8,4,13),
              (1,11,4,12),
              (1,11,4,12),
              (1,11,4,12),
              (1,11,4,12),
              (1,4,4,11),
              (1,4,4,11),
              (1,4,4,11),
              (1,4,4,11),
              (1,9,11,0)),]

sfx_frame = 255
sfx = 0

#####################################

while True:
    # UPDATE
    delta = time.ticks_us()
        
    # INPUT READING
    btnp0, btnp1 = read_input()
    
    # BACKGROUND MUSIC
    if music_on: music.tick()
    
    # SOUND EFFECTS
    if not sfx_frame >= len(sfx_banks[sfx]):
        music._play_note(sfx_banks[sfx][sfx_frame][0], sfx_banks[sfx][sfx_frame][1], sfx_banks[sfx][sfx_frame][2])
        music.set_vol(sfx_banks[sfx][sfx_frame][0], sfx_banks[sfx][sfx_frame][3])
        sfx_frame += 1
    
    #Screen fade
    
    if fade==1 and v>0 and t%7==0: v=v-0.25
    if fade==0 and v<1 and t%7==0: v=v+0.25
    
    if mode is not 'pause':
        t = (t + 1) % 120

        if t%20==0:
            set_write_address(PATTERN_TABLE + 0x7C0)
            
            for i in range(3):
                for pattern_table_data in stars[(t//20 + i) % 6]:
                    write_byte_to_VRAM(pattern_table_data)

    #Game modes

    if mode=='title':
        # BUTTONMAP: A, B, SELECT, START, UP, DOWN, LEFT, RIGHT
        if btnp0 == 0: # A
            #sfx(13)
            fade=1
            fade_frame=1
        if fade_frame==1 and v==0:
            # Initialize sprite attributes
            vdp_sprite_init(0, 0, VDP_LIGHT_RED)
            vdp_sprite_init(1, 1, VDP_LIGHT_RED)
            vdp_sprite_init(1, 2, VDP_LIGHT_RED)
            vdp_sprite_init(1, 3, VDP_LIGHT_RED)
            vdp_sprite_init(1, 4, VDP_LIGHT_RED)
            vdp_sprite_init(2, 5, VDP_LIGHT_RED)
            vdp_sprite_init(3, 6, VDP_LIGHT_GREEN)
            
            vdp_sprite_set_position(1, 128, 71)
            vdp_sprite_set_position(2, 104, 95)
            vdp_sprite_set_position(3, 152, 95)
            vdp_sprite_set_position(4, 128, 119)
            
            vdp_sync(9, 1)
            
            reset_stats()
            mode='game'
            if music_on==True:
                music.load_vgm(f"{ASSET_PATH}/music/4.vgm")
            elif music_on==False:
                vdp_mset(31,23,241)
            fade=0
            fade_frame=0
            
            
            vdp_print(f"{points:<5d}",2,7)
            vdp_print(f"{hi_score:<5d}",26,7)
            vdp_print(level,26,12)
            vdp_print(f"{wave:<4d}",2,17)

    elif mode=='gameover':
        if btnp0 == 0: # A
            fade=1
            fade_frame=1
        if fade_frame==1 and v==0:
            vdp_sync(8, 0)
            
            vdp_print(f"{hi_score:<5d}",7,1)
            vdp_print(f"{points:<5d}",7,3)
            vdp_print(f"{wave:<4d}",7,4)
            vdp_print(level,7,5)
            
            mode='title'
            music.load_vgm(f"{ASSET_PATH}/music/5.vgm")
            fade=0
            fade_frame=0
    
    elif mode=='pause':
        v=0.75
        if btnp0 == 0: # A
            if menu_selection==0:
                vdp_sprite_init(0, 0, VDP_LIGHT_RED)
                vdp_sprite_init(1, 1, VDP_LIGHT_RED)
                vdp_sprite_init(1, 2, VDP_LIGHT_RED)
                vdp_sprite_init(1, 3, VDP_LIGHT_RED)
                vdp_sprite_init(1, 4, VDP_LIGHT_RED)
                vdp_sprite_init(2, 5, VDP_LIGHT_RED)
                vdp_sprite_init(3, 6, VDP_LIGHT_GREEN)
                
                vdp_sprite_set_position(1, 128, 71)
                vdp_sprite_set_position(2, 104, 95)
                vdp_sprite_set_position(3, 152, 95)
                vdp_sprite_set_position(4, 128, 119)
                
                set_write_address(NAME_TABLE + 569)
                for i in range(6):
                    write_byte_to_VRAM(224 + i)
                
                vdp_sync(1, 1)
                
                mode='game'
                
                sfx = 4
                sfx_frame = 0
            elif menu_selection==1:
                if music_on==True:
                    music_on=False
                    vdp_mset(31,23,241)
                    music.reset()
                elif music_on==False:
                    music_on=True
                    vdp_mset(31,23,240)
                    if beam_generators==0:
                        music.load_vgm(f"{ASSET_PATH}/music/7.vgm")
                    else:
                        music.load_vgm(f"{ASSET_PATH}/music/4.vgm")
        
        if btnp0 == 4: # UP
            menu_selection=0
            
            set_write_address(COLOR_TABLE + 29)
            write_byte_to_VRAM(0x74)
            write_byte_to_VRAM(0x54)
        elif btnp0 == 5: # DOWN
            menu_selection=1
            
            set_write_address(COLOR_TABLE + 29)
            write_byte_to_VRAM(0x54)
            write_byte_to_VRAM(0x74)
        
        if e["f"]<7:
            vdp_mset(math.floor(e["oldx"]/8),math.floor(e["oldy"]/8),176+e["f"])
        
    elif mode == 'game':
        enemy()
        winlose()
        controls()
        beam()
        
        if points==level_points+10*wave:
            level_points=points
            if level<5:
                level=level+1
                vdp_print(level,26,12)
                
                sfx = 3
                sfx_frame = 0
            else:
                e["s"]=e["initial_s"]
                level=1
                wave=wave+1
                vdp_print(level,26,12)
                vdp_print(f"{wave:<4d}",2,17)
                
                sfx = 5
                sfx_frame = 0
        
        if points>=99999: points=99999
    
        if btnp0 == 0 and v==1:
            vdp_sprite_init(0, 0, VDP_DARK_RED)
            vdp_sprite_init(1, 1, VDP_DARK_RED)
            vdp_sprite_init(1, 2, VDP_DARK_RED)
            vdp_sprite_init(1, 3, VDP_DARK_RED)
            vdp_sprite_init(1, 4, VDP_DARK_RED)
            vdp_sprite_init(2, 5, VDP_DARK_RED)
            vdp_sprite_init(3, 6, VDP_DARK_GREEN)
            
            vdp_sprite_set_position(1, 128, 71)
            vdp_sprite_set_position(2, 104, 95)
            vdp_sprite_set_position(3, 152, 95)
            vdp_sprite_set_position(4, 128, 119)
            
            set_write_address(NAME_TABLE + 569)
            for i in range(6):
                write_byte_to_VRAM(232 + i)
            
            set_write_address(COLOR_TABLE)
            for color_table_data in bytearray(b'Aa\xe1\xe1\xe4\xe4\xe4\xe4\xe4\xe4\xe4\xe4Ad\xa1\xa1\xa1\xa1aaaad\xc4\xe1\xe1\xe1\xe1TtT\xe1'):
                write_byte_to_VRAM(color_table_data)
            
            mode='pause'
            
            sfx = 4
            sfx_frame = 0
        
        if beam_generators==0 and v==0:
            # Initialize sprite attributes
            set_write_address(SPRITE_ATTRIBUTES)
            for _ in range(0x80):
                write_byte_to_VRAM(0x00)
            
            vdp_sync(9, 2)
            
            init()
            mode='gameover'
            music.load_vgm(f"{ASSET_PATH}/music/6.vgm")
            fade=0
        
        if e["type"]==1:
            vdp_sprite_set_position(5,math.floor(e["x"]/8)*8,math.floor(e["y"]/8)*8)
        else:
            vdp_sprite_set_position(5,-8,-8)
        if e["type"]==2:
            vdp_sprite_set_position(6,math.floor(e["x"]/8)*8,math.floor(e["y"]/8)*8)
        else:
            vdp_sprite_set_position(6,-8,-8)
        
        vdp_sprite_set_position(0, b["x"], b["y"])
        if e["f"]<7:
            if e["f"]<6:
                try:
                    if e["oldtype"]==1:
                        vdp_mset(math.floor(e["oldx"]/8),math.floor(e["oldy"]/8),176+e["f"])
                    elif e["oldtype"]==2:
                        vdp_mset(math.floor(e["oldx"]/8),math.floor(e["oldy"]/8),184+e["f"])
                except KeyError:
                    pass
            else:
                vdp_mset(math.floor(e["oldx"]/8),math.floor(e["oldy"]/8),1)
            e["f"]=e["f"]+0.2
        
        if shake>0:
            if shake>4:
                vdp_set_bdcolor(VDP_LIGHT_RED)
            elif shake==4:
                vdp_set_bdcolor(VDP_BLACK)
            shake=shake-1
    
    time.sleep_us(16666-time.ticks_diff(time.ticks_us(), delta))
