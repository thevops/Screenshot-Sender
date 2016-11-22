# -*- coding: utf-8 -*-
# Python 2.7

# GUI and Threads
from Tkinter import *
from threading import Thread

# core
from socket import *
import matplotlib.pyplot as plt
import pyscreenshot as ImageGrab
from io import BytesIO
import time
import struct
import netifaces as ni


class ScreenMaker():

    def __init__(self):
        self.top = Tk()
        self.top.minsize(width=190, height=150)
        self.top.maxsize(width=190, height=150)
        self.top.title("ScreenshotSender")
        self.top.protocol('WM_DELETE_WINDOW', self.exit)

        self.play = False # toggle

        # interface
        self.chosen_iface = StringVar()
        self.iface_options = self.getInteface()
        self.chosen_iface.set(self.iface_options[0])
        # screen resolution
        self.width = self.top.winfo_screenwidth()
        self.height = self.top.winfo_screenheight()
        self.chosen_resolution = StringVar()
        self.res_list = self.resolutionOptions()
        self.chosen_resolution.set(self.res_list[0])

        # GUI
        self._ = Label(self.top, text="SERVER", justify = "center").grid(column = 0, columnspan=2, row = 0)

        self._ = Label(self.top, text="Interface:", justify = "center").grid(column = 0, row = 1)
        self.iface_box = OptionMenu(self.top, self.chosen_iface, *self.iface_options).grid(column = 1, row = 1)

        self._ = Label(self.top, text="Port:", justify = "center").grid(column = 0, row = 2)
        self.port_box = Entry(self.top, width=6)
        self.port_box.grid(column = 1, row = 2)

        self._ = Label(self.top, text="Resolution:", justify = "center").grid(column = 0, row = 3)
        self.resolution_box = OptionMenu(self.top, self.chosen_resolution, *self.res_list).grid(column = 1, row = 3)

        self._ = Label(self.top, text="Speed [s]:", justify = "center").grid(column = 0, row = 4)
        self.speed_box = Entry(self.top, width=6)
        self.speed_box.grid(column = 1, row = 4)

        self.start_stop = Button(self.top, bg="red",text="Start", relief=RAISED, command = self.run)
        self.start_stop.grid(column = 0, columnspan = 2, row = 5) 

        self.top.mainloop()



    def exit(self):
        self.top.destroy()

    def nothing(self):
        pass

    def getInteface(self):
        """
        Return list of available interfaces.
        If interface is not connected then it raise error, so that why is try clause.
        """
        addr_list = []
        for i in ni.interfaces():
            try:
                addr_list.append(ni.ifaddresses(i)[2][0]['addr'])
            except:
                pass
        return addr_list

    def resolutionOptions(self):
        """
        strange behaviour - if item of res = "800x600", then python interprets its as unicode
        that why is "800 x 600" - space between number and "x"
        """
        res = [
                str(self.width)+" x "+str(self.height), 
                "800 x 600",
                "640 x 480"
                ]
        return res

    def parseResolution(self):
        r = self.chosen_resolution.get()
        r=r.replace(" ","").replace("x"," ").split()
        return r


    def restoreGui(self):
        self.play = not self.play
        self.start_stop.config(text='Start', bg="red")
        self.top.protocol('WM_DELETE_WINDOW', self.exit)

    # ---------------------------------------------------------------------
    def sendBinaryFile(self, sock, data):
        """
        !I as format means: ! = network, I = unsigned int
        """
        sock.sendall(struct.pack('!I', len(data))) # send file size
        sock.sendall(data) # send fiile

    # ---------------------------------------------------------------------

    def run(self):
        self.play = not self.play
        if self.play == True: # run screenshots sending
            self.top.protocol('WM_DELETE_WINDOW', self.nothing)
            self.start_stop.config(text='Stop', bg="green")
            a=Thread(target=self.screenSender, name = "Sender")
            a.start()
        if self.play == False: # stop screenshots sending
            self.top.protocol('WM_DELETE_WINDOW', self.exit)
            self.start_stop.config(text='Start', bg="red")


    def screenSender(self):
        try:
            address = self.chosen_iface.get()
            port = int(self.port_box.get())
            speed = float(self.speed_box.get())
            resolution = self.parseResolution()
        except Exception, Arg:
            print Arg
            self.restoreGui()
            return

        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            s.bind((address, port))
            s.listen(1)
            client,addr = s.accept()
        except Exception, Arg:
            print Arg
            self.restoreGui()
            return

        
        try:
            while self.play:
                box = BytesIO()
                img = ImageGrab.grab()
                img.thumbnail((int(resolution[0]), int(resolution[1])), ImageGrab.Image.ANTIALIAS) # screenshot cutting
                img.save(box, "jpg")
                self.sendBinaryFile(client, box.getvalue())
                
                #box.flush() # dont know
                #box.truncate(0) # dont know
                time.sleep(speed)
            client.close()
        except Exception, Arg:
            print Arg 
            self.restoreGui()
            return

    def test(self):
        self.play = not self.play
        if self.play == True:
            self.top.protocol('WM_DELETE_WINDOW', self.nothing)
            self.start_stop.config(text='Stop', bg="green")
            a=Thread(target=self.do, name = "do")
            a.start()
        if self.play == False:
            self.top.protocol('WM_DELETE_WINDOW', self.exit)
            self.start_stop.config(text='Start', bg="red")

    def do(self): 
        while self.play:
            a= self.parseResolution()
            print a[0], a[1]
            time.sleep(1)


class ScreenTaker():
    def __init__(self):
        self.top = Tk()
        self.top.minsize(width=185, height=100)
        self.top.maxsize(width=185, height=100)
        self.top.title("ScreenshotSender")
        self.top.protocol('WM_DELETE_WINDOW', self.exit)

        self.play = False


        # GUI
        self._ = Label(self.top, text="CLIENT", justify = "center").grid(column = 0, columnspan=2, row = 0)

        self._ = Label(self.top, text="IP Address:", justify = "center").grid(column = 0, row = 1)
        self.iface_box = Entry(self.top, width=14)
        self.iface_box.grid(column = 1, row = 1)

        self._ = Label(self.top, text="Port:", justify = "center").grid(column = 0, row = 2)
        self.port_box = Entry(self.top, width=6)
        self.port_box.grid(column = 1, row = 2)

        self.start_stop = Button(self.top, bg="red",text="Start", relief=RAISED, command = self.run)
        self.start_stop.grid(column = 0, columnspan = 2, row = 5) 

        self.top.mainloop()


    def exit(self):
        self.top.destroy()

    def nothing(self):
        pass


    def restoreGui(self):
        self.play = not self.play
        self.start_stop.config(text='Start', bg="red")
        self.top.protocol('WM_DELETE_WINDOW', self.exit)



    # ------------------------------------------------------------
    def recvAll(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def recvBinaryFile(self, sock):
        lengthbuf = self.recvAll(sock, 4) # receive file size
        length, = struct.unpack('!I', lengthbuf)
        return self.recvAll(sock, length) # receive file
    # -----------------------------------------------------------

    def run(self):
        self.play = not self.play
        if self.play == True: # run screenshots receiving
            self.top.protocol('WM_DELETE_WINDOW', self.nothing)
            self.start_stop.config(text='Stop', bg="green")
            a=Thread(target=self.screenReceiver, name = "Receiver")
            a.start()
        if self.play == False: # stop screenshots receiving
            self.top.protocol('WM_DELETE_WINDOW', self.exit)
            self.start_stop.config(text='Start', bg="red")

    def screenReceiver(self):
        try:
            address = self.iface_box.get()
            port = int(self.port_box.get())
        except Exception, Arg:
            print Arg
            self.restoreGui()
            return

        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((address, port))
        except Exception, Arg:
            print Arg
            self.restoreGui()
            return

        # maximize window
        #plt.switch_backend('TkAgg')
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        try:
            while self.play:
                data = self.recvBinaryFile(s)
                img = ImageGrab.Image.open(BytesIO(data))
                plt.imshow(img)
                plt.draw()
                plt.pause(0.001)
            plt.close()
            s.close()
        except Exception, Arg:
            print Arg 
            self.restoreGui()
            return



if __name__ == "__main__":
    master = Tk()
    master.title("ScreenshotSender")
    master.minsize(width=200, height=90)
    master.maxsize(width=200, height=90)

    mode = 0 # 1 - server, 2 - client

    _ = Label(master, text="Select mode", justify = "center").grid(column = 0, columnspan=2, row = 0)

    server = Button(master, bg="white",text="Server",height=4, width=9, relief=RAISED, command = lambda i=1: pick(i))
    server.grid(column = 0, row = 1)

    client = Button(master, bg="white",text="Client",height=4, width=9, relief=RAISED, command = lambda i=2: pick(i))
    client.grid(column = 1, row = 1)


    def pick(num):
        """
        this functions must be in this place, between initilization of Tk() and mainloop()
        """
        global mode
        mode = num
        master.destroy()

    master.mainloop()

    # forward to selected mode
    if mode==1:
        start = ScreenMaker()
    if mode==2:
        start = ScreenTaker()