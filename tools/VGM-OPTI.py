import struct
import sys

# OLD VGM
filename = input("Input filename: ")
file = open(filename, 'rb')

header = file.read(0x100)

gd3_offset = struct.unpack_from("<I", header, 0x14)[0]
loop_offset = struct.unpack_from("<I", header, 0x1C)[0]
vmg_data_offset = struct.unpack_from("<I", header, 0x34)[0]

file.seek(vmg_data_offset + 0x34)

data = bytearray(file.read(gd3_offset-vmg_data_offset))

new_data = bytearray(header)

i = 0
saved = 0

try:
    while i < len(data):
        # AY-3-8910 COMMAND
        if data[i] == 0xa0:
            new_data.extend(data[i].to_bytes(1, byteorder='big') + data[i + 1].to_bytes(1, byteorder='big') + data[i + 2].to_bytes(1, byteorder='big'))
                            
            i += 3
        # DAC STREAM CONTROL WRITE: STOP STREAM
        elif data[i] == 0x94:
            i += 2
        
        # WAIT N
        elif data[i] == 0x61:
            new_data.extend(bytes(b"a") + data[i + 1].to_bytes(1, byteorder='big') + data[i + 2].to_bytes(1, byteorder='big'))
            
            i += 3
        
        # WAIT 1/60
        elif data[i] == 0x62:
            new_data.extend(bytes(b"b"))
            
            i += 1
        
        # EOF
        elif data[i] == 0x66:
            new_data.extend(bytes(b"f"))
            
            break
        
        # SCC1 COMMAND
        elif data[i] == 0xd2:
            # WAVEFORM
            if data[i + 1] == 0x00:
                new_data.extend(bytes(b"\xD2") + data[i + 2].to_bytes(1, byteorder='big') + data[i + 3].to_bytes(1, byteorder='big'))
            # FREQUENCY
            elif data[i + 1] == 0x01:
                new_data.extend(bytes(b"\xD2") + int(data[i + 2] + 0xA0).to_bytes(1, byteorder='big') + data[i + 3].to_bytes(1, byteorder='big'))
            # VOLUME
            elif data[i + 1] == 0x02:
                new_data.extend(bytes(b"\xD2") + int(data[i + 2] + 0xAA).to_bytes(1, byteorder='big') + data[i + 3].to_bytes(1, byteorder='big'))
            # KEY ON/OFF
            elif data[i + 1] == 0x03:
                new_data.extend(bytes(b"\xD2") + bytes(b"\xAF") + data[i + 3].to_bytes(1, byteorder='big'))
                
            i += 4
            if i < ((loop_offset + 0x1C) - (vmg_data_offset + 0x34)):
                saved += 1
        else:
            print(data[i])
            sys.exit()
        
except IndexError as e:
    print(e)
    print(i, len(data))
    
    sys.exit()
            
file.close()

# NEW VGM
# NO GD3 OFFSET
new_data[0x14:0x18] = struct.pack('<I', 0)
# NEW LOOP OFFSET
new_data[0x1C:0x20] = struct.pack('<I', loop_offset - (vmg_data_offset + 0x34 - 0x100) - saved)
# NO EXTRA HEADER OFFSET
new_data[0xBC:0xC0] = struct.pack('<I', 0)

file = open(filename.split(".")[0] + "-opti.vgm", 'xb')

file.write(new_data)

file.close()
