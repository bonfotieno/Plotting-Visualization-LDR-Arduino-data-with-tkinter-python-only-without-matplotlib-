# Developer: Bonface Otieno; bonnyotieno9@gmail.com

from tkinter import *
import threading
from serial import Serial, serialutil
from collections import deque
from time import sleep


class HandleData(object):
    def __init__(self):
        self.arduinoData = 0
        self.dataQue = deque()
        self.poppedData = 0

    def set_data(self):
        global stopFlag
        while stopFlag is False:
            try:
                self.arduinoData = (serial.readline().decode('ascii')).strip("\r\n")
                self.arduinoData = (int(
                    self.arduinoData)) // 2.56  # divided by 2.56 to constrain the graph inside the plane(within the canvas)
                self.dataQue.append(self.arduinoData)
            except NameError:
                print("arduino was disconnected")

    def get_data(self):
        """
            this is a pretty function
            it makes sure that only one value is popped from the queue and used by the two threads;
            -show_graph() in both LeftChart and RightChart classes
        """
        global getData_flag
        if getData_flag:
            while True:
                if len(self.dataQue) > 0:
                    self.poppedData = self.dataQue.pop()
                    break
            return self.poppedData
        else:
            return self.poppedData


class LeftChart(Frame):
    """ visualize data in real time """
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.plane = Canvas(self, width=600, height=500, bg='#f9f9f9', highlightthickness=0)
        self.plane.pack()
        self.voltagelabels = []
        self.H_lines = 50
        self.V_lines = 50

    # the functions create_horizontal_lines() and create_vertical_lines() are for building the cartesian plane for plotting
    def create_horizontal_lines(self):
        """to create the horizontal lines on the plane at spacing of 5 pixels also the left green dot"""
        voltageLabelContent = 5
        while self.V_lines <= 450:
            if (self.V_lines + 30) % 80 == 0:
                self.plane.create_line(45, self.V_lines, 555, self.V_lines, fill='#80cbc4')
                self.voltagelabels.append(
                    self.plane.create_text(37, self.V_lines, text='{}v'.format(voltageLabelContent),
                                           font=('Calibri', 8),
                                           fill='#a20202'))
                self.voltagelabels.append(
                    self.plane.create_text(562, self.V_lines, text='{}v'.format(voltageLabelContent),
                                           font=('Calibri', 8),
                                           fill='#a20202'))
                voltageLabelContent -= 1
            else:
                self.plane.create_line(50, self.V_lines, 550, self.V_lines, fill='#86f9a6')
            self.V_lines += 5

    def create_vertical_lines(self):
        """to create the vertical lines on the plane at spacing of 5 pixels place this plane'serial text label"""
        self.plane.create_text(310, 11, text="Real time Data flow Visualization", font='Calibri 12 underline')
        while self.H_lines <= 550:
            if (self.H_lines + 50) % 100 == 0:
                self.plane.create_line(self.H_lines, 45, self.H_lines, 455, fill='#80cbc4')
            else:
                self.plane.create_line(self.H_lines, 50, self.H_lines, 450, fill='#86f9a6')
            self.H_lines += 5

    def show_graph(self):
        global stopFlag
        # note that most of the numbers here(like 450,54,550) represent pixels' positions in the canvas(plane).
        xDataPoint = 54
        lock.acquire()
        coords = [50, 450 - dt.get_data(), 50, 450 - dt.get_data()]  # initializing coords
        lock.release()
        # using two lines here to enable anti-aliasing feature in the displayed line graph
        line1 = self.plane.create_line(coords, fill='#AAA', width=1.8, tags='thickLine')
        line = self.plane.create_line(coords, fill='#000', width=1.3, tags='thinLine')
        while stopFlag is False:
            self.parent.update()
            lock.acquire()
            yDataPoint = 450 - dt.get_data()
            lock.release()
            if xDataPoint <= 550:  # checks if the line has reached the edge of the plane
                coords.extend((xDataPoint, yDataPoint))  # adds more data points hence increasing line(line graph) length
                xDataPoint += 4  # each plotted yDataPoint is 4 pixel far from the previous
            else:
                yIndex = 1  # helps in indexing only y values in the coords list
                while True:  # this block is responsible moving y values(yDataPoints) to the left of the list(coords) through swapping
                    coords[yIndex] = coords[
                        yIndex + 2]  # yDataPoints are swapped to the left therefore replacing the previous ones
                    yIndex += 2
                    if yIndex >= 253:  # 253 here is per the reference of indexes of all values in coords, it should 250 but due the values added before the loop its 253; that'serial a length of 254
                        coords[253] = yDataPoint
                        break
            self.plane.coords(line1, coords)
            self.plane.coords(line, coords)


class RightChart(Frame):
    """ visualizes data in condensed form at an interval of 1  second"""
    def __init__(self, parent):
        self.parent = parent
        Frame.__init__(self, self.parent)
        self.plane = Canvas(self, width=600, height=500, bg='#f9f9f9', highlightthickness=0)
        self.plane.pack()
        self.H_lines = 50
        self.V_lines = 50
        self.voltagelabels = []

    def create_horizontal_lines(self):
        """to create the horizontal lines on the plane at spacing of 5 pixels also the left red dot"""
        voltageLabelContent = 5
        while self.V_lines <= 450:
            if (self.V_lines + 30) % 80 == 0:
                self.plane.create_line(45, self.V_lines, 555, self.V_lines, fill='#80cbc4')
                self.voltagelabels.append(
                    self.plane.create_text(37, self.V_lines, text='{}v'.format(voltageLabelContent),
                                           font=('Calibri', 8),
                                           fill='#a20202'))
                self.voltagelabels.append(
                    self.plane.create_text(562, self.V_lines, text='{}v'.format(voltageLabelContent),
                                           font=('Calibri', 8),
                                           fill='#a20202'))
                voltageLabelContent -= 1
            else:
                self.plane.create_line(50, self.V_lines, 550, self.V_lines, fill='#86f9a6')
            self.V_lines += 5

    def create_vertical_lines(self):
        """to create the vertical lines on the plane at spacing of 5 pixels place this plane'serial text label"""
        self.plane.create_text(310, 11, text="Condensed at 1 second interval", font='Calibri 12 underline')
        while self.H_lines <= 550:
            if (self.H_lines + 50) % 100 == 0:
                self.plane.create_line(self.H_lines, 45, self.H_lines, 455, fill='#80cbc4')
            else:
                self.plane.create_line(self.H_lines, 50, self.H_lines, 450, fill='#86f9a6')
            self.H_lines += 5

    def show_graph(self):
        # note that most of the numbers here(like 450,54,550) represent pixels' positions in the canvas(plane).
        global stopFlag, getData_flag
        getData_flag = False
        lock.acquire()
        coords = [50, 450 - dt.get_data(), 50, 450 - dt.get_data()]
        getData_flag = True
        lock.release()
        xDataPoint = 54
        xIncrement = 4
        line1 = self.plane.create_line(coords, fill='#AAA', width=1.8)
        line = self.plane.create_line(coords, fill='#000', width=1.3)
        while stopFlag is False:
            sleep(1)
            getData_flag = False
            lock.acquire()
            yDataPoint = 450 - dt.get_data()
            getData_flag = True
            lock.release()
            if xDataPoint <= 550:  # checks if the line has reached the edge of the plane
                coords.extend((xDataPoint, yDataPoint))
                xDataPoint += xIncrement  # each plotted yDataPoint is 4 pixel far from the previous
            else:
                # this else block is the one which shrinks the line graph to fit in the canvas(plane)
                # ((len(coords) - 4) / 2) is for getting the number of data points. I subtracted -4 to get rid of the first four which all represent data point at index 0
                new_xIncrement = round(450 / ((len(coords) - 4) / 2), 5)  # I get 450 here by subtracting 50 from the length of plotting area which is 500
                multiplier = 1
                xIndex = 4
                while xIndex <= (len(coords)-2):  # minus 2 to index last xDataPoint
                    # when coords grow bigger(like 100,000 data points) the algorithm inside this loop might be slow depending on your machine, I recommend you use multiprocessing or redesign this to be efficient
                    coords[xIndex] = coords[xIndex]-((xIncrement-new_xIncrement)*multiplier)  # to make sure all xDataPoint values are at interval of new_xIncrement
                    xIndex += 2
                    multiplier += 1
                xDataPoint = coords[len(coords)-2]
                xIncrement = new_xIncrement
            self.plane.coords(line1, coords)
            self.plane.coords(line, coords)


def start():
    global stopFlag
    start.config(bg="#e1f6ff", state=DISABLED)
    stopFlag = False
    serial.flushInput()
    serial.write(b'GET')
    t5 = threading.Thread(target=dt.set_data)
    t6 = threading.Thread(target=L.show_graph)
    t7 = threading.Thread(target=R.show_graph)
    t5.start(); t6.start(); t7.start()

    
if __name__ == "__main__":
    try:
        serial = Serial('COM3', baudrate=9600, timeout=1)  # make sure to change the port to which your arduino is connected
    except serialutil.SerialException:
        print("Arduino wasn't detected")
    stopFlag = False  # stopFlag is unused here you can use it to stop the running 
    getData_flag = True
    lock = threading.Lock()
    dt = HandleData()
    root = Tk()
    root.title("BOTIEN")
    root.config(bg="#fdfdfd")
    root.geometry("+2+2")
    root.minsize(1280, 550)
    L = LeftChart(root)
    R = RightChart(root)
    buttonFrames = Frame(bg="#f9f9f9")
    t1 = threading.Thread(target=L.create_vertical_lines)
    t2 = threading.Thread(target=L.create_horizontal_lines)
    t3 = threading.Thread(target=R.create_vertical_lines)
    t4 = threading.Thread(target=R.create_horizontal_lines)
    t1.start(); t3.start(); t2.start(); t4.start()
    L.grid(row=0, column=0, padx=(20, 0), pady=10)
    R.grid(row=0, column=1, padx=20, pady=10)
    buttonFrames.grid(row=1, column=0, columnspan=2, padx=20)
    start = Button(buttonFrames, text="START", bg="#b3e8ff", command=start, relief=FLAT, borderwidth=0)
    start.grid(row=0, column=1, padx=20, ipadx=60)
    root.mainloop()
