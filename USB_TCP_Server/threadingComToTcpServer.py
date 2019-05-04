import socket
import threading
import serial
import time

class ThreadedServer(object):
    def __init__(self, host, port=3003):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.comPort = "com" + str(self.port-3000)
        self.comDevice = serial.Serial(self.comPort, baudrate=19200, writeTimeout = 100000)
        self.clients = []
        threading.Thread(target = self.listenToCom,args = (self.clients , self.comDevice)).start()

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            print "new client at adress" , address
            self.clients.append(client)
            client.setblocking(0)
            threading.Thread(target = self.listenToClient,args = (client,address, self.comDevice)).start()



    def listenToClient(self, client, address, comDevice):
        size = 20
        while True:
            time.sleep(0.003)
            try:
                data = client.recv(size)
                if data:
                    comDevice.write(data)
##                    print data
                else:
                    print('Client disconnected')
                    client.close()
                    return False
            except :
                pass


    def listenToCom(self, clients,  comDevice):
        while comDevice.isOpen():
            time.sleep(0.003)
            while self.comDevice.inWaiting()>= 1:
                data = self.comDevice.readline()
##                print data
                for client in clients:
                    try:
                        client.send(data)  # echo
                    except:
##                        print "could not send to client", client
                        clients.remove(client)
                        pass


if __name__ == "__main__":
    while True:
        port_num = input("TCP Port? (3000 + com Port) ")
        try:
            port_num = int(port_num)
            com_port = int(port_num)-3000
            if com_port > 0 or None: break
        except ValueError:
            pass


    ThreadedServer('',port_num).listen()