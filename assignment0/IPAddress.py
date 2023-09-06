import sys
import functools

# function that converts binary to integer
def convert(byte):
    # uses the int function to convert a base 2 byte to an integer, 
    # converting it to a string to keep any leading 0s.
    return str(int(byte, 2))

# function that separates binary address into list of bytes
def isolate_bytes(addr):
    # range() takes in start, stop, step args
    # use list comprehension to form the list
    # split addr into chunks of 8 bits
    return [addr[x : x + 8] for x in range(0, len(addr), 8)]

def main():
    input = sys.argv[1]
    bytes = isolate_bytes(input)
    ints = map(convert, bytes)
    print(functools.reduce(lambda x, y: x + '.' + y, ints)
)
          
if __name__ == '__main__':
    main()