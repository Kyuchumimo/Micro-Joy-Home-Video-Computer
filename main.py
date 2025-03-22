# vars
opt = 0
offset = 0

# file manager
import os
listdir = [i for i in os.ilistdir()]

vdp_init(VDP_MODE_TEXT, VDP_BLACK, True, False)

def _DRAW_DIR():
    if len(os.getcwd()) > 32:
        if len(os.getcwd().split('/')[-1]) > 28:
            vdp_print(f".../{os.getcwd().split('/')[-1][:25]}...", 0, 0) 
        else:
            vdp_print(f"{os.getcwd()[:28-len(os.getcwd().split('/')[-1])]}.../{os.getcwd().split('/')[-1]}", 0, 0) 
    else:
        vdp_print(os.getcwd(), 0, 0)

def _DRAW_FS():
    for i in range(min(len(listdir), 23)):
        if listdir[offset+i][1] == 0x8000:  # FILE
            if len(listdir[offset+i][0]) > 28:
                vdp_print(f"{listdir[offset+i][0][:25]}...", 2, i+1)
            else:
                vdp_print(f"{listdir[offset+i][0]:28s}", 2, i+1)
            vdp_print(f"{listdir[offset+i][3]:>8d}B", 31, i+1)  # FILE SIZE
        elif listdir[offset+i][1] == 0x4000:  # FOLDER
            if len(listdir[offset+i][0]) > 27:
                vdp_print(f"/{listdir[offset+i][0][:24]}...          ", 2, i+1)
            else:
                vdp_print(f"/{listdir[offset+i][0]:37s}", 2, i+1)

_DRAW_DIR()
_DRAW_FS()

vdp_print(f"{opt+offset+1:03d}/{len(listdir):03d}", 33, 0)
vdp_print(">", 0, 1+opt)

try:
    while True:
        # UPDATE
        delta = time.ticks_us()
        
        # INPUT READING
        btnp0, btnp1 = read_input()
        
        # MENU
        # INPUT/LOGIC
        # BUTTONMAP: A, B, SELECT, START, UP, DOWN, LEFT, RIGHT
        if btnp0 in range(8):
            if btnp0 == 4: # UP
                vdp_print(" ", 0, opt+1)
                
                if opt == 0:
                    if offset==0: opt = (opt-1)%min(len(listdir), 23)
                    offset = (offset-1)%max(len(listdir)-22, 1)
                    
                    _DRAW_FS()
                else:
                    opt = (opt-1)%min(len(listdir), 23)
            elif btnp0 == 5: # DOWN
                vdp_print(" ", 0, opt+1)
                
                if opt==22:
                    if offset==len(listdir)-23: opt = (opt+1)%23
                    offset = (offset+1)%(len(listdir)-22)
                    
                    _DRAW_FS()
                else:
                    opt = (opt+1)%min(len(listdir), 23)
            elif btnp0 == 0: # 1
                try:
                    vdp_cls()
                    
                    if listdir[opt+offset][1] == 0x8000:
                        # Execute the python file (.py)
                        with open(f"{os.getcwd()}/{listdir[opt+offset][0]}", "r") as f:
                            exec(f.read())
                        
                        machine.reset()
                    elif listdir[opt+offset][1] == 0x4000:
                        os.chdir(listdir[opt+offset][0])
                        listdir = [i for i in os.ilistdir(os.getcwd())]
                        
                        opt = 0
                        offset = 0
                    
                    _DRAW_DIR()
                    _DRAW_FS()
                except BaseException as err:
                    from sys import print_exception
                    print_exception(err)
                    
                    music.reset()
                    
                    vdp_init(VDP_MODE_TEXT, VDP_BLACK, True, False)
                    
                    vdp_text_wrap(f"{err.__class__.__name__}: {err}", 0, 0, VDP_WHITE, 40, 24, VDP_DARK_RED)
                    
                    btnp0, btnp1 = read_input()
                    
                    while not btnp0 == 0:
                        btnp0, btnp1 = read_input()

                    vdp_textcolor(VDP_WHITE, VDP_BLACK)
                    vdp_cls()
                    
                    _DRAW_DIR()
                    _DRAW_FS()
            elif btnp0 == 1: # 0
                os.chdir('..')
                listdir = [i for i in os.ilistdir(os.getcwd())]
                
                opt = 0
                offset = 0
                
                vdp_cls()
                
                _DRAW_DIR()
                _DRAW_FS()
            
            vdp_print(f"{opt+offset+1:03d}/{len(listdir):03d}", 33, 0)
            vdp_print(">", 0, 1+opt)
        
        time.sleep_us(16666-time.ticks_diff(time.ticks_us(), delta))
except BaseException as err:
    from sys import print_exception
    print_exception(err)
    
    music.reset()
    
    vdp_init(VDP_MODE_TEXT, VDP_BLACK, True, False)
    
    vdp_text_wrap(f"{err.__class__.__name__}: {err}", 0, 0, VDP_WHITE, 40, 24, VDP_DARK_RED)
