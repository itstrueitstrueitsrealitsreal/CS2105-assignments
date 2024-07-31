import sys
from socket import *


class Store:
    def __init__(self):
        self.kvps = {}
        self.counters = {}

    # key methods, accessible with /key
    # return res
    def update_val(self, key, val, count=None):
        if key not in self.counters:
            # check if count is specified
            if count:
                # update count if so
                self.update_count(count)
            # update val
            self.kvps[key] = val
            return Res(200)
        if key in self.counters and self.counters.get(key) < 1:
            self.kvps[key] = val
            return Res(200)
        return Res(405)

    # return res of status code and message
    def get_val(self, key):
        if key not in self.kvps:
            return Res(404)
        # decrement counter when queried
        content = self.kvps.get(key)
        self.update_count(key, -1)
        return Res(200, content)

    # return status code and content
    def del_val(self, key):
        # check if key exists
        if key not in self.kvps:
            return Res(404)
        # check if counter exists
        if key in self.counters:
            if self.counters.get(key) != "Infinity":
                return Res(405)
        if key in self.kvps:
            if key in self.counters:
                self.counters.pop(key)
            return Res(200, self.kvps.pop(key))

    # counter methods, accessible with /counter
    def update_count(self, key, val):
        # if key exists, decrease / add accordingly
        if key in self.kvps:
            # else, update counter value in counter store to val
            if key in self.counters:
                self.counters[key] += val
                if self.counters[key] == 0:
                    self.counters.pop(key)
                    self.kvps.pop(key)
                return Res(200)
            else:
                self.counters[key] = val
                return Res(200)
        return Res(405)

    # return list of status code and count
    def get_count(self, key):
        if key not in self.counters and key not in self.kvps:
            return Res(404)
        if key in self.counters:
            return Res(200, str(self.counters.get(key)).encode())
        return Res(200, b"Infinity")

    def delete_count(self, key):
        if key in self.counters:
            # remove counter by removing key from dict
            output = str(self.counters.pop(key)).encode()
            self.counters[key] = "Infinity"
            return Res(200, output)
        return Res(404)

    # return status code
    def insert_count(self, key, val):
        if key not in self.counters:
            return Res(405)
        self.update_count(key, val)
        return Res(200)


class WebServer:
    def __init__(self, port, host="127.0.0.1"):
        self.store = Store()
        self.host = host
        self.port = port

    def start(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        print("The server is listening at {}:{}".format(self.host, self.port))
        while True:
            connection_socket, client_addr = server_socket.accept()
            print('Client Socket: ', connection_socket)
            print('Client Address: ', client_addr)
            while True:
                req = Req(self.store, connection_socket)
                res = req.process()
                if not res:
                    break
                connection_socket.send(res.to_bytes())
        server_socket.close()


class Req:
    def __init__(self, store, socket):
        self.store = store
        self.socket = socket

    # method to process header and return a response if any
    def process(self):
        header = self.parse()
        # if header invalid
        if not header:
            return None
        # if path is key
        if header["path"].split("/")[1] == "key":
            return self.kvp_res(header)
        # if path is counter
        if header["path"].split("/")[1] == "counter":
            return self.counter_res(header)

    # method to split header into method, path and other components
    def parse(self):
        header = {}
        req = []
        string = []
        while True:
            # receive data character by character
            data = self.socket.recv(1)
            # if data isn't received
            if not data:
                self.socket.close()
                return
            # convert data to character
            data = data.decode()
            # if data is whitespace and there is an existing string
            if data == " " and string:
                req.append("".join(string))
                string = []
            # else if data is not whitespace
            elif data != " ":
                string.append(data)
            else:
                # if data is second consecutive whitespace
                break
        # place components of the header into their respective categories
        header["method"] = req[0].upper()
        header["path"] = req[1]
        header["other"] = {}
        # adding other components into header
        for i in range(2, len(req) - 1, 2):
            header["other"][req[i].lower()] = req[i + 1]
        return header

    # method to generate response for key query
    def kvp_res(self, header):
        key = header["path"].split("/")[2]
        match header["method"]:
            case "GET":
                data = self.store.get_val(key)
                return data
            case "POST":
                length = int(header["other"]["content-length"])
                body = self.parse_message(length)
                data = self.store.update_val(key, body)
                return data
            case "DELETE":
                data = self.store.del_val(key)
                return data

    # method to generate response for counter query
    def counter_res(self, header):
        key = header["path"].split("/")[2]
        match header["method"]:
            case "GET":
                data = self.store.get_count(key)
                return data
            case "POST":
                length = int(header["other"]["content-length"])
                val = int(self.parse_message(length))
                data = self.store.update_count(key, val)
                return data
            case "DELETE":
                data = self.store.delete_count(key)
                return data

    # method to read message of req
    def parse_message(self, length):
        content = b""
        while length > 0:
            data = self.socket.recv(length)
            if data:
                content += data
                length -= len(data)
            else:
                self.socket.close()
                return
        return content


class Res:
    STATUS_CODE = {
        200: "OK",
        404: "NotFound",
        405: "MethodNotAllowed"
    }

    def __init__(self, status_code, data=None):
        self.status_code = status_code
        self.msg = self.STATUS_CODE[status_code]
        self.data = data

    def to_bytes(self):
        output = "{} {} ".format(self.status_code, self.msg)
        if self.data is not None:
            return (output + "Content-Length {}  ".format(len(self.data))).encode() + self.data
        return (output + " ").encode()


if __name__ == '__main__':
    port = int(sys.argv[1])
    server = WebServer(port)
    server.start()
