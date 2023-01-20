import unicodecsv as csv
import re


file_prefixes = [
    "op00",
    "sc1a", "sc1b", "sc1c", "sc1d",
    "sc2a", "sc2b", "sc2c", "sc2d", "sc2e", "sc2f",
    "ss4a", "ss5a", "ss6a", "ss7a", "ssbd", "ssep",
    "sy4a", "sy4b", "sy5a", "sy6a", "sy6b", "sy7a", "sybd", "syep",
    "s_1a", "s_1a2", "s_1b", "s_1c",
    "s_2a", "s_2b", "s_2c", "s_2d",
    "s_3a", "s_3b", "s_3c", "s_3d", "s_3e",
    
    "tc1a", "tc1d", "tc2a",
    "tl6a", "tl7a", "tt6a", "tt7a",
    "t_1a", "t_1b", "t_1c",
    "t_2a", "t_2b", "t_2c", "t_2d",
    "t_3a", "t_3b", "t_3c", 
    "t_4a", "t_4b", "t_4c", 
    "t_5a", "t_5b", "t_5c", "t_5d",
    "t_6a", "t_6b", 
    "t_bd", "t_ep",
    
    "yc3a", "yc3a2", "yc3b",
    "yc4a", "yc4b", "yc5a", "yc5b", 
    "yc6a", "yc6b", "yc7a", "yc7b",
    "ycep", "y_ed", 
    ]

count = 0
all_lines = []

for file_prefix in file_prefixes:
    with open('duplicate_check/{}.tsv'.format(file_prefix),'rb') as f:
        section = 0
        line = ""
        eng_final = ""
        jp_final = ""
        for ln in f:
            line += ln.decode('utf8')
            
            line = re.sub("\r\n", "\n", line)
            line = re.sub("\n$", "", line)
            
            cells = line.split("\t")
            if len(cells) != 5:
                continue
                
            
            eng = cells[3]
            jp = cells[4]
            line = ""
            
            x = re.search("^([0-9]*) :", jp)
            try:
                ## New section, new number
                section = int(x.group(1))
                continue
                
            except:
                pass
            
            ## Skip voice tags
            x = re.search("^\{(.*?)}$", jp)
            if x is not None:
                continue
            
            ## Skip name fields
            x = re.search("^【(.*?)】$", jp)
            if x is not None:
                continue
            
            ## Ignore solitary punctuation
            x = re.search("^([…]{1,})$", jp)
            if x is not None:
                continue
            
            
            if (eng != ""):
                if (eng_final != ""):
                    eng_final += " "
                    
                eng_final += eng
            jp_final += jp
            
            if (jp != "" or eng != ""):
                continue
            
            
            
            """
            ## Skip images
            x = re.search("^([a-zA-Z_0-9]*)$", jp)
            if x is not None:
                continue
            """
            
            
            
            if (jp_final == ""):
                continue
            
            vec = [file_prefix, section, eng_final, jp_final, ""]
            all_lines.append(vec)
            
            eng_final = ""
            jp_final = ""
            #print(vec)

    count += 1
    if count >= 100:
        break

print("--Assembled lines")
prev_found = []
final = []

line_count = len(all_lines)
for curr_idx in range(line_count):
    curr_line = all_lines[curr_idx]
    if (curr_line[3] in prev_found):
        continue
    
    ## Make sure the line meets our length requirement
    if (len(curr_line[3]) < 10):
        continue
    
    for next_idx in range(curr_idx+1, line_count):
        next_line = all_lines[next_idx]
        if curr_line[3] == next_line[3]:
            ## JP matches, add this to the list if it's a reasonably long enough line
            if (len(curr_line[2]) < 10):
                continue
            
            final.append([curr_line[0], curr_line[1], next_line[0], next_line[1], curr_line[3], curr_line[2], next_line[2]])
            prev_found.append(curr_line[3])
    
    if curr_idx%100 == 0:
        print("{}/{} done".format(curr_idx, line_count))
    
    #if curr_idx > 500:
    #    break

final = sorted(final, key=lambda elem: (elem[0], elem[2]))
first  = final[0][0]
second = final[0][2]
for f in final:
    if (f[0] != first or f[2] != second):
        print("")
        first = f[0]
        second = f[2]
        
    msg = "{} {:03} -- {} {:03} - {} - {} - {}".format(f[0], f[1], f[2], f[3], f[4], f[5], f[6])
    if (f[5] != f[6]):
        msg = "===" + msg

    print(msg)