# run with rcvPort as a cli argument
# receives chat messages from alice
# prints them to stdout
# send feedback to alice (ACK, NAK, seq number)
# no need to manually terminate
# have to combine messages together if the packets are split

import sys
import zlib
from socket import *


# checks if packet is corrupted
def not_corrupted(packet):
    checksum = zlib.crc32(packet[4:]).to_bytes(4, "big")
    return packet[:4] == checksum


# demultiplexes packet, returns sequence number, length and data
def demux(packet):
    return [int(packet[4]), packet[5], packet[6:]]


# creates ack
def ack(seq_num):
    data = chr(6).encode()
    packet = seq_num.to_bytes(1, "big") + len(data).to_bytes(1, "big") + data
    checksum = zlib.crc32(packet).to_bytes(4, "big")
    return checksum + packet


def main():
    bob_port = int(sys.argv[1])
    bob_socket = socket(AF_INET, SOCK_DGRAM)
    bob_socket.bind(('127.0.0.1', bob_port))
    curr_seq_num = 0

    while True:
        # rcv from unreliNET
        packet, addr = bob_socket.recvfrom(64)
        # check for corruption
        if not_corrupted(packet):
            seq_num, length, data = demux(packet)
            # check seq_num against curr seq_num
            if seq_num == curr_seq_num:
                print(data.decode(), end="")
                curr_seq_num ^= 1

        bob_socket.sendto(ack(curr_seq_num ^ 1), addr)


if __name__ == "__main__":
    main()
