import os
import glob
import sys

"""
## TODO
Look for double quotes
Look for dialogue WITHOUT quotes
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

dir_scr_extracted = "D:/Games/VN/Ever17/PC/_extracted/script/_bak"

class UnknownArgumentsException(Exception):
    def __init__(self, args):
        self.args = args
        
    def __str__(self):
        msg = "Unknown argument(s)"
        
        for arg in self.args:
            msg += " {:02X}".format(arg)
        
        return msg


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
                
            
            
            if (token_length is None):
                self.pos_curr += 1
            else:
                self.pos_curr += token_length
        
        return ret
    
    
    def DumpFormatingTokens(self):
        ret = ""
        while (self.pos_curr < self.pos_max):
            try:
                token = self.GetChar(offset=0)
                token_length, opcode, token_str = self.CheckToken(token)
                
                if (opcode == 0x04 or opcode == 0x0b or opcode == 0x0c or opcode == 0x10 or opcode == 0x11):
                    ret += "\n[{}, Chunk {}, Offset {:04X}, Token: {:02X}] ".format(self.name, self.chunk_num, self.pos_curr, self.token)
                    ret += token_str
                
            except Exception as e:
                msg = str(e)
                msg += "\n[{}, Chunk {}, Offset {:04X}, Token: {:02X}]".format(self.name, self.chunk_num, self.pos_curr, self.token)
                
                raise Exception(msg) 
                
            
            
            if (token_length is None):
                self.pos_curr += 1
            else:
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
            ## Wait for user acknowledgment
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
                return 2, token, "{11:1}\n"
            
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


if __name__ == "__main__":
    file_prefixes = [x[1] for x in os.walk(dir_scr_extracted)][0]
    
    for file_prefix in file_prefixes:
        filepaths = glob.glob(os.path.join(dir_scr_extracted, file_prefix, "*.scr_chunk*"))
        chunk_num_max = len(filepaths)
        
        
        for chunk_num in range(1, chunk_num_max):
            filepath = filepaths[chunk_num]
        
            c = Chunk(filepath, file_prefix, chunk_num)
            
            
            #val = c.DumpTokens()
            val = c.DumpFormatingTokens()
            if val != "":
                print(val)
            
        #sys.exit()
        #print("Done checking " + file_prefix)