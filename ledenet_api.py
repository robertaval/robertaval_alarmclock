import socket
import binascii
import time

class  led_lights():

    def __init__(self):
        self.list = []

    def __iter__(self):
        return iter(self.list)

    def __len__(self):
        return len(self.list)

    def __getitem__(self,index):
        if isinstance (index, int):
            return self.list[index]
        elif isinstance (index, str):
            return self[tuple(a.ip for a in self).index(index)]
        else:
            return None

    def __str__(self):
        resp = ''
        for b in self:
            resp += b.__str__() + '\n'
        return resp

    def exists(self, ip):
        return ip in (blub.ip for blub in self)

    def add(self, bulb):
        if self.exists(bulb.ip):
            raise DuplicateNameError(bulb.ip, ': this ip adress is  allready taken')
        else:
            self.list.append(bulb)
            bulb.scan()

    def delete(self, bulb):
        if self.exists(bulb.name):
            self.list.remove(bulb)

    def all_on(self):
        for bulb in self:
            if not bulb.is_on:
               bulb.turn_on()

    def all_off(self):
        for bulb in self:
            if bulb.is_on:
               bulb.turn_off()

    def all_set_color(r,g,b):
        for bulb in self:
            bulb.set_color(r,g,b)

    def all_dim(level):
        for bulb in self:
            bulb.dim(level)

    def scan(self, timeout=10, DISCOVERY_PORT=48899):

        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.bind(('', DISCOVERY_PORT))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        msg = "HF-A11ASSISTHREAD"
        msg = msg.encode('utf-8')
        # set the time at which we will quit the search
        quit_time = time.time() + timeout
        response_list = []
        while True:   # outer loop for query send
             if time.time() > quit_time:
                 break
             sock.sendto(msg, ('<broadcast>', DISCOVERY_PORT)) # send out a broadcast query
             while True:                      # inner loop waiting for responses
                 sock.settimeout(1)
                 try:
                     data, addr = sock.recvfrom(64)
                 except socket.timeout:
                     data = None
                     if time.time() > quit_time:
                         break

                 if data is not None and data != msg:
                     # tuples of name and IP addresses
                     data = data.decode('utf-8')
                     item = dict()
                     item['ip'] = data.split(',')[0]
                     item['id'] = data.split(',')[1]
                     item['model'] = data.split(',')[2]
                     response_list.append(item)

                     # add the individual ip adresses to the list
        for r in response_list:
            ip = r['ip']
            id = r['id']
            if not self.exists(ip):
                self.add(bulb(ip, id))




class bulb():
    def __init__(self, ip, id = None, port = 5577):

         self.ip           = ip
         self.port         = port
         self.id           = id
         self.is_on        = False
         self.socket       = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

         self.color        = bytearray([255, 255, 255]) # r g b
         self.brightness   = None
         self.color_set    = ('red', 'green', 'blue')

         self.socket.connect((self.ip, self.port))


    def __str__(self):
        str ='id {id} ip: {ip} port: {port} on: {on}, red: {red} green {green} blue {blue}, brightness {brightness}'
        return str.format(id = self.id, ip = self.ip, port = self.port,
                          on = self.is_on, red = self.__color('red'), green = self.__color('green'),
                          blue = self.__color('blue'), brightness = self.brightness)

    def __del__(self):
        self.socket.close()

    def __color(self, color_code, color_val=None):
        i = self.color_set.index(color_code)
        if isinstance(color_val, int):
            self.color[i] = max(min(255, color_val), 0) #val should be between 0 and 255
        return self.color[i]

    def status(self):
        '''.status() retrieves the status of the bulb as held by the controller and
        updates the bulb attributes'''
        msg =  bytearray([0xef, 0x01, 0x77])
        self.__write(msg)
        # typical response:
        #pos  0  1  2  3  4  5  6  7  8  9 10
        #    66 01 24 39 21 0a ff 00 00 01 99
        #     |     |           |  |  |  |  |
        #     |     |           |  |  |  |  checksum
        #     |     |           |  |  |  warmwhite
        #     |     |           |  |  blue
        #     |     |           |  green
        #     |     |           red
        #     |     off(23)/on(24)
        #     |
        #     |
        #     msg head
        #
        rx = self.__read(11)
        self.color[0] = rx[6] #red
        self.color[1] = rx[7] #green
        self.color[2] = rx[8] #blue
        self.brightness = max(rx[6], rx[7], rx[8])
        self.on = rx[2] == 0x24

    def turn_on(self,on=True):
        if on == True:
            msg =  bytearray([0xcc, 0x23, 0x33]) # 0x23 = on
        else:
            msg =  bytearray([0xcc, 0x24, 0x33]) # 0x24 = off
        self.on = on
        self.__write(msg)

    def turn_off(self):
        self.turn_on(on=False)

    def set_color(self, r, g, b):
        # typical msg 56 ff 00 00 aa <- red
        msg = bytearray([0x56])
        msg.append(self.__color('red',r))
        msg.append(self.__color('green',g))
        msg.append(self.__color('blue',b))
        msg.append(0xaa)
        self.__write(msg)
        self.brightness = max(self.color)

    def dim(self, level=None):
        #100% brightness means one color is full
        current_level = max(self.color)
        if level != None:
            adjust = level/current_level
            self.set_color(int(self.color[0]*adjust),
                           int(self.color[1]*adjust),
                           int(self.color[2]*adjust))

        self.brightness = max(self.color)
        return self.brightness

    def gradual(self,red=255,green=255,blue=255,duration=300, increase = True):

        step = 1
        if duration >0: 
            step = 1/duration
        if increase:
            self.set_color(0,0,0)
            i = 0
        else:
            self.set_color(red,green,blue)
            step = -step
            i = 1
        self.turn_on()
        for t in range(duration + 1):
            i += step
            self.set_color(int(red*i), int(green*i), int(blue*i))
            time.sleep(1)

    def __read(self, length):
        #socket does not know when the message is complete
        #length is the expected length of the message
        #socket  listens and appends the resonse until the
        #message of the expected length has been recieved
        #or a certain time has expired
        remaining = length
        response = bytearray()
        while remaining > 0:
            chunk = self.socket.recv(length)
            remaining -= len(chunk)
            response.extend(chunk)
#       print (' '.join(list('{:02x}'.format(r) for r in response)))
        return response

    def __write(self, message, checksum = False):
        if checksum: #calculate checksum and append to message
            csum = sum(message) & 0xff
            message.append(csum)
#        print ('sending:',binascii.hexlify(message))
        self.socket.send(message)
