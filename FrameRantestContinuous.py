#! /usr/bin/python

from Tkinter import *
from ttk import Separator
from Rantest import Rantest
from data_screen import Data_Screen
from PlotRandomDist import PlotRandomDist
from ReadRandat import read_Data

__author__="remis"
__date__ ="$27-May-2009 12:45:34$"

class FrameRantestContinuous:
    'GUI for randomisation test'

    def __init__(self, root):
        root.title('DC_PyPs: Randomisation test : continuously variable data.')
        self.createFrame(root)
    

    def createFrame(self, root):
        'Creates main frame and data input field.'
        self.frame = Frame(root)
        self.frame.pack()

        self.frame.config(background="#dcdcdc") #well, it has to be, right?
        
        #self.frame.geometry('600x800')
        message = Message(self.frame, text="\n"+Rantest.introd, justify=LEFT, padx=10, width=500, font=("Helvetica", 12), bg="#dcdcdc")
        message.grid(row=0, column=0, rowspan=6, columnspan=2, sticky=W)

        s = Separator(self.frame, orient=HORIZONTAL)
        s.grid (columnspan=2, sticky=EW)

        Label(self.frame, text="Please select the data source:", justify=LEFT, bg="#dcdcdc").grid(row=15, column=0, padx=10, sticky=W)
        Label(self.frame, text="The calculation will proceed automatically with\n the default number of randomisations (5000).\n\nUse [Repeat Calculation] for more repetitions\n(e.g. to estimate P < 0.001)", font=("Helvetica", 12), justify=LEFT, bg="#dcdcdc").grid(row=15, column=1, rowspan=4, sticky=S)

        self.b1 = Button(self.frame, text="Input data manually", command=self.callback1, highlightbackground="#dcdcdc").grid(row=18, column=0,  sticky=W, padx=30)

        self.b2 = Button(self.frame, text="Generic .txt file", command=self.callback2, highlightbackground="#dcdcdc").grid(row=17, column=0, sticky=W, padx=30)
        

        self.b3 = Button(self.frame, text="Excel Tab-delimited.txt file", command=self.callback3, highlightbackground="#dcdcdc").grid(row=16, column=0,  sticky=W, padx=30)

        Label(self.frame, text="Number of randomisations:", bg="#dcdcdc").grid(row=22, column=0, padx=30, pady=5, sticky=W)
        
        self.e5 = Entry(self.frame, justify=CENTER, width=12, highlightbackground="#dcdcdc")
        self.e5.grid(row=22, column=1, sticky=W, pady=5)
        self.e5.insert(END, '5000')

        self.var1 = IntVar()
        text1="Paired test?"
        self.paired = 0
        # Callback is not triggered if checkbox is never touched
        # Hence self.paired is set to zero above.
        c1=Checkbutton(self.frame, text=text1, variable=self.var1, command=self.callback_paired, bg="#dcdcdc").grid(row=23, column=0, padx=30, pady=5, sticky=W)
        
        self.var2 = IntVar()
        hedges="Calculate confidence intervals for Hedge's g?"
        self.H_CI = 0
        # Callback is not triggered if checkbox is never touched
        # Hence self.H_CI is set to zero above.
        
        c2=Checkbutton(self.frame, text=hedges, variable=self.var2, command=self.callback_hedges, bg="#dcdcdc").grid(row=23, column=1, padx=30, pady=5, sticky=W)


        self.txt = Text(self.frame)
        self.txt.grid(row=25, column=0, columnspan=4, padx=10)
        self.txt.config(width=75, height= 25, font=("Courier", "12"))
        self.txt.insert(END, "Results will appear here")
        
        #both these buttons are ungreyed after results display.
        #Label(self.frame, text="").grid(row=(26), column=0, columnspan=4)
        self.b4 = Button(self.frame, text="Repeat calculation", state=DISABLED,command=self.callback4,highlightbackground="#dcdcdc")
        self.b4.grid(row=27, padx=40, pady=10, column=0, sticky=E)

        self.b5 = Button(self.frame, text="Plot Distribution", state=DISABLED, command=self.callback5,highlightbackground="#dcdcdc")
        self.b5.grid(row=27, padx=40, pady=10, column=1, sticky=W)
    

### NEW BY AP
    def callback_paired(self):
        'Called when ""Paired Test?"" tickbox is checked'
        self.paired = self.var1.get()
        print self.paired

    def callback_hedges(self):
        'Called when ""Hedges CI"" tickbox is checked'

        self.H_CI= self.var2.get()
        print self.H_CI

### end of NEW BY AP

    def callback1(self):
        'Called by GET DATA AND CALCULATE button.'
        self.in_data, self.nran = self.getData()
        
        rntdict = self.getResult(self.in_data, self.nran)
        self.showResult(rntdict)

### NEW BY AP
    def callback2(self):
        'Called by TAKE DATA FROM FILE button'
        self.in_data, self.dfile = read_Data('txt')
        #dfile contains source data path and filename
        self.data_source = 'Data from ' + self.dfile
        
        self.e5.delete(0, END)
        self.e5.insert(END, '5000') #reset to low value
        self.nran = int(self.e5.get())

        rntdict = self.getResult(self.in_data, self.nran)
        self.showResult(rntdict)

    def callback3(self):
        'Called by TAKE DATA FROM excel button'
        self.in_data, self.dfile = read_Data('excel')
        #dfile contains source data path and filename
        self.data_source = 'Data from ' + self.dfile
        
        self.e5.delete(0, END)
        self.e5.insert(END, '5000')     #reset to low value
        self.nran = int(self.e5.get())

        rntdict = self.getResult(self.in_data, self.nran)
        self.showResult(rntdict)

    def callback4(self):
        'Called by REPEAT button'
        #self.indata and self.dfile should already be populated.
        #dfile contains source data path and filename
        
        self.data_source = 'Data from ' + self.dfile
        
        self.nran = int(self.e5.get())
        
        rntdict = self.getResult(self.in_data, self.nran)
        self.showResult(rntdict)

### end of NEW BY AP

    def getData(self):
        'Calls a table to enter data manually.'

### NEW BY AP
        self.data_source = 'Data entered by hand'
### end of NEW BY AP

        from_screen = Data_Screen(self.frame)
        n1 = from_screen.n1
        n2 = from_screen.n2
        dataScreen = from_screen.data
        data1 = dataScreen[0:n1]
        data2 = dataScreen[n1:n1+n2]

        nset = 1    # number of data sets
       # self.paired = 0                    replaced by callback so removed?? AP
       # self.paired = self.var1.get()
        nran = int(self.e5.get())

        in_data = []
        in_data.append(nset)
        for j in range(0, nset):
            in_data.append(n1)
            in_data.append(n2)
            titled = 'Set'
            titlex = 'Sample 1'
            titley = 'Sample 2'
            in_data.append(titled)
            in_data.append(titlex)
            in_data.append(titley)
            in_data.append(data1)
            in_data.append(data2)

        return in_data, nran

    def getResult(self, in_data, nran):
        'Calls rantest to calculate statistics.'

        jset = 1
        rnt = Rantest()
        xobs, yobs = rnt.setContinuousData(in_data, nran, jset, self.paired)
        rnt.tTestContinuous(xobs, yobs, self.paired)
        rnt.doRantestContinuous(xobs, yobs, self.paired, nran)
        #rnt.doRantestContinuous(in_data, nran, jset, self.paired)
        self.randiff = rnt.dict['randiff']

        return rnt.dict

    def showResult(self, rntd):
        'Displays calculation results on main frame.'
        # AP 021209 : many added hard coded tabs ('\t') to ease copy and paste of data
        # First line of output now specifies source file or manual entry

        self.txt.delete(1.0, END)

        self.txt.insert(END,self.data_source+'\n')

        #result1 = (rnt.nx, rnt.ny, rnt.xbar, rnt.ybar, rnt.sdx, rnt.sdy, rnt.sex, rnt.sey)
        self.txt.insert(END, '   n                \t  %(nx)d      \t  %(ny)d \
        \n  Mean       \t %(xbar)f    \t  %(ybar)f \
        \n  s(x), s(y) \t %(sdx)f     \t  %(sdy)f \
        \n  s(x/ybar)  \t %(sex)f     \t  %(sey)f' %rntd)

        if rntd['nx'] == rntd['ny'] and self.paired:
            #result2 = (rnt.dbar, rnt.sdd, rnt.sed)
            self.txt.insert(END, '\n\n Mean difference (dbar) = \t %(dbar)f \
            \n  s(d) = \t %(sdd)f \t s(dbar) = \t %(sed)f' %rntd)

        self.txt.insert(END, '\n\n'+rntd['tPaired'])
        if self.paired:
            #result3 = (rnt.df, rnt.dbar, rnt.sdbar, rnt.tval, rnt.P)
            self.txt.insert(END, '\n  t(%(df)d)= \t %(dbar)f \t / \t%(sdbar)f \t = \t %(tval)f \
            \n  two tail P =\t %(P)f' %rntd)
            self.meanToPlot = rntd['dbar']

        else:
            #result4 = (rnt.dobs, rnt.df, rnt.adiff, rnt.sdiff, rnt.tval, rnt.P)
            self.txt.insert(END, '\n\n Observed difference between means= \t %(dobs)f \
            \n t(%(df)d) = \t %(adiff)f / %(sdiff)f = \t %(tval)f \
            \n two tail P = \t %(P)f' %rntd)
            self.meanToPlot = rntd['dobs']

        #result5 = (nran, rnt.pg1, rnt.pl1, rnt.pa1, rnt.ne1, rnt.pe1, rnt.ne2, rnt.pe2)
        self.txt.insert(END, '\n\n'+rntd['RanPaired'])
        self.txt.insert(END, '\n\n   %(nran)d randomisations \
        \n P values for difference between means are: \
        \n  greater than or equal to observed: P = \t %(pg1)f \
        \n  less than or equal to observed: P = \t %(pl1)f \
        \n  greater than or equal in absolute value to observed: P = \t %(pa1)f \
        \n  Number equal to observed = %(ne1)d (P= %(pe1)f) \
        \n  Number equal in absolute value to observed = %(ne2)d (P= %(pe2)f)' %rntd)

        self.b4.config(state=NORMAL)        # results have been calculated so recalculate and plot distribution buttons become available
        self.b5.config(state=NORMAL)

    def callback5(self):
        'Called by PLOT DISTRIBUTION button.'
        PlotRandomDist(self.randiff, self.paired,0,1, self.meanToPlot)



if __name__ == "__main__":
    root=Tk()

    frc = FrameRantestContinuous(root)
    root.mainloop()
