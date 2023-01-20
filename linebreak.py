import re
import sys

"""
## TODO
* Reset on forced linebreak {1}
* Centering for {16:0} and {16:1}
"""

"""
Potential problems (choices):
op00 48
sc1a 36
sc1b 2
sy5a 27
sy6b 8
s_1a 21
"""

file_prefix = "ss5a"

with open('text/in/in_{}.txt'.format(file_prefix), 'r') as f:
    s = f.read()

########################
def get_line_length(line, limit=None):
    ## Ignore any {} tags in length calculation
    ## Returns:
    ##   int: text length
    ##   str: substring up till the last space (including any {} tags)
    ##   str: remainder of the line
    
    is_text = True
    count = 0
    offset = -1
    subs = ""
    
    for c in line:
        offset += 1
        subs += c
        
        if is_text:
            if c == "{":
                is_text = False
            
            elif c == "\x01":
                break
                
            else:
                count += 1
        
        elif not is_text and c == "}":
            ## End of tag
            is_text = True
        
        if limit is not None and count >= limit:
            break
    
    rem = line[offset:]
    
    return count, subs, rem
        

## Merge all lines within a single entry
s = re.sub("\r\n", "\n", s)
s = re.sub("([^:\n\}\]]) \n([^\r\n])", "\\1 \\2", s)
s = re.sub("([^:\n\}\]])\n([^\r\n])", "\\1 \\2", s)

## Add quotes to single dialogue
s = re.sub('\]\n([^"].*?)\n', ']{1}"\\1"\n', s)

## Merge lines that already have quotes into the name tag
s = re.sub('\]\n"(.*?)\n', ']{1}"\\1\n', s)

## Center any text between {16:0}{16:1}
def center_text_breakup(m):
    ## Remove tags
    length = len(m.group(1))
    spaces_to_add = int((48-length)/2)
    return ' '*spaces_to_add + "\n\n" + m.group(1) + "\n\n"

def center_text_breakup_newline(m):
    ## Remove tags
    length = len(m.group(1))
    spaces_to_add = int((48-length)/2)
    return ' '*spaces_to_add + "\n\n" + m.group(1) + "\x01\n\n"

def center_text(m):
    ## Remove tags
    length = len(m.group(1))
    spaces_to_add = int((48-length)/2)
    return ' '*spaces_to_add + m.group(1) + "\n\n"

def center_text_newline(m):
    ## Remove tags
    length = len(m.group(1))
    spaces_to_add = int((48-length)/2)
    return ' '*spaces_to_add + m.group(1) + "\x01\n\n"

s = re.sub('\{16:0x}(.*?)\{16:1}', center_text_breakup, s)
s = re.sub('\{16:0x}(.*?)\{1}', center_text_breakup_newline, s)
s = re.sub('\{16:0}(.*?)\{16:1}', center_text, s)
s = re.sub('\{16:0}(.*?)\{1}', center_text_newline, s)
s = re.sub('(.*?)\{16:1}', center_text, s)

## Combine choices into a single line
s = re.sub('({11:1})\n', "\\1", s)

## Replace all newlines with hex code
s = re.sub('\{1}', '\x01', s)

########################
lines = s.split("\n")
final = []

for line_idx in range(len(lines)):
    line = lines[line_idx]
    processed_line = []
    
    is_multiline = False
    
    while True:
        count, subs, rem = get_line_length(line, limit=49)
        
        if count < 49:
            ## Add the length in its entirety, unless it is the last line
            if (line_idx+1 <= len(lines) or lines[line_idx+1] == "\n"):
                ## This is the last line in this entry. Make sure it's 46 char max
                count, subs, rem = get_line_length(line, limit=47)
                
                if count < 47:
                    ## Add the length in its entirety
                    processed_line.append(line)
                else:
                    ## Find the first space before the overflow
                    k = subs.rfind(" ")
                    left = line[:k]
                    right = line[k+1:]
                    
                    processed_line.append(left)
                    processed_line.append(right)
                
            else:
                ## There's more lines after this. Just 48 chars is enough
                processed_line.append(line)        
            
            break
        
        ## Find the first space before the overflow
        is_multiline = True
        k = subs.rfind(" ")
        left = line[:k]
        right = line[k+1:]
        
        processed_line.append(left)
        line = right
        
    final.append( "\x01".join(processed_line) )



final = "\n".join(final)

## Go back to text friendly versions
s = re.sub('\x01', '{1}', s)

## Save result
with open('text/out/out_{}.txt'.format(file_prefix), 'wb') as f:
    f.write(final.encode("ansi"))

print(final)