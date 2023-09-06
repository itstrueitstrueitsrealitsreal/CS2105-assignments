import sys 

def main():
    while True:
        #obtain size of file
        bytes = getSize()

        if (bytes < 0):
           break
    
        while (bytes > 0):
            data = sys.stdin.buffer.read1(bytes)
            bytes -= len(data)
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()

def getSize():
    flag = True
    # create new bytearray object to store data
    byte_arr = bytearray()
    while (flag):
        data = sys.stdin.buffer.read1(1)
        # end of header
        if (data == b'B'):
          flag = False
        # EOF
        elif (len(data) == 0): 
          return -1
        else:
          byte_arr += bytearray(data)

    header = bytes(byte_arr).decode()
    return int(header.split()[1])


if __name__ == '__main__':
   main()