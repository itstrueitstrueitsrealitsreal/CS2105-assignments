from socket import *

try:
    serverName = '127.0.0.1'
    serverPort = 2105
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))

    commands = [
        'POST /key/keyT content-length 7  abcdefg',
        'POST /counter/keyT content-length 1  3',
        'DELETE /key/keyT  ',
        'GET /key/keyT  ',
        'GET /counter/keyT  ',
        'DELETE /counter/keyT  ',
        'GET /counter/keyT  ',
        'DELETE /key/keyT  ',
        'GET /counter/keyT  ',
        'POST /key/key dummy hdr content-length 7 unknowN Header  abcdefg',
        'GET /key/key  '
    ]

    results = [
        "200 OK  ",
        "200 OK  ",
        "405 MethodNotAllowed  ",
        "200 OK Content-Length 7  abcdefg",
        "200 OK Content-Length 1  2",
        "200 OK Content-Length 1  2",
        '200 OK Content-Length 8  Infinity',
        '200 OK Content-Length 7  abcdefg',
        '404 NotFound  ',
        "200 OK  ",
        "200 OK Content-Length 7  abcdefg"
    ]
    error = False
    for i in range(len(commands)):
        clientSocket.send(commands[i].encode())
        result = clientSocket.recv(1024)
        if result.decode() != results[i]:
            print("[{}] - [{}], test case {}".format(result.decode(), results[i], 1 + i))
            error = True
    print("Has Error:", error)
finally:
    clientSocket.close()