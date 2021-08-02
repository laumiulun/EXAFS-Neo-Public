import subprocess
import tkinter

class Console():
    def __init__(self,tkFrame,command):


        self.tkframe = tkFrame
        self.p = subprocess.Popen(command,
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        self.outQueue = queue.Queue()
        self.errQueue = queue.Queue()

        # Tracking the line
        self.line_start = 0
        self.alive = True
        # Create two new threads
        Thread(target=self.readFromProccessOut).start()
        Thread(target=self.readFromProccessErr).start()

        self.writeLoop()

    def writeLoop(self):
        "Used to write data from stdout and stderr to the Text widget"
        # if there is anything to write from stdout or stderr, then write it
        if not self.errQueue.empty():
            self.write(self.errQueue.get())
        if not self.outQueue.empty():
            self.write(self.outQueue.get())

        # run this method again after 10ms
        if self.alive:
            self.tkframe.after(50,self.writeLoop)
        else:
            self.destroy()

    def write(self,string):
        self.tkframe.insert(tk.END, string)
        self.tkframe.see(tk.END)
        self.line_start+=len(string)

    def readFromProccessOut(self):
        "To be executed in a separate thread to make read non-blocking"
        while self.alive:
            data = self.p.stdout.raw.read(1024).decode('utf-8')
            self.outQueue.put(data)

    def readFromProccessErr(self):
        "To be executed in a separate thread to make read non-blocking"
        while self.alive:
            data = self.p.stderr.raw.read(1024).decode('utf-8')
            self.errQueue.put(data)

    def destroy(self):
        "This is the function that is automatically called when the widget is destroyed."
        self.alive=False
        # write exit() to the console in order to stop it running
        # self.p.stdin.write("exit()\n".encode('utf-8'))
        self.p.stdin.flush()
