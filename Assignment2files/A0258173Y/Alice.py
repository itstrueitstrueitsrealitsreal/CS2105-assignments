# run with unreliNetPort as a cli argument
# read message from stdin
# send to UnreliNET
# messages contain ascii characters only, no empty messages
# no input delay
# need to detect end of transmission and terminate
# implement seq number and checksum
# packet size limit: 64 bytes
# checksum should be checked for every packet
# set socket timeout value for 50ms
# do so via socket.settimeout()
# format of packet: 64 byte total
# checksum is 32 bits = 4 bytes
# 1 byte for seq number
# 1 byte for length
# header is 6 bytes in total
# remaining 58 bytes are for data

import sys
import zlib
from socket import *


# reads up to 58 bytes of user input
def read_input():
    num_bytes = 58
    data = b''
    while num_bytes > 0:
        stdin = sys.stdin.buffer.read(num_bytes)
        if len(stdin) == 0:
            break
        data += stdin
        num_bytes -= len(stdin)
    return data


# multiplexes data, checksum, length of data and adds header to data
def mux(data, seq_num):
    packet = b''
    checksum = zlib.crc32(seq_num.to_bytes(1, "big") + len(data).to_bytes(1, "big") + data)
    packet += checksum.to_bytes(4, "big")
    packet += seq_num.to_bytes(1, "big")
    packet += len(data).to_bytes(1, "big")
    packet += data
    return packet


# reads header of packet, returns checksum, ack_num
def parse_header(header):
    checksum = header[:4]
    seq_num = int(header[4])
    return [checksum, seq_num]


# checks for corruption of ack
def not_corrupted(ack):
    checksum = zlib.crc32(ack[4:]).to_bytes(4, "big")
    return ack[:4] == checksum


def main():
    alice_port = int(sys.argv[1])
    alice_socket = socket(AF_INET, SOCK_DGRAM)
    alice_socket.settimeout(0.05)
    seq_num = 0
    data = read_input()

    while True:
        try:
            if len(data) == 0:
                break
            # add send packet to multiplexer
            packet = mux(data, seq_num)
            # send packet to unreliNet
            alice_socket.sendto(packet, ('127.0.0.1', alice_port))

            # rcv ack
            ack, addr = alice_socket.recvfrom(64)

            # check for corruption
            if not_corrupted(ack):
                checksum, ack_num = parse_header(ack)
                if ack_num == seq_num:
                    data = read_input()
                    seq_num ^= 1
        except timeout:
            continue

    alice_socket.close()


if __name__ == "__main__":
    main()
