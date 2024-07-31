import sys
import zlib

def main():
    with open(sys.argv[1], "rb") as f:
        bytes = f.read()
    print(zlib.crc32(bytes))

if __name__ == '__main__':
    main()