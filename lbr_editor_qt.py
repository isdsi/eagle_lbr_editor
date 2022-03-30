import sys
from PyQt5.QtWidgets import *
import xml.etree.ElementTree as elemTree
import os
import shutil

def search(dirname, filter):
    l = list()
    filenames = os.listdir(dirname)
    for filename in filenames:
        full_filename = os.path.join(dirname, filename)
        ext = os.path.splitext(full_filename)[-1]
        if ext.find(filter) != -1:
            l.append(full_filename)
    return l

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(800, 200, 300, 300)

        self.tableWidget = QTableWidget(10, 5)
        self.tableWidget.setHorizontalHeaderLabels(["name"])

        self.pbOpen = QPushButton("Open")
        self.pbOpen.clicked.connect(self.pbOpenClicked)
        self.pbSave = QPushButton("Save")
        self.pbSave.clicked.connect(self.pbSaveClicked)
        self.pbChange = QPushButton("Change")
        self.pbChange.clicked.connect(self.pbChangeClicked)

        topLayOut = QHBoxLayout()
        topLayOut.addWidget(self.pbOpen)
        topLayOut.addWidget(self.pbSave)
        topLayOut.addWidget(self.pbChange)
        self.pbSave.setEnabled(False)
        self.pbChange.setEnabled(False) #

        rightLayOut = QVBoxLayout()
        rightLayOut.addWidget(self.tableWidget)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topLayOut)
        mainLayout.addLayout(rightLayOut)

        self.setLayout(mainLayout)

    def pbOpenClicked(self):
        fname = QFileDialog.getOpenFileName(self, "Open", "", "*.lbr")
        try:
            self.tree = elemTree.parse(fname[0])
        except:
            QMessageBox.information(self, "file open error", "error")
            return
        self.fileName = fname[0]
        self.root = self.tree.getroot()
        self.drawing = self.root.find("./drawing")
        self.library = self.drawing.find("./library")
        self.devicesets = self.library.find("./devicesets")
        
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setRowCount(1)
        r = 0
        for ds in self.devicesets:            
            devices = ds.find("./devices")
            for d in devices:
                rowCount = self.tableWidget.rowCount()
                if rowCount <= r:
                    self.tableWidget.setRowCount(r + 1)
                self.tableWidget.setItem(r, 0, QTableWidgetItem(ds.attrib["name"] + d.attrib["name"]))
                technologies = d.find("./technologies")
                technology = technologies.find("./technology")
                c = 1
                for t in technology:
                    columnCount = self.tableWidget.columnCount()
                    if columnCount <= c:
                        self.tableWidget.setColumnCount(columnCount + 1)
                    self.tableWidget.setItem(r, c, QTableWidgetItem(t.attrib["name"]))
                    c = c + 1
                    if columnCount <= c:
                        self.tableWidget.setColumnCount(columnCount + 1)
                    self.tableWidget.setItem(r, c, QTableWidgetItem(t.attrib["value"]))
                    c = c + 1
                r = r + 1
        if r == 0:
            QMessageBox.information(self, "Couldn't find devices", "error")
        
        # to insert new attributes
        columnCount = self.tableWidget.columnCount()
        if columnCount <= c:
            self.tableWidget.setColumnCount(columnCount + 2)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        self.pbSave.setEnabled(True)                     
        self.pbChange.setEnabled(False) 

    def pbSaveClicked(self):
        #fname = QFileDialog.getOpenFileName(self, "Save", "", "*.lbr")        
        dir = os.path.dirname(self.fileName)
        print(dir)
        base = os.path.basename(self.fileName)
        print(base)
        baseSplit = os.path.splitext(base)
   
        rowCount = self.tableWidget.rowCount()
        for r in range(rowCount):
            deviceName = self.tableWidget.item(r, 0).text()   
            for ds in self.devicesets:            
                devices = ds.find("./devices")
                if ds.attrib["name"] in deviceName:
                    for d in devices:
                        if deviceName == ds.attrib["name"] + d.attrib["name"]:
                            technologies = d.find("./technologies")
                            technology = technologies.find("./technology")
                            c = 1
                            colCount = self.tableWidget.columnCount()
                            for c in range(1, colCount, 2):
                                if self.tableWidget.item(r, c) == None:
                                    break
                                if self.tableWidget.item(r, c + 1) == None:
                                    break
                                name = self.tableWidget.item(r, c).text()
                                value = self.tableWidget.item(r, c + 1).text()
                                for t in technology:
                                    if t.attrib["name"] == name:
                                        t.attrib["value"] = value

        self.outputFileName = dir + "/" + baseSplit[0] + "output" + ".lbr"
        self.tree.write(self.outputFileName, encoding = "utf-8", xml_declaration = True)

        # use for UNIX LF
        WINDOWS_LINE_ENDING = b'\r\n'
        UNIX_LINE_ENDING = b'\n'

        with open(self.outputFileName, 'rb') as open_file:
            content = open_file.read()
            content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
            content = content.replace(b' />', b'/>') # change last space for each line
            content = content.replace(b"<?xml version='1.0' encoding='utf-8'?>", b'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE eagle SYSTEM "eagle.dtd">')
            
        content = content + b'\n'

        with open(self.outputFileName, 'wb') as open_file:
            open_file.write(content)

        self.pbChange.setEnabled(True)
        
    def pbChangeClicked(self):
        #fname = QFileDialog.getOpenFileName(self, "Change", "", "*.lbr")
        #changeFileName = fname[0]
        changeFileName = self.fileName
        dir = os.path.dirname(changeFileName)
        base = os.path.basename(changeFileName)
        baseSplit = os.path.splitext(base)        

        listBackupFile = search(dir, ".l#")
        lastBackupNum = 0
        i = 0
        bfLast = dir + baseSplit[0] + ".l#1"
        for bf in listBackupFile:
            dir = os.path.dirname(bf)
            base = os.path.basename(bf)
            baseSplit = os.path.splitext(base)
            if i > 0:
                shutil.copy(bf, bfLast)
            i = i + 1
            bfLast = bf

        shutil.copy(changeFileName, bfLast)
        shutil.copy(self.outputFileName, changeFileName)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()


