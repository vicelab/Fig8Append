# TO DO:
# add RTL handling
# add jump handling



import sys
import time
from Tkinter import *
import tkMessageBox
import math


class MissAppendDialog(Frame):

    def __init__(self):
        self.parent = Tk()

        Frame.__init__(self, self.parent)
        self.create_widgets()
        self.parent.mainloop()

    def create_widgets(self):
        DEFAULTrotation = "0"
        self.returnval=[-1, 0]

        self.parent.bind("<Return>", self.enterpressed)
        self.parent.title("Append Fig8 Parameters")
        self.grid()

        l1 = Label(self, text="\nPlease enter by how much you want to rotate the Figure 8 \n(in degrees) ")
        l1.grid(columnspan=10)

        self.rotation = StringVar(self)
        self.rotation.set(DEFAULTrotation)
        self.sb = Spinbox(self, from_=-355, to=355, width = 4, textvariable=self.rotation)
        self.sb.grid( row=0, column= 10, padx=5, pady=5 )

        l2 = Label(self, text="Also place fig 8 at end: ")
        l2.grid(columnspan=10, sticky=W, row=1)

        self.alsoAtEnd = StringVar(self)
        self.alsoAtEnd.set(0)
        self.c = Checkbutton(self, text="", variable=self.alsoAtEnd, onvalue=1, offvalue=0)
        self.c.grid( row=1, column= 10, padx=5, pady=5 )


        self.okbutton = Button(self, text="OK", command=self.ok, state="active", height = 1, width = 8)
        self.okbutton.grid(padx=5, pady=5, sticky=E, column=9, columnspan=2)
        self.okbutton.focus_set()

    def enterpressed (self,event):
        self.ok()

    def ok(self):
        self.returnval[1] = int( self.alsoAtEnd.get() )
        t = self.rotation.get()
        self.returnval[0] = int ( t )
        self.parent.destroy()   # quit this dialog box
        return()


# creates an error dialog with a custom message
def infoDialog(message):
    root = Tk()
    root.withdraw()
    tkMessageBox.showinfo("Info", message)
    root.destroy()


# creates an error dialog with a custom message
def errorDialog(message):
    root = Tk()
    root.withdraw()
    tkMessageBox.showerror("Error", message)
    root.destroy()



# ==================== Main Program ========================
fig8file = 'C:\\Users\\aanderson29\\Documents\\Sliding_Racetrack\\fig8.waypoints'

if len(sys.argv) == 1: # if no parameter given
   errorDialog("You need to drag and drop a Mission Planner \nwaypoint file onto this program!")
   sys.exit()

# open the main dialog
params = MissAppendDialog()
if params.returnval[0] == -1:  # if the dialog box was cancelled
    sys.exit()

sourcefilename = str(sys.argv[1])
#sourcefilename = 'C:\\Users\\aanderson29\\Documents\\Sliding_Racetrack_mod\\level1.txt'
# sourcefilename = 'C:\\Users\\aanderson29\\Documents\\CITRIS\\Missions\\Barn\\barn.waypoints'
rotation = float(params.returnval[0]) * math.pi / 180.0
alsoAtEnd = params.returnval[1]

srcMission = [] # the source file in list form
f8= []          # the figure 8 file in list form


# ==================== Read Data ========================
# read the source file into array srcMission
f = open(sourcefilename, 'r')
for lines in f:
    srcMission.append(lines.split('\t'))
f.close()

# read fig8 file into an array
f = open(fig8file, 'r')
for lines in f:
    f8.append(lines.split('\t'))
f.close()

# ==================== Transform Figure 8 ========================
# get mission home
miss_home = [float(srcMission[1][8]), float(srcMission[1][9])]
# get fig8 home
f8_home = [ float(f8[1][8]), float(f8[1][9]) ]

# subtract the home position from all wpts in f8
for q in range(1, len(f8)):
    if [float(f8[q][8]), float(f8[q][9])] != [0.0,0.0]:                       # if we are dealing with a waypoint
        f8[q][8] = float(f8[q][8]) - f8_home[0]   # subtract the home position from all wpts
        f8[q][9] = float(f8[q][9]) - f8_home[1]   # subtract the home position from all wpts

# calculate latitude compensation factor and compress
lcf = math.cos( f8_home[0] / 180.0 * math.pi )
for q in range(1, len(f8)):
    if [float(f8[q][8]), float(f8[q][9])] != [0.0,0.0]:                       # if we are dealing with a waypoint
        f8[q][9] *= lcf                 # appropriately compress the figure

# ROTATE!
for q in range(1, len(f8)):
    if [float(f8[q][8]), float(f8[q][9])] != [0.0,0.0]:                       # if we are dealing with a waypoint
        newx = math.cos(rotation) * f8[q][9] - math.sin(rotation) * f8[q][8]
        newy = math.sin(rotation) * f8[q][9] + math.cos(rotation) * f8[q][8]
        f8[q][9] = newx
        f8[q][8] = newy

# calculate latitude compensation factor and stretch
lcf = 1.0 / math.cos( miss_home[0] / 180.0 * math.pi )
for q in range(1, len(f8)):
    if [float(f8[q][8]), float(f8[q][9])] != [0.0,0.0]:                       # if we are dealing with a waypoint
        f8[q][9] *= lcf                 # appropriately stretch the figure

# add the new home position to all wpts in f8
for q in range(1, len(f8)):
    if [float(f8[q][8]), float(f8[q][9])] != [0.0,0.0]:                       # if we are dealing with a waypoint
        f8[q][8] = str(float(f8[q][8]) + miss_home[0])   # add the mission home position to all wpts
        f8[q][9] = str(float(f8[q][9]) + miss_home[1])   # add the mission home position to all wpts


# ==================== Combine Missions ========================
# rebuild the first two lines of the original mission( identifier code & home line)
lines = srcMission[0][0] # this is the identifier code
lines = lines + '0'       # this is the line number for home
for v in range(1, len(srcMission[1])):  #add all the other elements of the home line
    lines = lines + '\t' + srcMission[1][v]

counter = 1
# add the fig8 mission
for a in range(2, len(f8)):
    lines = lines + '%d' % counter  # this overwrites the old waypoint number
    counter += 1
    for v in range(1, len(f8[a])):
        lines = lines + '\t' + f8[a][v]

# add the original mission (except for takeoff, which is already taken from fig8)
for a in range(3, len(srcMission)-1):
    lines = lines + '%d' % counter  # this overwrites the old waypoint number
    counter += 1
    for v in range(1, len(srcMission[a])):
        lines = lines + '\t' + srcMission[a][v]

# add another Fig 8 at the end, if needed
if alsoAtEnd:
    for a in range(3, len(f8)):
        lines = lines + '%d' % counter  # this overwrites the old waypoint number
        counter += 1
        for v in range(1, len(f8[a])):
            lines = lines + '\t' + f8[a][v]



# write the result to a file
resfilename = sourcefilename.rsplit('.', 1)
filename = resfilename[0] + "_Fig8.txt"
f = open(filename, "w")
f.write(lines)
f.close()
