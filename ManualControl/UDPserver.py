import socket
import time
import os
import sys
import threading

try:
    import netifaces
except ImportError:
    try:
        command_to_execute = "pip install netifaces || easy_install netifaces"
        os.system(command_to_execute)
    except OSError:
        print ("Can NOT install netifaces, Aborted!")
        sys.exit(1)
    import netifaces

# class definition
class DockingSystem:
    def __init__(self, boat_ID, dock_num):
        ## variable assignment
        self.TimeBegin = time.time()
        self.send_PORT_default = 8888
        self.bind_PORT = 9999
        
        self.broadmsg = boat_ID 
        self.DSNum = dock_num  # docking system number
        self.collectAllFlag = False # True when all clients are collected
        
        self.IPdic = {} # {'ID name':{'IP adress':IP,'port':8888}} for all docking system
        
        ## initialization workflow
        self.routingIPAddr, self.routingIPNetmask = self.getIP() # get the IP
        self.BroadcastAddr = self.getBroadcast() 
        self.s = self.getSocket() # build the socket
        
        ## connect the clients
        client_thread = threading.Thread(target=self.set_client)
        client_thread.setDaemon(True)
        client_thread.start()
        
        udp_thread = threading.Thread(target=self.UDP_receive)
        udp_thread.setDaemon(True)
        udp_thread.start()
        
    # actions
    
    def ON(self, whichDS):
        message = "CONTROL1"
        try:
            client_addr = self.IPdic[whichDS]['ip']
            client_port = self.IPdic[whichDS]['port']
            self.UDP_send(message, client_addr, client_port)
        except Exception as e:
            print(e)
            print('Turning on command fails to ' + whichDS)
    
    def OFF(self, whichDS):
        message = "CONTROL0"
        try:
            client_addr = self.IPdic[whichDS]['ip']
            client_port = self.IPdic[whichDS]['port']
            self.UDP_send(message, client_addr, client_port)
        except Exception as e:
            print(e)
            print('Turning off command fails to ' + whichDS)
    
    # functions
    def getIP(self):# get the IP Address and Net Mask
        routingGateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
        routingNicName = netifaces.gateways()['default'][netifaces.AF_INET][1]
        
        for interface in netifaces.interfaces():
            if interface == routingNicName:
                # print netifaces.ifaddresses(interface)
                routingNicMacAddr = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
                try:
                    routingIPAddr = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
                    # TODO() Note: On Windows, netmask maybe give a wrong result in 'netifaces' module.
                    routingIPNetmask = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['netmask']
                except KeyError:
                    pass
        
        display_format = '%-30s %-20s'
        print (display_format % ("Routing Gateway:", routingGateway))
        print (display_format % ("Routing NIC Name:", routingNicName))
        print (display_format % ("Routing NIC MAC Address:", routingNicMacAddr))
        print (display_format % ("Routing IP Address:", routingIPAddr))
        print (display_format % ("Routing IP Netmask:", routingIPNetmask))
        
        return routingIPAddr, routingIPNetmask
    
    def getint(self, data):
        addr = data.split('.')
        for k, v in enumerate(addr):
            addr[k] = int(v, 10)
        return addr
    
    def getBroadcast(self):
        localIP = self.getint(self.routingIPAddr)
        Netmask = self.getint(self.routingIPNetmask)
        broadcast = ""
        for k, v in enumerate(localIP):
            broadcast = broadcast + str( (~Netmask[k] | (Netmask[k] & localIP[k]))+256) + '.'
        broadcast = broadcast[:-1]
        return broadcast

    def getSocket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('', self.bind_PORT))
        s.settimeout(3)
        
        print('Bind UDP on ', self.bind_PORT, '...')
        print('Broadcast to ', self.BroadcastAddr, ':', self.send_PORT_default)
        return s

    #各设备IP地址：
    def set_client(self): # send the signal and scan all the device in 4 seconds
        print("Start scanning")
        self.UDP_send(self.broadmsg, self.BroadcastAddr, self.send_PORT_default) # braodmsg is ID
        #time_scanStarts = time.time()
        while not self.collectAllFlag:
            try:
                if len(self.IPdic) >= self.DSNum:
                    self.collectAllFlag = True
                    print('All devices are as follows:')
                    print(self.IPdic)
                    print("Scanning over")
                    for k, v in self.IPdic.items():
                        self.UDP_send("Connected", v['ip'], v['port']) # k = ip
                    break
                data, addr = self.s.recvfrom(1024)
                # time_scanStarts = time.time()
                # ctypes.windll.user32.MessageBoxA(0, data.decode("utf-8").encode('gb2312'), u' 信息'.encode('gb2312'), 0)
                data = data.decode('utf-8')
                message = 'Received from %s:%s' % (addr, data)
                print(message)
                client_ip = addr[0]
                client_info = {'ip': client_ip, 'port': addr[1]} # client's name and Port
                if client_ip.startswith(self.BroadcastAddr[0:4]):
                    self.IPdic[data] = client_info
                    print('Get the device:', data,', ',client_ip)
    
            except Exception as e:
                print(e)
                self.UDP_send(self.broadmsg, self.BroadcastAddr, self.send_PORT_default)

    def UDP_send(self, context, IPaddr, device_PORT):
        #
        self.s.sendto(context.encode("utf-8"), (IPaddr, device_PORT))

    def UDP_receive(self):
        # global all_data
        while not self.collectAllFlag:
            try:
                data, addr = self.s.recvfrom(2048)
                data = data.decode("utf-8")
                # ctypes.windll.user32.MessageBoxA(0, data.decode("utf-8").encode('gb2312'), u' 信息'.encode('gb2312'), 0)
                # print(addr.type)
                message = 'Received from (%s:%s),%s' % (addr[0],addr[1], data)
                # client_info = message.split(',')
                #TimeStep = time.time() - self.TimeBegin
                # all_data.append(client_info)
                client_addr = addr[0]
                client_port = addr[1]
                print(message)
                self.UDP_send("Connected", client_addr, client_port)
            except Exception as e:
                print(e)
                self.UDP_send(self.broadmsg, self.BroadcastAddr, self.send_PORT_default)
                
#

# if __name__ == "__main__":
#     DS = DockingSystem('BOAT_1', 2)
#     time.sleep(5)
#     
#     while 1:
#         x = input('Enter:')
#         if x == '11':
#             DS.ON('BOAT_1_DOCK_1')
#             print('turn on 1')
#         if x == '10':
#             DS.OFF('BOAT_1_DOCK_1')
#             print('turn off 1')
#         if x == '21':
#             DS.ON('BOAT_1_DOCK_2')
#             print('turn on 2')
#         if x == '20':
#             DS.OFF('BOAT_1_DOCK_2')
#             print('turn off 2')
        
    

