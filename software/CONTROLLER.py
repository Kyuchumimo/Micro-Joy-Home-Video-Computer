color_table_data = bytearray(b'\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1\xf1')
sprite_pattern_table_data = bytearray(b'\x18<~\xff\x18\x18\x18\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x18\x18\x18\xff~<\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x100p\xff\xffp0\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x0c\x0e\xff\xff\x0e\x0c\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x008DDDDD8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x100\x10\x10\x10\x108\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00;FFFGF:\x00\x00\x00\x00\x00\x00\x00\x00\x00\xdf$$$\xc4\x04\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x7f\x12\x12\x12\x13\x12~\x00\x00\x00\x00\x00\x00\x00\x00\x00\xce111\xd52-')

#####################################
vdp_init(VDP_MODE_G1, VDP_WHITE, True, False)

# Initialize color table
set_write_address(COLOR_TABLE)
for b in color_table_data:
    write_byte_to_VRAM(b)

# Initialize sprite patterns
set_write_address(SPRITE_PATTERNS)
for b in sprite_pattern_table_data:
    write_byte_to_VRAM(b)

for i in range(16):
    vdp_sprite_init(i%8, i, VDP_WHITE)

#####################################

running = True
state = 0

vdp_print("CONTROLLER SW TEST", 7, 0)
vdp_print("CONTROLLER 0", 10, 5)
vdp_print("CONTROLLER 1", 10, 13)
vdp_print("PRESS 0 AND 1 TOGETHER TO EXIT", 1, 23)

while running:
    # UPDATE
    delta = time.ticks_us()
    
    # INPUT READING
    # BUTTONMAP: A, B, SELECT, START, UP, DOWN, LEFT, RIGHT
    btnp0, btnp1 = read_input()
    
    if btn0[0] and btn0[1]:
        running = False
    
    if btnp0 is not None:
        state |= 1 << btnp0
    elif btnp1 is not None:
        state |= 1 << 8+btnp1
    
    vdp_sprite_set_position(5, 154, btn0[0] and 72 or 192)  # 1
    vdp_sprite_set_position(4, 130, btn0[1] and 72 or 192)  # 0
    vdp_sprite_set_position(6, 126, btn0[2] and 56 or 192)  # OPT
    vdp_sprite_set_position(7, 149, btn0[3] and 56 or 192)  # IRQ
    
    vdp_sprite_set_position(0, 98, btn0[4] and 64 or 192)  # UP
    vdp_sprite_set_position(1, 98, btn0[5] and 80 or 192)  # DOWN
    vdp_sprite_set_position(2, 90, btn0[6] and 72 or 192)  # LEFT
    vdp_sprite_set_position(3, 106, btn0[7] and 72 or 192)  # RIGHT
    
    
    vdp_sprite_set_position(13, 154, btn1[0] and 136 or 192)  # 1
    vdp_sprite_set_position(12, 130, btn1[1] and 136 or 192)  # 0
    vdp_sprite_set_position(14, 126, btn1[2] and 120 or 192)  # OPT
    vdp_sprite_set_position(15, 149, btn1[3] and 120 or 192)  # IRQ
    
    vdp_sprite_set_position(8, 98, btn1[4] and 128 or 192)  # UP
    vdp_sprite_set_position(9, 98, btn1[5] and 144 or 192)  # DOWN
    vdp_sprite_set_position(10, 90, btn1[6] and 136 or 192)  # LEFT
    vdp_sprite_set_position(11, 106, btn1[7] and 136 or 192)  # RIGHT
    
    vdp_print(f"{state:05d}", 0, 0)
    
    time.sleep_us(16666-time.ticks_diff(time.ticks_us(), delta))
