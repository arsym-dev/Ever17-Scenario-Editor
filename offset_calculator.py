import re
import sys
import struct

inputs=["sy4b 21"]

offsets = {
    "op00": -1,
    "sc1a": 213,
    "sc1b": 303,
    "sc1c": 453,
    "sc1d": 471,
    "sc2a": 528,
    "sc2b": 609,
    "sc2c": 721,
    "sc2d": 742,
    "sc2e": 764,
    "sc2f": 819,
    "ss4a": 877,
    "ss5a": 1025,
    "ss6a": 1258,
    "ss7a": 1355,
    "ssbd": 1382,
    "ssep": 1398,
    "sy4a": 1434,
    "sy4b": 1643,
    "sy5a": 1756,
    "sy6a": 1889,
    "sy6b": 2024,
    "sy7a": 2197,
    "sybd": 2280,
    "syep": 2312,
    "s_1a": 2332,
    "s_1a2": 2497,
    "s_1b": 2659,
    "s_1c": 3000,
    "s_2a": 3249,
    "s_2b": 3492,
    "s_2c": 3757,
    "s_2d": 3932,
    "s_3a": 4243,
    "s_3b": 4447,
    "s_3c": 4616,
    "s_3d": 4783,
    "s_3e": 4854,
    "tc1a": 4966,
    "tc1d": 5031,
    "tc2a": 5078,
    "tl6a": 5147,
    "tl7a": 5368,
    "tt6a": 5433,
    "tt7a": 5701,
    "t_1a": 5783,
    "t_1b": 5843,
    "t_1c": 6067,
    "t_2a": 6310,
    "t_2b": 6500,
    "t_2c": 6667,
    "t_2d": 6829,
    "t_3a": 7041,
    "t_3b": 7253,
    "t_3c": 7395,
    "t_4a": 7487,
    "t_4b": 7583,
    "t_4c": 7880,
    "t_5a": 8104,
    "t_5b": 8200,
    "t_5c": 8324,
    "t_5d": 8524,
    "t_6a": 8605,
    "t_6b": 8812,
    "t_bd": 9026,
    "t_ep": 9073,
    "yc3a": 9077,
    "yc3a2": 9281,
    "yc3b": 9393,
    "yc4a": 9517,
    "yc4b": 9651,
    "yc5a": 9749,
    "yc5b": 9870,
    "yc6a": 10028,
    "yc6b": 10248,
    "yc7a": 10381,
    "yc7b": 10514,
    "ycep": 10608,
    "y_ed": 10753
    }

"""
inputs = [
#"t_1b 101",
"s_1b 87",
"sc1a   6 -> sc2e 26-31",
"sc1b   8 -> sc2e 34-43",
"sc1d   2 -> sc2e 45-46",
"sc1d  21 -> sc2e 47-48",
"sc2b  72 -> sc2e 49-52",
"sc2d   1 -> tc2a 1-24",
"sc2d   9 -> yc3a 31-41",
"ss4a  12 -> yc4a 5",
"ss4a 113 -> sy4b 73-79",
"ss5a  92 -> sy5a 41-89 / sy5a 38",
"ss5a 172 -> t_5b 35",
"ss5a 180 -> sy5a 97-102",
"ss6a  63 -> yc6b 116-127",
"sy4a  26 -> sybd 28-29",
"sy4b  73 -> ss4a 113-120",
"sy5a  38 -> ss5a 92-176",
"sy5a  97 -> ss5a 180-184",
"sy6a  23 -> t_6a 11-18",
"sy6a  26 -> t_6a 24-30",
"sy6a  29 -> t_6a 133-144",
"sy6a  60 -> t_6a 161-165",
"sy6b  97 -> yc4b 41",
"sy7a   1 -> sybd 1",
"sybd   1 -> sy7a 1",
"s_1a2  25 -> tc1a 16-19",
"s_1a2 103 -> sc1a 60-63",
"s_1b  48 -> t_1b 55-59 / t_1c 194",
"s_1b  87 -> t_1b 101-104",
"s_1b 333 -> sc1b 4-7",
"s_1b 341 -> sc1b 48",
"s_1c   1  -> sc1b 49",
"s_1c  32 -> t_1c 117-119 / ssep 5-6",
"s_1c  47 -> sc1b 149-150",
"s_1c  78 -> t_1c 31-32",
"s_1c  86 -> yc4b 81-83",
"s_1c 171 -> t_1c 47-48",
"s_1c 187 -> sc1d 1-20",
"s_1c 208 -> sc1d 44-48 / sc1d 53-57",
"s_1c 229 -> tc1d 10-14",
"s_1c 236 -> t_1c 226-227",
"s_2a  86 -> t_2a 45-51",
"s_2a 103 -> t_2a 52-60",
"s_2a 167 -> t_2a 89-90 / t_2a 115-116",
"s_2a 178 -> sc2a 1-7",
"s_2a 185 -> sc2a 13-81",
"s_2a 232 -> t_2a 162-164",
"s_2b   2 -> t_2b 1-4",
"s_2b  83 -> sc2b 1-23",
"s_2b 110 -> sc2b 24-50 / sc2b 55",
"s_2b 136 -> sc2b 110-112",
"s_2b 189 -> s_3b 64-76",
"s_2b 156 -> s_3b 46",
"s_2b 211 -> t_2b 128-139",
"s_2b 231 -> t_2b 142-152",
"s_2c  19 -> t_2c 34-46",
"s_2c  37 -> t_2c 50-71",
"s_2c  68 -> t_2c 73-74",
"s_2c  75 -> t_2c 83-93",
"s_2c 100 -> sc2c 2-11",
"s_2c 120 -> t_2c 106",
"s_2c 132 -> t_2c 118-133",
"s_2c 166 -> sc2c 12-16 / t_2c 148-159",
"s_2c 172 -> sc2d 1",
"s_2c 175 -> sc2d 4",
"s_2d   1 -> t_2d 1-10",
"s_2d  55 -> t_2d 45-60",
"s_2d 163 -> t_2d 76-110 / sc2e 2-6",
"s_2d 302 -> sc2e 14-21",
"s_2d 311 -> t_2d 212",
"s_3a 132 -> t_3a 45-49",
"s_3a 158 -> t_3a 71-82",
"s_3b  13 -> yc3a2 24-34",
"s_3b  35 -> yc3a2 36-42",
"s_3b  46 -> s_2b 156-157",
"s_3b  57 -> s_3b 79-80",
"s_3b  64 -> s_2b 189-209",
"s_3b  79 -> s_3b 57-59",
"s_3b 134 -> yc3a2 46-54",
"s_3b 153 -> yc3a2 55-65",
"s_3c   6 -> t_3a 96-100",
"s_3c  18 -> t_3a 104-124",
"s_3c  46 -> t_3a 126-132",
"s_3c  58 -> t_3a 133-136",
"tc1a 27 -> yc3a 23-29",
"tc2a   1 -> sc2d 1-22",
"tc2a  11 -> yc3a 31-41",
"tc2a  33 -> yc3a 48-65",
"tc2a  58 -> yc3a 66-68",
"tl6a   1 -> tt6a  1-3",
"tl6a   5 -> tt6a  8-11",
"tl6a  10 -> yc6a 133-139",
"tl6a  30 -> tt6a 34-38",
"tl6a  77 -> tt6a 40-82 / yc6a 166",
"tl6a  93 -> yc6a 169-177 / tt6a 83-99",
"tl6a 100 -> tt6a 183",
"tl6a 105 -> yc6b 4-21 / tt6a 186-196",
"tl6a 122 -> tt6a 198-214",
"tl6a 181 -> tt6a 215",
"tl7a  19 -> tt7a 1-2",
"tt6a   1 -> tl6a  1-2",
"tt6a   8 -> tl6a  5-10",
"tt6a  36 -> yc6a 148-155 / tl6a 30-34",
"tt6a  48 -> tl6a 36-77 / yc6a 162",
"tt6a  83 -> tl6a 81-99",
"tt6a 152 -> yc6a 200-220",
"tt6a 183 -> tl6a 100",
"tt6a 186 -> tl6a 103-113",
"tt6a 198 -> yc6b 20-35 / tl6a 122-138",
"tt6a 215 -> tl6a 181-182",
"tt6a 222 -> yc6b 41-58",
"tt6a 246 -> yc6b 82-107",
"tt6a 257 -> yc7a 107",
"tt7a   1 -> tl7a 19-20",
"tt7a  26 -> yc7a 2-9",
"tt7a  33 -> yc7a 13-26",
"tt7a  44 -> yc7a 31-35",
"tt7a  54 -> yc7a 40-64", #78
"t_1b  16 -> tc1a 1-2",
"t_1b  20 -> tc1a 55-65",
"t_1b  55 -> s_1b 41-68",
"t_1b 101 -> s_1b 87-90",
"t_1c  31 -> s_1c 78-89",
"t_1c  47 -> s_1c 171-180",
"t_1c  75 -> yc3a 43-46",
"t_1c 117 -> s_1c 25-32",
"t_1c 194 -> s_1b 48-49",
"t_1c 215 -> tc1d 1",
"t_1c 217 -> tc1d 5",
"t_1c 219 -> tc1d 16-20",
"t_1c 226 -> tc1d 24-35 / s_1c 236-245",
"t_1c 235 -> tc1d 37-44",
"t_1c 242 -> tc1d 45",
"t_2a  45 -> s_2a 86-100",
"t_2a  52 -> s_2a 103-113",
"t_2a  89 -> s_2a 167-169 / t_2a 115-116",
"t_2a 115 -> s_2a 167-169 / t_2a 89-90",
"t_2a 162 -> s_2a 232-239",
"t_2b   1 -> s_2b   2-4",
"t_2b 128 -> s_2b 211-229",
"t_2b 142 -> s_2b 231-251",
"t_2c  34 -> s_2c 19-33",
"t_2c  50 -> s_2c 37-67",
"t_2c  73 -> s_2c 68-70",
"t_2c  83 -> s_2c 75-95",
"t_2c 106 -> s_2c 120",
"t_2c 118 -> s_2c 132-155",
"t_2c 148 -> s_2c 156-174",
"t_2c 161 -> tc2a 5-6",
"t_2d   1 -> s_2d 1-11",
"t_2d  45 -> s_2d 55-83",
"t_2d  76 -> s_2d 127-168",
"t_2d 212 -> s_2d 311",
"t_3a  15 -> yc3a 3-19",
"t_3a  45 -> s_3a 132-136",
"t_3a  77 -> s_3a 158-186 / yc3a 76-81",
"t_3a  96 -> s_3c 6-9",
"t_3a 115 -> s_3c 18-42 / yc3a 84-99",
"t_3a 126 -> s_3c 46-55",
"t_3a 133 -> s_3c 58-60",
"t_3a 143 -> yc3a 100-112",
"t_3a 179 -> yc3a 119-137",
"t_3a 192 -> yc3a 138-153",
"t_3b  98 -> yc3b 56-57",
"t_3b 111 -> yc3b 58-63",
"t_3b 133 -> yc3b 66-71",
"t_4c   1 -> t_4c 20-26",
"t_4c   8 -> t_4c 28-38",
"t_4c  20 -> t_4c 1-6",
"t_4c  28 -> t_4c 8-15",
"t_4c 142 -> yc4b 58-60",
"t_5a 58 -> yc5a 111",
"t_5a 66 -> yc5a 93-93",
"t_5b  35 -> ss5a 172",
"t_5c  94 -> t_5d 2-5",
"t_5c 198 -> t_5d 79-82",
"t_5d   2 -> t_5c  94-99",
"t_5d  79 -> t_5c 198-200",
"t_6a  11 -> sy6a 23-25",
"t_6a  24 -> sy6a 26-27",
"t_6a 133 -> sy6a 29-37",
"t_6a 161 -> sy6a 60-65",
"t_6a 200 -> yc6a 19",
"t_6b  13 -> yc6a 22-26",
"t_6b  52 -> yc6a 27-30",
"t_6b 135 -> yc6a 43-65",
"t_6b 175 -> yc6a 70-94",
"t_6b 189 -> yc6a 097-100",
"t_6b 194 -> yc6a 104-130",
"yc3a2 106 -> yc4a 7-9",
"yc4a   7 -> yc3a2 106-108",
    ]
#"""

## TODO: Generate assembly code
## If it only detects one target clock, CALL EBP
## Otherwise CALL ESI
##
## If there are multiple target files in the same line, make them share the same compare/jump code

final_code = b""

for input in inputs:
    
    ## xx yy -> xx yy-yy / xx yy-yy
    x = re.search("^([0-9a-zA-Z_]*)\s+([0-9]{1,3})\s+->\s+([0-9a-zA-Z_]*)\s+([0-9]{1,3})-([0-9]{1,3})\s+/\s+([0-9a-zA-Z_]*)\s+([0-9]{1,3})-([0-9]{1,3})$", input)
    if x is not None:
        file1 = offsets[x.group(1)]
        file2 = offsets[x.group(3)]
        file3 = offsets[x.group(6)]
        
        start1 = int(x.group(2))
        start2 = int(x.group(4))
        start3 = int(x.group(7))
        
        length2 =  int(x.group(5)) - start2 +1
        length3 =  int(x.group(8)) - start3 +1
        
        start1 += file1
        start2 += file2
        start3 += file3
        
        
        ##### Build the code
        code = b""
        
        ## CMP AX, start1
        code += b"\x66\x3D" + struct.pack('<H', start1)
        
        ## JNZ SHORT (just past this block)
        code += b"\x75\x10"
        
        ## MOV BX, start2
        code += b"\x66\xBB" + struct.pack('<H', start2)
        
        ## MOV CL, length2
        code += b"\xB1" + struct.pack('<B', length2)
        
        ## CALL ESI
        code += b"\xFF\xD6"
        
        ## MOV BX, start3
        code += b"\x66\xBB" + struct.pack('<H', start3)
        
        ## MOV CL, length3
        code += b"\xB1" + struct.pack('<B', length3)
        
        ## CALL ESI
        code += b"\xFF\xD6"
        
        final_code += code
        print("{:04X}   {:04X}({:02X}) / {:04X}({:02X})".format(start1, start2, length2, start3, length3))
        continue
    
    
    ## xx yy -> xx yy-yy / xx yy
    x = re.search("^([0-9a-zA-Z_]*)\s+([0-9]{1,3})\s+->\s+([0-9a-zA-Z_]*)\s+([0-9]{1,3})-([0-9]{1,3})\s+/\s+([0-9a-zA-Z_]*)\s+([0-9]{1,3})$", input)
    if x is not None:
        file1 = offsets[x.group(1)]
        file2 = offsets[x.group(3)]
        file3 = offsets[x.group(6)]
        
        start1 = int(x.group(2))
        start2 = int(x.group(4))
        start3 = int(x.group(7))
        
        length2 =  int(x.group(5)) - start2 +1
        
        start1 += file1
        start2 += file2
        start3 += file3
        
        ##### Build the code
        code = b""
        
        ## CMP AX, start1
        code += b"\x66\x3D" + struct.pack('<H', start1)
        
        ## JNZ SHORT (just past this block)
        code += b"\x75\x0E"
        
        ## MOV BX, start2
        code += b"\x66\xBB" + struct.pack('<H', start2)
        
        ## MOV CL, length2
        code += b"\xB1" + struct.pack('<B', length2)
        
        ## CALL ESI
        code += b"\xFF\xD6"
        
        ## MOV BX, start3
        code += b"\x66\xBB" + struct.pack('<H', start3)
        
        ## CALL EDI
        code += b"\xFF\xD5"
        
        final_code += code
        print("{:04X}   {:04X}({:02X}) / {:04X}".format(start1, start2, length2, start3))
        continue
    
    
    ## xx yy -> xx yy-yy
    x = re.search("^([0-9a-zA-Z_]*)\s+([0-9]{1,3})\s+->\s+([0-9a-zA-Z_]*)\s+([0-9]{1,3})-([0-9]{1,3})$", input)
    if x is not None:
        file1 = offsets[x.group(1)]
        file2 = offsets[x.group(3)]

        start1 = int(x.group(2))
        start2 = int(x.group(4))
        
        length2 =  int(x.group(5)) - start2 +1
        
        start1 += file1
        start2 += file2
        
        
        
        ##### Build the code
        code = b""
        
        ## CMP AX, start1
        code += b"\x66\x3D" + struct.pack('<H', start1)
        
        ## JNZ SHORT (just past this block)
        code += b"\x75\x08"
        
        ## MOV BX, start2
        code += b"\x66\xBB" + struct.pack('<H', start2)
        
        ## MOV CL, length2
        code += b"\xB1" + struct.pack('<B', length2)
        
        ## CALL ESI
        code += b"\xFF\xD6"
        
        final_code += code
        print("{:04X}   {:04X}({:02X})".format(start1, start2, length2))
        continue
        
    ## xx yy -> xx yy
    x = re.search("^([0-9a-zA-Z_]*)\s+([0-9]{1,3})\s+->\s+([0-9a-zA-Z_]*)\s+([0-9]{1,3})$", input)
    if x is not None:
        file1 = offsets[x.group(1)]
        file2 = offsets[x.group(3)]

        start1 = int(x.group(2))
        start2 = int(x.group(4))
        
        start1 += file1
        start2 += file2
        
        
        ##### Build the code
        code = b""
        
        ## CMP AX, start1
        code += b"\x66\x3D" + struct.pack('<H', start1)
        
        ## JNZ SHORT (just past this block)
        code += b"\x75\x06"
        
        ## MOV BX, start2
        code += b"\x66\xBB" + struct.pack('<H', start2)
        
        ## CALL EBP
        code += b"\xFF\xD5"
        
        final_code += code
        print("{:04X}   {:04X}".format(start1, start2))
        continue
    
    ## xx yy
    x = re.search("^([0-9a-zA-Z_]*)\s+([0-9]{1,3})$", input)
    if x is not None:
        file = x.group(1)
        number = int(x.group(2))
        
        print(input)
        print(offsets[file] + number)
        sys.exit()
        
    print("Wrong syntax: {}".format(input))
    
## Final POPS + RETN
final_code += b"\x5D\x5E\x59\x5B\x58\xC3"

with open("compiled_crossroute.txt", 'bw') as f:
    f.write(final_code)