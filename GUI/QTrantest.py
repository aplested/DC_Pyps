#! /usr/bin/python
import os
import sys
import socket
import datetime
import pandas as pd
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from dcstats import helpers
from dcstats import dataIO
from dcstats.fieller import Fieller
import dcstats.rantest as rantest
from dcstats.basic_stats import TTestBinomial

__author__="remis"
__date__ ="$03-Jan-2010 15:26:00$"


class RantestQT(QDialog):
    def __init__(self, parent=None):
        super(RantestQT, self).__init__(parent)
        self.setWindowTitle("DC_PyPs: Statistics")

        main_box = QHBoxLayout()
        # Left side: Result text box
        self.results = ResultBox()
        main_box.addWidget(self.results)       
        # Right side: controls and plot
        right_box = QVBoxLayout()
        main_box.addLayout(right_box)
        self.setLayout(main_box)
        

        ####### Tabs ##########
        tab_widget = QTabWidget()
        tab_widget.addTab(RandomisationContTab(self.results), "Rantest: continuous")
        tab_widget.addTab(RandomisationBinTab(self.results), "Rantest: binary")

        tab4 = QWidget()
        tab_widget.addTab(tab4, "Fieller")
        self.fieller_layout(QVBoxLayout(tab4))

        ##### Finalise main window ######
        tab_widget.setFixedWidth(600)
        right_box.addWidget(tab_widget)
        right_box.addWidget(WelcomeScreen())

        quitButton = QPushButton("&QUIT")
        quitButton.clicked.connect(self.close)
        right_box.addLayout(single_button(quitButton))       

#######   TAB 4: FIELLER. START  #############
    def fieller_layout(self, tab_layout):
        'Prepare layout for Tab 4. Fieller theorema.'
        grid = QGridLayout()
        grid.addWidget(QLabel("Nominator:"), 0, 0)
        grid.addWidget(QLabel("SD of Nominator:"), 1, 0)
        grid.addWidget(QLabel("Denominator:"), 2, 0)
        grid.addWidget(QLabel("SD of Denominator:"), 3, 0)
        grid.addWidget(QLabel("Correlation coefficient (nom,denom):"), 4, 0)
        grid.addWidget(QLabel("Alpha:"), 5, 0)
        grid.addWidget(QLabel("Total number of observations (Na + Nb):"), 6, 0)
        self.tb4e1 = QLineEdit("14")
        grid.addWidget(self.tb4e1, 0, 1)
        self.tb4e2 = QLineEdit("3")
        grid.addWidget(self.tb4e2, 1, 1)
        self.tb4e3 = QLineEdit("7")
        grid.addWidget(self.tb4e3, 2, 1)
        self.tb4e4 = QLineEdit("2")
        grid.addWidget(self.tb4e4, 3, 1)
        self.tb4e5 = QLineEdit("0")
        grid.addWidget(self.tb4e5, 4, 1)
        self.tb4e6 = QLineEdit("0.05")
        grid.addWidget(self.tb4e6, 5, 1)
        self.tb4e7 = QLineEdit("12")
        grid.addWidget(self.tb4e7, 6, 1)
        tab_layout.addLayout(grid)

        self.tb4b1 = QPushButton("Calculate SD and confidence limits for a ratio")
        tab_layout.addLayout(self.single_button(self.tb4b1))
        self.tb4b1.clicked.connect(self.callback2)       
        return tab_layout

    def callback2(self):
        'Called by CALCULATE button in Tab4.'
        a = float(self.tb4e1.text())
        b = float(self.tb4e3.text())
        sa = float(self.tb4e2.text())
        sb = float(self.tb4e4.text())
        r = float(self.tb4e5.text())
        alpha = float(self.tb4e6.text())
        Ntot = float(self.tb4e7.text())
        #Call Fieller to calculate statistics.
        flr = Fieller(a, b, sa, sb, r, alpha, Ntot)
        self.results.append(str(flr))
#######   TAB 4: FIELLER. END  #############

    def single_button(self, bt):
        b_layout = QHBoxLayout()
        b_layout.addStretch()
        b_layout.addWidget(bt)
        b_layout.addStretch()
        return b_layout


class RandomisationBinTab(QWidget):
    def __init__(self, log, parent=None):
        QWidget.__init__(self, parent)
        layout = QVBoxLayout(self)
        self.log = log
        layout.addWidget(QLabel(rantest.RTINTROD))
        self.nran = 5000

        layout.addWidget(QLabel("Sample 1"))
        layout1 = QHBoxLayout()
        layout1.addWidget(QLabel("Successes:"))
        self.ed1 = QLineEdit("3")
        layout1.addWidget(self.ed1)
        layout1.addWidget(QLabel("Failures:"))
        self.ed2 = QLineEdit("4")
        layout1.addWidget(self.ed2)
        layout1.addStretch()
        layout.addLayout(layout1)

        layout.addWidget(QLabel("Sample 2"))
        layout2 = QHBoxLayout()
        layout2.addWidget(QLabel("Successes:"))
        self.ed3 = QLineEdit("4")
        layout2.addWidget(self.ed3)
        layout2.addWidget(QLabel("Failures:"))
        self.ed4 = QLineEdit("5")
        layout2.addWidget(self.ed4)
        layout2.addStretch()
        layout.addLayout(layout2)

        layout3 = QHBoxLayout()
        layout3.addWidget(QLabel("Number of randomisations:"))
        self.ed5 = QLineEdit("5000")
        layout3.addWidget(self.ed5)
        layout3.addStretch()
        layout.addLayout(layout3)
        
        self.bt1 = QPushButton("Calculate")
        layout.addLayout(single_button(self.bt1))
        self.bt1.clicked.connect(self.run_rantest_bin)

    def run_rantest_bin(self):
        """Called by button CALCULATE."""
        ir1 = int(self.ed1.text())
        if1 = int(self.ed2.text())
        ir2 = int(self.ed3.text())
        if2 = int(self.ed4.text())
        self.nran = int(self.ed5.text())
        self.log.append(helpers.calculate_rantest_binary(
            self.nran, ir1, if1, ir2, if2))


class RandomisationContTab(QWidget):
    def __init__(self, log, parent=None):
        QWidget.__init__(self, parent)
        layout = QVBoxLayout(self)
        self.log = log
        layout.addWidget(QLabel(rantest.RTINTROD))

        self.nran = 5000
        self.paired = 0
        self.path = ""

        bt1 = QPushButton("Get data from Excel file")
        layout.addLayout(single_button(bt1))
        layout1 = QHBoxLayout()
        layout1.addWidget(QLabel("Number of randomisations:"))
        self.ed1 = QLineEdit(str(self.nran))
        layout1.addWidget(self.ed1)
        self.ch1 = QCheckBox("&Paired test?")
        layout1.addWidget(self.ch1)
        layout.addLayout(layout1)
        bt2 = QPushButton("Run randomisation test")
        layout.addLayout(single_button(bt2))

        self.ed1.editingFinished.connect(self.ran_changed)
        self.ch1.stateChanged.connect(self.ran_changed)
        bt1.clicked.connect(self.open_file)
        bt2.clicked.connect(self.run_rantest)

    def ran_changed(self):
        if self.ch1.isChecked():
            self.paired = 1
        else:
            self.paired = 0
        self.nran = int(self.ed1.text()) 

    def open_file(self):
        """Called by TAKE DATA FROM FILE button in Tab2"""
        try:
            self.filename, filt = QFileDialog.getOpenFileName(self,
                "Open Data File...", self.path, "MS Excel Files (*.xlsx)")
            self.path = os.path.split(str(self.filename))[0]
            #TODO: allow loading from other format files
            self.X, self.Y = load_two_samples_from_excel_with_pandas(self.filename)
            self.get_basic_statistics()
        except:
            pass

    def get_basic_statistics(self):
        # Display basic statistics
        self.log.append('\nData loaded from a file: ' + self.filename + '\n')
        self.log.append(helpers.calculate_ttest_hedges(self.X, self.Y, self.paired))

    def run_rantest(self):
        """Called by RUN TEST button in Tab2."""
        self.log.append(helpers.calculate_rantest_continuous(
            self.nran, self.X, self.Y, self.paired))



class WelcomeScreen(QWidget):
    """"""
    def __init__(self, parent=None):
        super(WelcomeScreen, self).__init__(parent)

        #plot_area = QWidget()
        self.setFixedHeight(400)
        self.setStyleSheet("QWidget { background-color: %s }"% "white")
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("<p align=center><b>Welcome to DC_PyPs: "
            "Statistics!</b></p>"))
        self.layout.addWidget(self.movie_screen())
        self.layout.addWidget(QLabel("<p align=center><b>To continue select a "
        "statistical test from visible tabs.</b></p>"))
        #tab_widget.addTab(plot_area, "Wellcome!")

    def movie_screen(self):
        """Set up the gif movie screen."""
        movie_screen = QLabel()
        # expand and center the label
        movie_screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        movie_screen.setAlignment(Qt.AlignCenter)
        movie = QMovie("GUI/dca2.gif", QByteArray(), self)
        movie.setCacheMode(QMovie.CacheAll)
        movie.setSpeed(100)
        movie_screen.setMovie(movie)
        movie.start()
        return movie_screen

class ExcelSheetDlg(QDialog):
    """
    Dialog to choose Excel sheet to load.
    """
    def __init__(self, sheetlist, parent=None):
        super(ExcelSheetDlg, self).__init__(parent)
        self.sheet = ''
        self.List = QListWidget()
        self.List.addItems(sheetlist)
        self.List.itemSelectionChanged.connect(self.sheetSelected)
        layout1 = QHBoxLayout()
        layout1.addWidget(self.List)
        layout2 = QVBoxLayout()
        layout2.addLayout(layout1)
        layout2.addWidget(ok_cancel_button(self))
        self.setLayout(layout2)
        self.resize(200, 300)
        self.setWindowTitle("Choose Excel sheet to load...")

    def sheetSelected(self):
        """
        Get selected sheet name.
        """
        self.sheet = self.List.currentRow()

    def returnSheet(self):
        """
        Return selected sheet name.
        """
        return self.sheet

class ResultBox(QTextBrowser):
    def __init__(self, parent=None):
        super(ResultBox, self).__init__(parent)
        self.setFixedWidth(500)
        self.append("DC-stats")
        self.append(sys.version)
        self.append("Date and time of analysis: " + str(datetime.datetime.now())[:19])
        self.append("Machine: {0};   System: {1}".format(socket.gethostname(), sys.platform))

def ok_cancel_button(parent):
    buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
    buttonBox.button(QDialogButtonBox.Ok).setDefault(True)
    buttonBox.accepted.connect(parent.accept)
    buttonBox.rejected.connect(parent.reject)
    return buttonBox

def single_button(bt):
    b_layout = QHBoxLayout()
    b_layout.addStretch()
    b_layout.addWidget(bt)
    b_layout.addStretch()
    return b_layout

def load_two_samples_from_excel_with_pandas(filename):
    #TODO: currently loads only firs two columns. Allow multiple column load.
    # TODO: consider moving out of this class
    xl = pd.ExcelFile(filename)
    dialog = ExcelSheetDlg(xl.sheet_names) #self
    if dialog.exec_():
        xlssheet = dialog.returnSheet()
    dt = xl.parse(xlssheet)
    X = dt.iloc[:,0].dropna().values.tolist()
    Y = dt.iloc[:,1].dropna().values.tolist()
    return X, Y
