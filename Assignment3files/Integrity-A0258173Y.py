# !/usr/bin/env python3
import os
import sys
from Cryptodome.Hash import SHA256

if len(sys.argv) < 3:
    print("Usage: python3 ", os.path.basename(__file__), "key_file_name document_file_name")
    sys.exit()

key_file_name   = sys.argv[1]
file_name       = sys.argv[2]

# get the authentication key from the file
key_file = open(key_file_name, "rb")
key = key_file.read()

# read the input file
input = open(file_name, "rb")

# First 32 bytes is the message authentication code
input = input.read()
mac_from_file = input[:32]

# Use the remaining file content to generate the message authentication code
mac_generated = SHA256.new(input[32:] + key).digest()

if mac_from_file == mac_generated:
    print ('yes')
else:
    print ('no')
