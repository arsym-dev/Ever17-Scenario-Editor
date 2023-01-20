import glob
import os
import sys
import re

file_prefix = "*"

dir_scr_original = "D:/Games/Ever17/_extracted/script/_bak/"
dir_scr_final = "D:/Games/Ever17/_extracted/script/"
dir_script = "text/out"


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
        ##  byte: Opcode
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
                ## Immediately play next effect then wait for user acknowledgment?

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
            ## Continue immediately without waiting for user acknowledgment
            return 1, token, "{12}"
        
        elif (self.token == 0x0d):
            ## Start of voice clip
            return 1, token, "{"
        
        elif (self.token == 0x0e):
            ## Start of text entry. Not strictly necessary. Seems to denote chunks with executable content rather than just image reference for BG/sprites
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

if file_prefix == "*":
    fnames = glob.glob(os.path.join(dir_script, "out_*.txt"))
else:
    fnames = [os.path.join(dir_script, "out_"+file_prefix + '.txt')]

## Open the script and divide it into numbered sections
## Each entry in "sections" is an array that contains a valid text entry. This is either a voice tag or formatted text

for fname in fnames:
    file_prefix = fname.split("\\")[-1][4:-4]
    print(file_prefix)

    with open(os.path.join(dir_script, "out_"+file_prefix + '.txt'), 'rb') as f:
        script = f.read()

    ## TODO: Replace tokens with the hex equivalent
    script = re.sub(b'\r\n', b'\n', script) ## Newlines
    script = re.sub(b'\{1}', b'\x01', script) ## Newlines
    script = re.sub(b'\{11:0.*?}', b'\n', script) ## Choice start
    script = re.sub(b'\{11:1}(.*?)\n', b'\\1\x01\n', script) ## Choice
    script = re.sub(b'\{16:4}\n', b'\n', script) ## Clear screen
    script = re.sub(b'\{(.*?)}', b'\\1\n', script) ## Voice tags

    sections = []
    lines = script.split(b"\n")
    accumulator = []
    sec_id = 0

    for line in lines:
        x = re.search(b"([0-9])* :", line)
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

    #print(sections)
    #sys.exit()



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
        
        print(section_idx, "ori", scr_original.raw)
        print(section_idx, "new", ret)
        print(section_idx, "arr", sections[section_idx])
        
        with open("{0}/{1}/{1}.scr_chunk_{2:03}".format(dir_scr_final,file_prefix, section_idx), 'wb') as f:
            f.write(ret)
        
        limit_count += 1
        if (limit_count>500):
            break