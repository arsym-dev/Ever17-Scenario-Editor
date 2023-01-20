import os
import glob
import sys

"""
Potential problems (choices):
op00 48
sc1a 36
sc1b 2
sy5a 27
sy6b 8
s_1a 21
"""

dir = "D:/Games/Ever17/_extracted/script/_bak/"

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
        self.pos_last_token = 0
        self.pos_max = len(self.raw)
    
    
    def CheckForUnknownTokens(self):
        while (self.pos_curr < self.pos_max):
            try:
                token = self.GetChar(offset=0)
                token_length = self.CheckToken(token)
                
                if (token < 0x20):
                    self.pos_last_token = self.pos_curr
                
            except Exception as e:
                msg = str(e)
                msg += "\n[{}, Chunk {}, Offset {:04X}, Token: {:02X}]".format(self.name, self.chunk_num, self.pos_curr, self.token)
                
                raise Exception(msg) 
                
            
            
            if (token_length is None):
                self.pos_curr += 1
            else:
                self.pos_curr += token_length
        
    
    def PrintTroublesomeTokens(self):
        while (self.pos_curr < self.pos_max):
            try:
                token = self.GetChar(offset=0)
                token_length = self.CheckToken(token)
                
                if (token < 0x20):
                    self.pos_last_token = self.pos_curr
                
            except Exception as e:
                msg = str(e)
                msg += "\n[{}, Chunk {}, Offset {:04X}, Token: {:02X}]".format(self.name, self.chunk_num, self.pos_curr, self.token)
                
                raise Exception(msg) 
                
            
        self.pos_curr += token_length
    
    
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
    
    
    def GetTextSinceLastToken(self):
        pos_start = self.pos_last_token+1
        
        diff = self.pos_curr - pos_start
        if (diff < 2):
            pos_start -= 20
        pos_start = max(0, pos_start)
            
            
        txt = self.raw[pos_start:self.pos_curr]
        try:
            txt = txt.decode("ansi")
        except:
            pass
        
        return txt
    
    def GetTextUpcoming(self, length=10):
        pos_end = self.pos_curr+length
        pos_end = min(self.pos_max, pos_end)
            
            
        txt = self.raw[self.pos_curr:pos_end]
        try:
            txt = txt.decode("ansi")
        except:
            pass
        
        return txt
    
    
    def CheckToken(self, token):
        if (token >= 0x20):
            ## Text. Game ignores it outside of choice / textbox / NVL
            return
        
        self.token_prev = self.token
        self.token = token
        
        msg  ="[{}, Chunk {:03}, Offset {:04X}, Token: {:02X}] ".format(self.name, self.chunk_num, self.pos_curr, self.token)
        txt = self.GetTextSinceLastToken()
        txt_next = self.GetTextUpcoming(10)
        
        if (self.token == 0x00):
            ## End of chunk
            if (self.token_prev == 0x0D):
                ## This is the closing tag for a voice clip
                return
            
            if (self.pos_curr < self.pos_max-1):
                raise Exception("End of file detected too early.")
            
            return
            
        elif (self.token == 0x01):
            if (self.token_prev == "0x0b"):
                ## End of choice entry
                pass
            
            ## Newline in text
            return
            
        elif (self.token == 0x02):
            ## Wait for user acknowledgement
            return
        
        elif (self.token == 0x03):
            ## Clear textbox and save to history
            return
            
        elif (self.token == 0x04):
            args = self.GetArgs(5)
            ## Alternate user input (pause, quick transitin)
            
            if (args[1] >= 0x80 and args[1] <= 0x8F):
                ## Small pause between letters?
                ## Immediately play next effect then wait for user acknowledgement?

                if (args[2] != 0x00 or args[3] != 0x00):
                    raise UnknownArgumentsException(args)
                
                else:
                    print (msg + txt + "{4:" + "{:02X}".format(args[1]) + "} " + txt_next + "- Small pause between letters?")
                    return 4
            
            elif (args[1] == 0xA0):
                ## 04 A0 xx 00 00 = How long to pause before continuing in auto mode
                
                if (args[3] != 0x00 or args[4] != 0x00):
                    raise UnknownArgumentsException(args)
                
                else:
                    print (msg + txt + "{4:A0-" + "{:02X}".format(args[2]) + "} " + txt_next + "--- Pause")
                
                return 5
                
            else:
                raise UnknownArgumentsException(args)
            
        elif (self.token == 0x05):
            ## Start of textbox entry
            args = self.GetArgs(4)
            if (args[1] != 0x80 or args[2] != 0x00 or args[3] != 0x00):
                raise UnknownArgumentsException(args)
            
            return 4
        
        elif (self.token == 0x0b):
            ## Choices
            
            args = self.GetArgs(2)
            if (args[1] == 0x00):
                ## Start of choice menu
                args = self.GetArgs(4)
                id = args[3]*0x100 + args[2]
                return 4
            
            elif (args[1] == 0x01):
                ## Standard choice
                return 2
            
            elif (args[1] == 0x02):
                args = self.GetArgs(8)
                ## Conditional choice. May or may not appear based on the value of some variable
                if (args[2] == 0x28 and args[3] == 0x0a and args[4] == 0xa4 and args[6] == 0x14  and args[7] == 0x00):
                    if (args[5] >= 0xd0 and args[5] <= 0xd5):
                        return 8
                    else:
                        raise UnknownArgumentsException(args)
                    
                else:
                    raise UnknownArgumentsException(args)
            
            else:
                raise UnknownArgumentsException(args)
        
        elif (self.token == 0x0c):
            ## Continue immediately without waiting for user acknowledgement
            
            # Grab last few entries
            txt = self.GetTextSinceLastToken()
            print(msg + txt + "{12} - [Continue immediately]")
            return
        
        elif (self.token == 0x0d):
            ## Start of voice clip
            return
        
        elif (self.token == 0x0e):
            ## Start of chunk
            return
            
            
        elif (self.token == 0x10):
            ## No clue. Clear the NVL screen?
            args = self.GetArgs(2)
            
            if (args[1] == 0x00):
                ## Start centered text
                print (msg + "{16:0}" + txt_next)
            
            elif (args[1] == 0x01):
                ## End centered text
                print (msg + txt + "{16:1}")
            
            elif (args[1] == 0x04):
                ## Clear NVL mode
                print (msg + txt + "{16:4} - [Clear text and save to history]")
                
            else:
                raise UnknownArgumentsException(args)
            
            return 2
        
        
        elif (self.token == 0x11):
            ## Change font size
            args = self.GetArgs(2)
            
            if (args[1] == 0x03):
                ## Font size 3: Huge font
                print (msg + "{17:3}" + txt_next)
            else:
                raise UnknownArgumentsException(args)
            
            return 2
            
            
        else:
            raise Exception("Unknown token")


if __name__ == "__main__":
    file_prefixes = [x[1] for x in os.walk(dir)][0]
    
    for file_prefix in file_prefixes:
        filepaths = glob.glob(os.path.join(dir, file_prefix, "*.scr_chunk*"))
        chunk_num_max = len(filepaths)
        
        
        for chunk_num in range(1, chunk_num_max):
            filepath = filepaths[chunk_num]
        
            c = Chunk(filepath, file_prefix, chunk_num)
            #c.CheckForUnknownTokens()
            c.PrintTroublesomeTokens()
            
        #print("Done checking " + file_prefix)