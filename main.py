# vars
opt = 0
offset = 0

# file manager
import os
listdir = [i for i in os.ilistdir()]

vdp_init(VDP_MODE_TEXT, VDP_BLACK, True, False)

vdp_print(os.getcwd(), 0, 0)
vdp_print(f"{opt+offset+1:03d}/{len(listdir):03d}", 33, 0)
vdp_print(">", 0, 1+opt)

for i in range(min(len(listdir), 23)):
    vdp_print(f"{listdir[offset+i][1] == 0x4000 and '/' or ''}{listdir[offset+i][0]:38s}", 2, i+1)

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
                    
                    for i in range(min(len(listdir), 23)):
                        vdp_print(f"{listdir[offset+i][1] == 0x4000 and '/' or ''}{listdir[offset+i][0]:38s}", 2, i+1)
                else:
                    opt = (opt-1)%min(len(listdir), 23)
            elif btnp0 == 5: # DOWN
                vdp_print(" ", 0, opt+1)
                
                if opt==22:
                    if offset==len(listdir)-23: opt = (opt+1)%23
                    offset = (offset+1)%(len(listdir)-22)
                    
                    for i in range(min(len(listdir), 23)):
                        vdp_print(f"{listdir[offset+i][1] == 0x4000 and '/' or ''}{listdir[offset+i][0]:38s}", 2, i+1)
                else:
                    opt = (opt+1)%min(len(listdir), 23)
            elif btnp0 == 0: # 1
                try:
                    vdp_cls()
                    
                    if listdir[opt+offset][1] == 0x8000:
                        # Execute the python file (.py)
                        with open(f"{os.getcwd()}/{listdir[opt+offset][0]}", "r") as f:
                            exec(f.read())
                        
                        vdp_init(VDP_MODE_TEXT, VDP_BLACK, True, False)
                    elif listdir[opt+offset][1] == 0x4000:
                        os.chdir(listdir[opt+offset][0])
                        listdir = [i for i in os.ilistdir(os.getcwd())]
                        
                        opt = 0
                        offset = 0
                    
                    vdp_print(os.getcwd(), 0, 0)
                    for i in range(min(len(listdir), 23)):
                        vdp_print(f"{listdir[offset+i][1] == 0x4000 and '/' or ''}{listdir[offset+i][0]:38s}", 2, i+1)
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
                    vdp_print(os.getcwd(), 0, 0)
                    for i in range(min(len(listdir), 23)):
                        vdp_print(f"{listdir[offset+i][1] == 0x4000 and '/' or ''}{listdir[offset+i][0]:38s}", 2, i+1)
            elif btnp0 == 1: # 0
                os.chdir('..')
                listdir = [i for i in os.ilistdir(os.getcwd())]
                
                opt = 0
                offset = 0
                
                vdp_cls()
                vdp_print(os.getcwd(), 0, 0)
                for i in range(min(len(listdir), 23)):
                    vdp_print(f"{listdir[offset+i][1] == 0x4000 and '/' or ''}{listdir[offset+i][0]:38s}", 2, i+1)
            
            vdp_print(f"{opt+offset+1:03d}/{len(listdir):03d}", 33, 0)
            vdp_print(">", 0, 1+opt)
        
        time.sleep_us(16666-time.ticks_diff(time.ticks_us(), delta))
except BaseException as err:
    from sys import print_exception
    print_exception(err)
    
    music.reset()
    
    vdp_init(VDP_MODE_TEXT, VDP_BLACK, True, False)
    
    vdp_text_wrap(f"{err.__class__.__name__}: {err}", 0, 0, VDP_WHITE, 40, 24, VDP_DARK_RED)
