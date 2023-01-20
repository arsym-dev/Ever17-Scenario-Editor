import struct

fname = "D:\\Games\\VN\\Ever17\\PC\\_images\\system\\map_coment.cps"

def cps_unobfuscate(data):
    v_off = struct.unpack(b'<L', data[-4:])[0] - 0x7534682
    if (v_off == 0):
     return data

    val_obf = struct.unpack(b'<L', data[v_off:v_off+4])[0] + v_off + 0x3786425
    data_len = len(data)
    if (data_len < 20):
     return data

    i_i = 0x10
    off_lim = len(data)-4
    vlim = 1 << 32

    while (i_i < off_lim):
     if (i_i != v_off):
        # Skip obfuscation information
        (v,) = struct.unpack('<L', data[i_i:i_i+4])
        v -= val_obf + data_len
        v %= vlim
        data[i_i:i_i+4] = struct.pack('<L', v)
     
     val_obf *= 0x41c64e6d
     val_obf %= vlim
     val_obf += 0x9b06 
     val_obf %= vlim
     
     i_i += 4
    del(data[-4:])
    return data

def e17_rle_unpack(din, out_sz):
   dout = bytearray(out_sz)
      
   def read_data(num=1):
      nonlocal i_i
      rv = din[i_i:i_i+num]
      i_i += 1
      return rv
      
   def read_u8():
      return read_data()[0]
      
   def copy_bytes(n):
      nonlocal i_i, i_o
      dout[i_o:i_o+n] = din[i_i:i_i+n]
      i_i += n
      i_o += n
      
   i_i = 0
   i_o = 0
   while (i_o < out_sz):
      rt = read_u8()
      #print(rt, len(din)-i_i, out_sz-i_o)
      if (rt & 0x80):
         if (rt & 0x40):
            # RLE encoded byte sequence
            run_length = (rt & 0x1F) + 2
            if (rt & 0x20):
               run_length += read_u8() << 5
            run_length = max(run_length,1)   
            data_byte = read_data()
               
            output_left = out_sz - i_o + 1
            if (output_left < run_length):
               run_length = output_left
               
            dout[i_o:i_o+run_length] = bytes(data_byte) * run_length
            i_o += run_length
            
         else:
            # Reference to an earlier version of the same byte sequence
            rl_raw = (rt >> 2) & 0xF
               
            run_length = max(rl_raw + 2,1)
            out_off = ((rt & 3) << 8) + read_u8() + 1
            i_oi = i_o - out_off
            for i in range(run_length):
               dout[i_o+i] = dout[i_oi+i]
            i_o += run_length
      else:
         if (rt & 0x40):
            # Repeated byte sequence
            iter_count = read_u8()+1
            run_length = (rt & 0x3F) + 2
            run_length = max(run_length,1)
               
            if (iter_count):
               for _ in range(iter_count):
                  output_left = out_sz - i_o + 1
                  if (output_left < run_length):
                     run_length = output_left
                     
                  dout[i_o:i_o+run_length] = din[i_i:i_i+run_length]
                  i_o += run_length
            else:
               raise
            i_i += run_length
               
         else:
            # Literal multi-byte sequence
            run_length = (rt & 0x1F) + 1
            if (rt & 0x20):
               run_length += read_u8() << 5
            run_length = max(run_length,1)

            output_left = out_sz - i_o + 1
            if (output_left < run_length):
               run_length = output_left
            copy_bytes(run_length)
   return dout

if __name__ == "__main__":
    with open(fname, "rb") as f:
        data = bytearray(f.read())

    out_sz = struct.unpack(b'<L', data[12:16])[0]

    unobf = cps_unobfuscate(data)
    unpac = e17_rle_unpack(unobf[20:], out_sz)

    with open(fname + ".d", "wb") as f:\
        f.write(unpac)