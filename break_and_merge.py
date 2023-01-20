import re
import sys
import glob
import os
import warnings
import struct
warnings.simplefilter('always')

path_output_dat  = "D:/Games/VN/Ever17/PC/script.dat"
dir_scr_original = "D:/Games/VN/Ever17/PC/_extracted/script/"
dir_scr_final    = "D:/Games/VN/Ever17/PC/_extracted/script-final/"
dir_preprocess   = "./text/in"
dir_processed    = "./text/out"

file_prefixes = [
    "op00",
    "sc1a", "sc1b", "sc1c", "sc1d",
    "sc2a", "sc2b", "sc2c", "sc2d", "sc2e", "sc2f",
    "ss4a", "ss5a", "ss6a", "ss7a", "ssbd", "ssep",
    #"startup",
    "sy4a", "sy4b", "sy5a", "sy6a", "sy6b", "sy7a", "sybd", "syep",
    #"system",
    "s_1a", "s_1a2", "s_1b", "s_1c",
    "s_2a", "s_2b", "s_2c", "s_2d",
    "s_3a", "s_3b", "s_3c", "s_3d", "s_3e",
    
    "tc1a", 
    #"tc1b", "tc1c", # Corrupted?
    "tc1d", "tc2a",
    #"tc2b", # Corrupted?
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

all_file_prefixes = [
    "op00",
    "sc1a", "sc1b", "sc1c", "sc1d",
    "sc2a", "sc2b", "sc2c", "sc2d", "sc2e", "sc2f",
    "ss4a", "ss5a", "ss6a", "ss7a", "ssbd", "ssep",
    "startup",
    "sy4a", "sy4b", "sy5a", "sy6a", "sy6b", "sy7a", "sybd", "syep",
    "system",
    "s_1a", "s_1a2", "s_1b", "s_1c",
    "s_2a", "s_2b", "s_2c", "s_2d",
    "s_3a", "s_3b", "s_3c", "s_3d", "s_3e",
    
    "tc1a", 
    "tc1b", "tc1c", # Corrupted?
    "tc1d", "tc2a",
    "tc2b", # Corrupted?
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
    
    rem = line[offset+1:]
    
    return count, subs, rem

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

def preprocess_input(s):
    ## Merge all lines within a single entry
    s = re.sub("\r\n", "\n", s)
    s = re.sub("([^:\n\}\]]) \n([^\r\n])", "\\1 \\2", s)
    s = re.sub("([^:\n\}\]])\n([^\r\n])", "\\1 \\2", s)
    
    ## Add quotes to single dialogue
    s = re.sub('\]\n([^"].*?)\n', ']{1}"\\1"\n', s)
    
    ## Merge lines that already have quotes into the name tag
    s = re.sub('\]\n"(.*?)\n', ']{1}"\\1\n', s)
    
    ## Merge lines that have a forced linebreak
    s = re.sub('\{1}\n([^\n])', '{1}\\1', s)
    
    ## Center text
    s = re.sub('\{16:0x}(.*?)\{1}{16:1}', center_text_newline, s)
    s = re.sub('\{16:0x}(.*?)\{1}', center_text_breakup_newline, s)
    s = re.sub('\{16:0x}(.*?)\{16:1}', center_text_breakup, s)
    s = re.sub('\{16:0}(.*?)\{1}{16:1}', center_text_newline, s)
    s = re.sub('\{16:0}(.*?)\{1}', center_text_newline, s)
    s = re.sub('\{16:0}(.*?)\{16:1}', center_text, s)
    s = re.sub('(.*?)\{16:1}', center_text, s)
    
    ## Combine choices into a single line
    s = re.sub('({11:1})\n', "\\1", s)
    
    ## Replace all newlines with hex code
    s = re.sub('\{1}', '\x01', s)
    
    return s


def process_script(s):
    lines = s.split("\n")
    final = []
    
    for line_idx in range(len(lines)):
        line = lines[line_idx]
        processed_line = []
        
        while True:
            count, subs, rem = get_line_length(line, limit=49)
            
            if count < 49:
                if (len(rem) == 0):
                    ## This is the actual end of the line
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
                
                else:
                    ## This is a forced newline (\x01)
                    if (subs[-1] == "\x01"):
                        subs = subs[:-1]
                    
                    processed_line.append(subs)
                    line = rem
            
            else:
                ## Line longer than 48 chars
                ## Find the first space before the overflow
                k = subs.rfind(" ")
                left = line[:k]
                right = line[k+1:]
                
                processed_line.append(left)
                line = right
        
        if len(processed_line) > 5:
            warnings.warn("Line too long. Overflow detected: " + repr(processed_line), UserWarning, stacklevel=2)
            
        final.append( "\x01".join(processed_line) )
    
    
    
    final = "\n".join(final)
    
    ## Go back to text friendly versions
    s = re.sub('\x01', '{1}', final)
    
    return s














def script_to_sections(script):
    script = re.sub(b'\r\n', b'\n', script) ## Newlines
    script = re.sub(b'\{1}', b'\x01', script) ## Newlines
    script = re.sub(b'\{11:0.*?}', b'\n', script) ## Choice start
    script = re.sub(b'\{11:1}(.*?)\n', b'\\1\x01\n', script) ## Choice
    script = re.sub(b'\{11:2.*?}(.*?)\n', b'\\1\x01\n', script) ## Choice
    script = re.sub(b'\{16:4}\n', b'\n', script) ## Clear screen
    script = re.sub(b'\{(.*?)}', b'\\1\n', script) ## Voice tags
    
    sections = []
    lines = script.split(b"\n")
    accumulator = []
    sec_id = 0
    
    for line in lines:
        x = re.search(b"([0-9]*) :", line)
        try:
            t = x.group(1)
            
            sections.append(accumulator)
            sec_id += 1
            
            ## New section
            accumulator = []
            
        except:
            ## Not a new section. Add to previous
            if line != b"":
                accumulator.append(line)
            
    sections.append(accumulator)
    return sections




class Chunk():
    def __init__(self, filepath, name, chunk_num):
        with open(filepath, 'rb') as f:
            self.raw = f.read()
        
        self.name = name
        self.chunk_num = chunk_num
        self.token = ""
        
        self.pos_curr = 0
        self.pos_max = len(self.raw)
    
    
    def DumpTokens(self):
        ret = ""
        while (self.pos_curr < self.pos_max):
            try:
                token = self.GetChar(offset=0)
                token_length, opcode, token_str = self.CheckToken(token)
                
                ret += token_str
                
            except Exception as e:
                msg = str(e)
                msg += "\n[{}, Chunk {}, Offset {:04X}, Token: {:02X}]".format(self.name, self.chunk_num, self.pos_curr, self.token)
                
                raise Exception(msg) 
                
            self.pos_curr += token_length
        
        return ret
    
    
    def GetChar(self, offset=0):
        return self.raw[self.pos_curr + offset]
    
    
    def GetArgs(self, count):
        args = []
        
        for i in range(count):
            args.append( self.GetChar(offset=i) )
        
        return args
    
    
    def GetArgsStr(self, count):
        ret = ""
        
        for i in range(count):
            ret += " {:02X}".format(self.GetChar(offset=i))
        
        return ret
    
    def CheckToken(self, token):
        ## Returns:
        ##  int: Length of the token
        ##  str: A text version of the token
        
        if (token >= 0x20):
            ## Text. Game ignores it outside of choice / textbox / NVL
            return 1, 0x20, bytes([token]).decode("ansi")
        
        self.token_prev = self.token
        self.token = token
        
        if (self.token == 0x00):
            
            if (self.token_prev == 0x0D):
                ## This is the closing tag for a voice clip
                return 1, token, "}\n"
            
            if (self.pos_curr < self.pos_max-1):
                raise Exception("End of file detected too early.")
            
            ## End of chunk
            return 1, token, "{0-end of chunk}"
            
        elif (self.token == 0x01):
            if (self.token_prev == "0x0b"):
                ## End of choice entry
                return 1, 0x00, "{1-end of choice}\n\n"
            
            ## Newline in text
            return 1, token, "{1}\n"
            
        elif (self.token == 0x02):
            ## Wait for user acknowledgement
            return 1, token, "{2}"
        
        elif (self.token == 0x03):
            ## Clear textbox and save to history
            return 1, token, "{3}\n\n"
            
        elif (self.token == 0x04):
            args = self.GetArgs(5)
            ## Alternate user input (pause, quick transition)
            
            if (args[1] >= 0x80 and args[1] <= 0x8F):
                ## Small pause between letters?
                ## Immediately play next effect then wait for user acknowledgement?

                if (args[2] != 0x00 or args[3] != 0x00):
                    raise UnknownArgumentsException(args)
                
                else:
                    ## Small pause between letters?"
                    return 4, token, "{4:" + "{:02X}".format(args[1]) + "}"
            
            elif (args[1] == 0xA0):
                ## 04 A0 xx 00 00 = How long to pause before continuing in auto mode
                
                if (args[3] != 0x00 or args[4] != 0x00):
                    raise UnknownArgumentsException(args)
                
                ## Pause
                return 5, token, "{4:A0-" + "{:02X}".format(args[2]) + "}"
                
            else:
                raise UnknownArgumentsException(args)
            
        elif (self.token == 0x05):
            ## Start of textbox entry
            args = self.GetArgs(4)
            if (args[1] != 0x80 or args[2] != 0x00 or args[3] != 0x00):
                raise UnknownArgumentsException(args)
            
            return 4, token, "{05}"
        
        elif (self.token == 0x0b):
            ## Choices
            
            args = self.GetArgs(2)
            if (args[1] == 0x00):
                ## Start of choice menu
                args = self.GetArgs(4)
                id = args[3]*0x100 + args[2]
                return 4, token, "{11:0-" + "{:04X}".format(id) + "}\n"
            
            elif (args[1] == 0x01):
                ## Standard choice
                return 2, token, "{11:1}"
            
            elif (args[1] == 0x02):
                args = self.GetArgs(8)
                ## Conditional choice. May or may not appear based on the value of some variable
                if (args[2] == 0x28 and args[3] == 0x0a and args[4] == 0xa4 and args[6] == 0x14  and args[7] == 0x00):
                    if (args[5] >= 0xd0 and args[5] <= 0xd5):
                        return 8, token, "{11:2-" + "{:02X}".format(args[5]) + "}\n"
                    else:
                        raise UnknownArgumentsException(args)
                    
                else:
                    raise UnknownArgumentsException(args)
            
            else:
                raise UnknownArgumentsException(args)
        
        elif (self.token == 0x0c):
            ## Continue immediately without waiting for user acknowledgement
            return 1, token, "{12}"
        
        elif (self.token == 0x0d):
            ## Start of voice clip
            return 1, token, "{"
        
        elif (self.token == 0x0e):
            ## Start of text entry. Not strickly necssary. Seems to denote chunks with executable content rather than just image reference for BG/sprites
            return 1, token, "{14}"
            
            
        elif (self.token == 0x10):
            ## No clue. Clear the NVL screen?
            args = self.GetArgs(2)
            msg = ""
            if (args[1] == 0x00):
                ## Start centered text
                msg = "{16:0}"
            
            elif (args[1] == 0x01):
                ## End centered text
                msg = "{16:1}"
            
            elif (args[1] == 0x04):
                ## Clear text and save to history
               msg = "{16:4}"
                
            else:
                raise UnknownArgumentsException(args)
            
            return 2, token, msg
        
        
        elif (self.token == 0x11):
            ## Change font size
            args = self.GetArgs(2)
            
            if (args[1] == 0x03):
                ## Font size 3: Huge font
                return 2, token, "{17:3-font size}"
            else:
                raise UnknownArgumentsException(args)
            
        else:
            raise Exception("Unknown token")
        

def create_scr_chunks(sections):
    ## Iterate through each "section" as follows:
    ## 1) Open the original SCR file
    ## 2) Copy content from the SCR file until it hits a field the contains text
    ## 3) Copy a line of text from the finalized script
    ## 4) Repeat steps 2 and 3 until all of the finalized script has replaced the original
    ##
    ## Purpose of this is to maintain all the opcodes in the game and only replace the text. Saves me a bit of time.
    
    path = os.path.join(dir_scr_original,file_prefix,file_prefix+".scr_chunk*")
    fname_chunks = glob.glob(path)
    
    dir = "final/{0}".format(file_prefix)
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    limit_count = 0
    for section_idx in range(1, len(sections)):
        path = fname_chunks[section_idx]
        
        scr_original = Chunk(path, file_prefix, path[-3:])
        
        
        ret = b""
        is_text = False
        subsection_idx = 0
        prev_token = 0
        while (scr_original.pos_curr < scr_original.pos_max):
            try:
                token = scr_original.GetChar(offset=0)
                token_length, opcode, token_str = scr_original.CheckToken(token)
                
            except Exception as e:
                msg = str(e)
                msg += "\n[{}, Chunk {}, Offset {:04X}, Token: {:02X}]".format(scr_original.name, scr_original.chunk_num, scr_original.pos_curr, scr_original.token)
                
                raise Exception(msg) 
            
            if ((token == 0x01 and prev_token != 0x02 and prev_token != 0x0C) or token >= 0x20):
                ## Text
                if (not is_text):
                    ## copy new content once and only once
                    is_text = True
                    
                    try:
                        ret += sections[section_idx][subsection_idx]
                    except Exception as e:
                        print(file_prefix, section_idx, subsection_idx)
                        if subsection_idx > 0:
                            print("Previous entry:")
                            print(sections[section_idx][subsection_idx-1])
                            print("Raw message/New message")
                            print(scr_original.raw)
                            print(ret)
                            print(sections[section_idx])
                        raise e
                        
                    subsection_idx += 1
                
            else:
                ## Not text
                is_text = False
                
                ret += scr_original.raw[scr_original.pos_curr:scr_original.pos_curr+token_length]
                
            prev_token = token
            scr_original.pos_curr += token_length
        
        if (subsection_idx != len(sections[section_idx])):
            print("Previous entry:")
            print(sections[section_idx][subsection_idx-1])
            print("Raw message/New message")
            print(scr_original.raw)
            print(ret)
            raise Exception("Number of text entries in script and original file do not match")
        
        #print(file_prefix, section_idx, "ori", scr_original.raw)
        #print(file_prefix, section_idx, "new", ret)
        
        with open("{0}/{1}/{1}.scr_chunk_{2:03}".format(dir_scr_final,file_prefix, section_idx), 'wb') as f:
            f.write(ret)
        
        limit_count += 1
        if (limit_count>500):
            break
        
        #print(scr_original)
        
        
        
        
        
def create_scr_file(file_prefix):
    ## Let's merge all of these into a single SCR file
    path = os.path.join(dir_scr_final, file_prefix, file_prefix+".scr_chunk*")
    fname_chunks = glob.glob(path)
    fname_chunks.sort()
    
    ## Read file contents into an array
    file_contents = [None]*len(fname_chunks)
    for fname_chunk in fname_chunks:
        chunk_num = int(fname_chunk[-3:])
        
        with open(fname_chunk, 'rb') as f:
            s = f.read()
            file_contents[chunk_num] = s
            
    ## Create offsets for our files and append them to chunk ZERO
    offset = len(file_contents[0]) + 4*(len(file_contents)-1)
    for i in range(1,len(file_contents)):
        file_contents[0] += struct.pack("L", offset)
        offset += len(file_contents[i])
    
    ## Create the final scenario file
    final_scr = b''.join(file_contents)
    
    ## Save it
    fname_out = os.path.join(dir_scr_final, f"{file_prefix}.scr")
    with open(fname_out, 'wb') as f:
        f.write(final_scr)
        
        
        
def create_script_dat():
    ## Make sure we have the right number of files
    path = os.path.join(dir_scr_final, "*.scr")
    fname_scrs = glob.glob(path)
    
    if(len(fname_scrs) != 84):
        raise Exception("Expected 84 SCR files in the directory '{}'. Found {}.".format(dir_scr_final, len(fname_scrs) ))
    
    if(len(fname_scrs) != 84):
        raise Exception("Expected 84 SCR files in the array 'all_file_prefixes'. Found {}.".format(dir_scr_final, len(all_file_prefixes) ))
    
    ## Create the script.dat file header
    header = b"LNK\x00\x54" + b"\x00"*11
    
    offset = 0
    file_contents = []
    for file_prefix in all_file_prefixes:
        # Chunk metadata entries look like the following:
        # - chunk data offset (32bit LE uint)
        # - chunk length (32bit LE uint, exactly twice as big as the actual chunk length)
        # - chunk name (24 bytes; NUL-padded)
        with open(os.path.join(dir_scr_final, file_prefix+".scr"), 'rb') as f:
            s = f.read()
        
        
        size = len(s)
        fname = (file_prefix + ".scr").encode("ascii")
        fname += b"\x00"*(24-len(fname))
        
        header += struct.pack("L", offset)
        header += struct.pack("L", size*2)
        header += fname
        
        offset += size
        file_contents.append(s)
        
    ## Append the files to the dat file
    for file_content in file_contents:
        header += file_content
        
    ## Save the script.dat file
    with open(path_output_dat, 'wb') as f:
        f.write(header)
        
        
        
        
if __name__ == "__main__":
    for file_prefix in file_prefixes:
        print(file_prefix)
        
        with open(os.path.join(dir_preprocess, f'in_{file_prefix}.txt'), 'r') as f:
            s = f.read()
        
        s = preprocess_input(s)
        s = process_script(s)
        
        ## Save result
        with open(os.path.join(dir_processed, f'out_{file_prefix}'), 'wb') as f:
            f.write(s.encode("ansi"))
        
        script = s.encode("ansi")
        sections = script_to_sections(script)
        create_scr_chunks(sections)
        create_scr_file(file_prefix)
        
    create_script_dat()
    print("Created script.dat")