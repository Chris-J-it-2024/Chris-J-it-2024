from operator import truediv
from urllib import request
from PyQt5 import QtWidgets, uic, QtGui, QtCore

from subprocess import Popen, PIPE, check_call, CalledProcessError
import subprocess
import os
import numpy as np
from numpy import asarray
from numpy import savetxt,loadtxt
import pandas as pd
from pathlib import Path
from os.path import exists
import sqlite3
from datetime import datetime
import socket
import time
import sys
import csv

rootPath=str(Path(__file__).parent)+'/'
sendNumberOfSMS=4
waitSendSMS=15

ltesearch = "/home/kk/workarea/srsRAN/build/lib/examples/cell_search"
gsmsearch = "grgsm_scanner"

lteue = "/home/kk/workarea/srsRAN/build/srsue/src/srsue"
lteue_conf = "/home/kk/workarea/srsRAN/srsue/ue.conf.example"
sms_socket = "192.168.1.5"
pnumber = "+44"

# srsRAN/lib/src/phy/rf/rf_uhd_imp.c.1033: Error timed out while receiving samples from UHD.

ltesearch = "/home/user/workarea/srsRAN/build/lib/examples/cell_search"
gsmsearch = "grgsm_scanner"

lteue = "/home/user/workarea/srsRAN/build/srsue/src/srsue"
# 11 lteue = "/home/user/workarea/srsRAN/cmake-build-debug/srsue/src/srsue"
lteue_conf = "/home/user/workarea/srsRAN/srsue/ue.conf.example"
sms_socket = "192.168.1.5"
pnumber = "+44"


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('spy.ui', self)
        cells1 = []
        cells_gsm = []
        telecomOper=['All']
        

        self.df =pd.read_csv(rootPath + 'mcc-mnc-table.csv')
        for n in self.df.values:            
            if str(n[5]) + ' ' + str(n[7]) not in telecomOper:
                telecomOper.append(n[5]+' '+str(n[7]))


        files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.csv') and f.startswith('mcc-mnc-table') == False]
        locs=['Current']
        for f in files:        
              nf=f.replace('ltecells-','')
              nf=nf.replace('.csv','')
              nf=nf.replace('gsmcells-','')
              nf=nf.replace('.csv','')
              if not nf in locs:
                if (nf!='ltecells' and nf!='gsmcells'):
                    locs.append(nf)


        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton') # Find the button
        self.button.clicked.connect(self.getTowersPressed) # Remember to pass the definition/method, not the return value!        

        self.button1 = self.findChild(QtWidgets.QPushButton, 'pushButton_2') # Find the button
        self.button1.clicked.connect(self.getTmsi) # Remember to pass the definition/method, not the return value!        

        self.button3 = self.findChild(QtWidgets.QPushButton, 'pushButton_3') # Find the button
        self.button3.clicked.connect(self.recordGsm) # Remember to pass the definition/method, not the return value!        

        self.button4 = self.findChild(QtWidgets.QPushButton, 'pushButton_4') # Find the button
        self.button4.clicked.connect(self.decodeGsm) # Remember to pass the definition/method, not the return value!        

        self.button5 = self.findChild(QtWidgets.QPushButton, 'pushButton_5') # Find the button
        self.button5.clicked.connect(self.setupLTE) # Remember to pass the definition/method, not the return value!        

        self.button6 = self.findChild(QtWidgets.QPushButton, 'pushButton_6') # Find the button
        self.button6.clicked.connect(self.newLocation) # Remember to pass the definition/method, not the return value!        


        self.button7 = self.findChild(QtWidgets.QPushButton, 'pushButton_7') # Find the button
        self.button7.clicked.connect(self.getTmsiOne) # Remember to pass the definition/method, not the return value!        

        self.combo = self.findChild(QtWidgets.QComboBox, 'comboBox') # Find the button
        self.combo.addItems(locs)

        self.combo2 = self.findChild(QtWidgets.QComboBox, 'comboBox_2') # Find the button
        self.combo2.addItems(telecomOper)

        self.button9 = self.findChild(QtWidgets.QPushButton, 'pushButton_9') # Find the button
        self.button9.clicked.connect(self.saveNumbers) # Remember to pass the definition/method, not the return value!        

        self.button10 = self.findChild(QtWidgets.QPushButton, 'pushButton_10') # Find the button
        self.button10.clicked.connect(self.getOperators) # Remember to pass the definition/method, not the return value!        

        self.checkbox1 = self.findChild(QtWidgets.QCheckBox, 'checkBox') # Find the button

        if (os.path.isfile('./spy.ini')==True):            
                file1 = open("spy.ini","r")                
                t1=file1.readline().replace('\n','')
                t2=file1.readline().replace('\n','')
                
                t3=file1.readline().replace('\n','')
                t4=file1.readline().replace('\n','')
                t5=file1.readline().replace('\n','')                
                t6=file1.readline().replace('\n','')
                
                file1.close() #to change file access modes
                self.findChild(QtWidgets.QLineEdit, 'lineEdit').setText(t1)
                self.findChild(QtWidgets.QLineEdit, 'lineEdit_2').setText(t2)
                self.findChild(QtWidgets.QLineEdit, 'lineEdit_20').setText(t3)
                self.findChild(QtWidgets.QLineEdit, 'lineEdit_21').setText(t4)
                self.findChild(QtWidgets.QLineEdit, 'lineEdit_22').setText(t5)
                self.findChild(QtWidgets.QLineEdit, 'lineEdit_23').setText(t6)                

        self.show()


    def getOperators(self):
        self.cells1 =loadtxt(rootPath + 'ltecells.csv', delimiter=',')
        self.getLTECNS()


    def saveNumbers(self):        
        sms_socket = self.findChild(QtWidgets.QLineEdit, 'lineEdit').text()
        pnumber = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2').text()
        sms_socket1 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_20').text()
        sms_socket2 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_21').text()
        sms_socket3 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_22').text()
        sms_socket4 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_23').text()
                        
        file1 = open("spy.ini","w")
        L = [sms_socket + '\n',pnumber + '\n']
        file1.write(sms_socket+'\n')
        file1.write(pnumber+'\n')
        file1.write(sms_socket1+'\n')
        file1.write(sms_socket2+'\n')
        file1.write(sms_socket3+'\n')
        file1.write(sms_socket4+'\n')        
        file1.close() #to change file access modes




    def testSMS(self):
        pnumber = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2').text()        
        sms_socket = self.findChild(QtWidgets.QLineEdit, 'lineEdit').text()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = sms_socket
        port =1339
        s.connect((host,port))
        self.plainTextEdit.insertPlainText("1. Sending SMS to " + pnumber + "\n")
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        self.silentSMS(s,pnumber)
        

    def newLocation(self):
        filename1 = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename1 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_9').text()
        if (os.path.isfile('./ltecells.csv')==True):            
            os.rename('./ltecells.csv','./ltecells-'+filename1+'.csv')
        
        if (os.path.isfile('./gsmcells.csv')==True):            
            os.rename('./gsmcells.csv','./gsmcells-'+filename1+'.csv')
        

    def setupLTE(self):        
        subprocess.call([ltesearch,'-b', '87'])

    def decodeGsm(self):
        frq = self.findChild(QtWidgets.QLineEdit, 'lineEdit_3').text()
        # sudo wireshark -k -f udp -Y gsmtap -i lo        
        subprocess.call(['grgsm_decode', '-c', '/tmp/testout' , '-f', frq,'-s','1e6', '-m' , 'BCCH', '-t', '0'])
        # tshark -T fields -n -r /tmp/testout1.pcap -E separator=/t -e gsm_a.tmsi  > /tmp/capture1.csv

    def recordGsm(self):
        frq = self.findChild(QtWidgets.QLineEdit, 'lineEdit_3').text()
        tm = self.findChild(QtWidgets.QLineEdit, 'lineEdit_4').text()
        self.plainTextEdit.insertPlainText("Started recording to file  /tmp/testout\n")
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        a_child_process = subprocess.call(['grgsm_capture', '-f', frq , '-s', '1e6' , '-g' , '90', '/tmp/testout', '-T', tm])
        # time.sleep(int(tm)+5)
        self.plainTextEdit.insertPlainText("Recording finished. Saved in file /tmp/testout\n")
        
    def getGsmFreq(self, cn):
        frq=0
        for r in self.cells_gsm:
            nm=(r[4]*100+r[5])
            #print(str(int(nm)))            
            if (str(int(nm)) == str(cn)):
                #print(r[1])
                frq=r[1]
        return frq*1000000

    def getTowersPressed(self):
        l=self.combo.currentText()
        if (l=='Current'):
            l=''
        else:
            l='-'+l;
        if (exists(rootPath + 'ltecells'+l+'.csv') == False):
            self.plainTextEdit.insertPlainText("Finding LTE cells ...\n")
            QtWidgets.QApplication.processEvents()
            QtWidgets.QApplication.processEvents()
            QtWidgets.QApplication.processEvents()
            # self.cells1 = self.execlte([ltesearch, "-b","20"])
            self.cells1 = self.execlte1([ltesearch, "-b","20"])
            self.cells1 = asarray(self.cells1)    
            savetxt(rootPath + 'ltecells.csv', self.cells1, delimiter=',')
            self.getLTECNS()
        else:
            self.cells1 =loadtxt(rootPath + 'ltecells'+l+'.csv', delimiter=',')


        if (exists(rootPath + 'gsmcells'+l+'.csv') == False):
            self.plainTextEdit.insertPlainText("Finding GSM cells ...\n")
            QtWidgets.QApplication.processEvents()
            QtWidgets.QApplication.processEvents()
            QtWidgets.QApplication.processEvents()
            # self.cells_gsm = self.execgsm([gsmsearch, "-b","DCS1800","-g","50","-v"])
            self.cells_gsm = self.execgsm1([gsmsearch, "-b","DCS1800","-g","50","-v"])
            self.cells_gsm = asarray(self.cells_gsm)    
            savetxt(rootPath + 'gsmcells.csv', self.cells_gsm, delimiter=',')
        else:
            self.cells_gsm =loadtxt(rootPath + 'gsmcells'+l+'.csv', delimiter=',')


        self.plainTextEdit.insertPlainText("LTE Cells\n")
        for r in self.cells1:
            self.plainTextEdit.insertPlainText("F: " + str(r[1]).replace('.0','') + ", ")
        self.plainTextEdit.insertPlainText("\n")
        self.plainTextEdit.insertPlainText("GSM Cells\n")
        for r in self.cells_gsm:
            self.plainTextEdit.insertPlainText("F: " + str(r[1]).replace('','')+ ", ")
        self.plainTextEdit.insertPlainText("\n")

    def silentSMS(self, s, str):        
        str=str+"\n"
        s.send(str.encode()) 
        data = ''
        data = s.recv(1024).decode()
        print (data)

    def getTmsiGsm(self):
        self.getTowersPressed()
        print(self.cells1)
        print(self.cells_gsm)
        sms_socket = self.findChild(QtWidgets.QLineEdit, 'lineEdit').text()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = sms_socket
        port =1339
        s.connect((host,port))
        for i in range(1,sendNumberOfSMS+1):
                self.plainTextEdit.insertPlainText("1. Sending SMS Freq: " + str(i) + "\n")
                QtWidgets.QApplication.processEvents()
                QtWidgets.QApplication.processEvents()
                QtWidgets.QApplication.processEvents()
                self.silentSMS(s,pnumber)
                time.sleep(waitSendSMS)
        self.silentSMS(s,"exit")
        time.sleep(5)            


    def getLTECNS(self):
        # self.getTowersPressed()
        for cl in self.cells1:
                frq=str(int(cl[1]))
                print(frq)
                self.setFreq(frq)
                self.plainTextEdit.insertPlainText("1st Pass Freq:" + str(frq) + "\n")
                QtWidgets.QApplication.processEvents()
                QtWidgets.QApplication.processEvents()
                QtWidgets.QApplication.processEvents()
                a_child_process = subprocess.Popen([lteue, lteue_conf+'1'])    
                time.sleep(10)
                a_child_process.terminate()
                time.sleep(3)
                cn,rw=self.getCandidates1(sendNumberOfSMS)
                cl[6]=cn
                self.plainTextEdit.insertPlainText("Cell No:" + str(cn) + "\n")
        savetxt(rootPath + 'ltecells.csv', self.cells1, delimiter=',')
            





    def getTmsi(self):        
        sendNumberOfSMS=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_6').text())
        waitSendSMS=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_7').text())
        waitSendSMS1=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_11').text())
        waitSendSMS2=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_12').text())
        waitSendSMS3=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_13').text())
        waitSendSMS4=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_14').text())        
        waitSendSMS5=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_15').text())        
        waitSendSMS6=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_16').text())
        waitSendSMS7=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_17').text())
        waitSendSMS8=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_18').text())
        waitSendSMS9=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_19').text())
        
        self.getTowersPressed()
        print(self.cells1)
        print(self.cells_gsm)
        currentOperator=self.combo2.currentText()
        socCC=0;    
        if (self.checkbox1.isChecked() == False):
            sms_socket = self.findChild(QtWidgets.QLineEdit, 'lineEdit').text()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = sms_socket
            port =1339
            s.connect((host,port))

            socCC=1
            sms_socket1 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_20').text()
            sms_socket2 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_21').text()
            sms_socket3 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_22').text()
            sms_socket4 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_23').text()
            if sms_socket1!='':
                s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                host = sms_socket1
                port =1339
                s1.connect((host,port))
                socCC=socCC + 1
                    
            if sms_socket2!='':
                s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                host = sms_socket2
                port =1339
                s2.connect((host,port))
                socCC=socCC + 1
        
            if sms_socket3!='':
                s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                host = sms_socket3
                port =1339
                s3.connect((host,port))
                socCC=socCC + 1
        
            if sms_socket4!='':
                s4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                host = sms_socket4
                port =1339
                s4.connect((host,port))
                socCC=socCC + 1

        pnumber = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2').text()        
        
        tmsi="-1"
        celln=""

        for cl in self.cells1:
            goAgead = True
            if (currentOperator!="All"):
                goAgead = False
                towerID=cl[6]                    
                for opr in self.df.values:
                    if (currentOperator == str(opr[5]) + ' ' + str(opr[7])):
                        op=str(opr[2])
                        if (len(op)==3):
                                op = '0'+op
                        twID=str(opr[0])+op
                        if (str(towerID) == twID):
                            goAgead = True                            
            if goAgead == True:
                frq=str(int(cl[1]))
                print(frq)
                self.setFreq(frq)
                self.plainTextEdit.insertPlainText("1st Pass Freq:" + str(frq) + "\n")
                QtWidgets.QApplication.processEvents()
                QtWidgets.QApplication.processEvents()
                QtWidgets.QApplication.processEvents()

                a_child_process = subprocess.Popen([lteue, lteue_conf+'1'])    
                time.sleep(3)
                firstseconds= 0
                sendMob=1
                for i in range(1,sendNumberOfSMS+1):
                    currentSeconds = datetime.now()
                    if firstseconds == 0:
                            firstseconds = currentSeconds            
                    if (self.checkbox1.isChecked() == False):
                        self.plainTextEdit.insertPlainText("1. Sending SMS Freq:" + str(frq)  + "-" + str(i) + " - " + str(datetime.now()) + "-" + str((currentSeconds - firstseconds).total_seconds()) + "\n")
                    
                    print(datetime.now())
                    QtWidgets.QApplication.processEvents()
                    QtWidgets.QApplication.processEvents()
                    QtWidgets.QApplication.processEvents()
                    if (self.checkbox1.isChecked() == False):
                        if sendMob==1:
                            self.silentSMS(s,pnumber)
                        if sendMob==2:
                            self.silentSMS(s1,pnumber)
                        if sendMob==3:
                            self.silentSMS(s2,pnumber)
                        if sendMob==4:
                            self.silentSMS(s3,pnumber)
                        if sendMob==5:
                            self.silentSMS(s4,pnumber)
                        sendMob = sendMob +1
                        if sendMob > socCC:
                            sendMob = 1 
                    
                    if (i == sendNumberOfSMS):
                        time.sleep(9)
                    else:
                        if (i ==1 ):
                            time.sleep(waitSendSMS)
                        if (i == 2):
                            time.sleep(waitSendSMS1)
                        if (i == 3):
                            time.sleep(waitSendSMS2)
                        if (i == 4):
                            time.sleep(waitSendSMS3)
                        if (i == 5):
                            time.sleep(waitSendSMS4)
                        if (i == 6):
                            time.sleep(waitSendSMS5)
                        if (i == 7):
                            time.sleep(waitSendSMS6)
                        if (i == 8):
                            time.sleep(waitSendSMS7)
                        if (i == 9):
                            time.sleep(waitSendSMS8)
                        if (i == 10):
                            time.sleep(waitSendSMS9)
                            
                a_child_process.terminate()
                time.sleep(3)

                if (self.checkbox1.isChecked() == False):                
                    cn,rw=self.getCandidates1(sendNumberOfSMS)        
                    print(cn)
                    print(rw)
                    possibleTmsi = ""
                    for r in rw:
                        possibleTmsi = possibleTmsi + str(r[0]) + ' - ' + str(r[1]) +' , '
                    self.plainTextEdit.insertPlainText("1. Possible TMSI's : " + possibleTmsi + "\n")

                    QtWidgets.QApplication.processEvents()
                    QtWidgets.QApplication.processEvents()
                    QtWidgets.QApplication.processEvents()

                    for r in rw:
                        if (tmsi=="-1"):
                            tmsi=""
                        if (tmsi==""):
                            tmsi=r[0]
                        else:
                            tmsi=tmsi+","+r[0]

                    if (tmsi!="-1"):
                        print("FOUND TMSI:",tmsi)            
                        self.plainTextEdit.insertPlainText("FOUND TMSI: " + tmsi + "\n")
                        self.findChild(QtWidgets.QLineEdit, 'lineEdit_5').setText(tmsi)
                        frq=self.getGsmFreq(cn)
                        self.findChild(QtWidgets.QLineEdit, 'lineEdit_3').setText(str(frq))
                        celln1=cn
                        QtWidgets.QApplication.processEvents()
                        QtWidgets.QApplication.processEvents()
                        QtWidgets.QApplication.processEvents()
                        break
                    
        if (self.checkbox1.isChecked() == False):
            self.silentSMS(s,"exit")
            time.sleep(5)            



    def getTmsiOne(self):
        sendNumberOfSMS=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_6').text())
        waitSendSMS=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_7').text())
        waitSendSMS1=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_11').text())
        waitSendSMS2=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_12').text())
        waitSendSMS3=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_13').text())
        waitSendSMS4=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_14').text())        
        waitSendSMS5=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_15').text())        
        waitSendSMS6=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_16').text())
        waitSendSMS7=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_17').text())
        waitSendSMS8=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_18').text())
        waitSendSMS9=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_19').text())
        
        self.getTowersPressed()
        # print(self.cells1)
        # print(self.cells_gsm)
        if (self.checkbox1.isChecked() == False):        
            sms_socket = self.findChild(QtWidgets.QLineEdit, 'lineEdit').text()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = sms_socket
            port =1339
            s.connect((host,port))

            socCC=1
            sms_socket1 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_20').text()
            sms_socket2 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_21').text()
            sms_socket3 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_22').text()
            sms_socket4 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_23').text()
            if sms_socket1!='':
                s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                host = sms_socket1
                port =1339
                s1.connect((host,port))
                socCC=socCC + 1
                    
            if sms_socket2!='':
                s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                host = sms_socket2
                port =1339
                s2.connect((host,port))
                socCC=socCC + 1
        
            if sms_socket3!='':
                s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                host = sms_socket3
                port =1339
                s3.connect((host,port))
                socCC=socCC + 1
        
            if sms_socket4!='':
                s4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                host = sms_socket4
                port =1339
                s4.connect((host,port))
                socCC=socCC + 1
            
        

        pnumber = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2').text()        
        
        tmsi="-1"
        celln=""

        
        frq=str(int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_8').text()))
        print(frq)
        self.setFreq(frq)
        self.plainTextEdit.insertPlainText("1st Pass Freq:" + str(frq) + "\n")
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
      
        
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        
        a_child_process = subprocess.Popen([lteue, lteue_conf+'1'])    
        time.sleep(3)
        firstseconds= 0
        sendMob = 1
        for i in range(1,sendNumberOfSMS+1):
            currentSeconds = datetime.now()
            if firstseconds == 0:
                    firstseconds = currentSeconds            
            if (self.checkbox1.isChecked() == False):
                self.plainTextEdit.insertPlainText("1. Sending SMS Freq:" + str(frq)  + "-" + str(i) + " - " + str(datetime.now()) + "-" + str((currentSeconds - firstseconds).total_seconds()) + "\n")
            
            print(datetime.now())
            QtWidgets.QApplication.processEvents()
            QtWidgets.QApplication.processEvents()
            QtWidgets.QApplication.processEvents()
            if (self.checkbox1.isChecked() == False):
                if sendMob==1:
                    self.silentSMS(s,pnumber)
                if sendMob==2:
                    self.silentSMS(s1,pnumber)
                if sendMob==3:
                    self.silentSMS(s2,pnumber)
                if sendMob==4:
                    self.silentSMS(s3,pnumber)
                if sendMob==5:
                    self.silentSMS(s4,pnumber)
                sendMob = sendMob +1
                if sendMob > socCC:
                    sendMob = 1 
                
                
            if (i == sendNumberOfSMS):
                time.sleep(9)
            else:
                if (i ==1 ):
                    time.sleep(waitSendSMS)
                if (i == 2):
                    time.sleep(waitSendSMS1)
                if (i == 3):
                    time.sleep(waitSendSMS2)
                if (i == 4):
                    time.sleep(waitSendSMS3)
                if (i == 5):
                    time.sleep(waitSendSMS4)
                if (i == 6):
                    time.sleep(waitSendSMS5)
                if (i == 7):
                    time.sleep(waitSendSMS6)
                if (i == 8):
                    time.sleep(waitSendSMS7)
                if (i == 9):
                    time.sleep(waitSendSMS8)
                if (i == 10):
                    time.sleep(waitSendSMS9)
                                        
        a_child_process.terminate()
        time.sleep(3)

        if (self.checkbox1.isChecked() == True):
            return

        cn,rw=self.getCandidates1(sendNumberOfSMS)        
        print(cn)
        print(rw)
        possibleTmsi = ""
        for r in rw:
            possibleTmsi = possibleTmsi + str(r[0]) + ' - ' + str(r[1]) +' , '
        self.plainTextEdit.insertPlainText("1. Possible TMSI's : " + possibleTmsi + "\n")
        
        for r in rw:
            if (tmsi=="-1"):
                tmsi=""
            if (tmsi==""):
                tmsi=r[0]
            else:
                tmsi=tmsi+","+r[0]

        if (tmsi!="-1"):
            print("FOUND TMSI:",tmsi)            
            self.plainTextEdit.insertPlainText("FOUND TMSI: " + tmsi + "\n")
            self.findChild(QtWidgets.QLineEdit, 'lineEdit_5').setText(tmsi)
            frq=self.getGsmFreq(cn)
            self.findChild(QtWidgets.QLineEdit, 'lineEdit_3').setText(str(frq))
            celln1=cn
            QtWidgets.QApplication.processEvents()
            QtWidgets.QApplication.processEvents()
            QtWidgets.QApplication.processEvents()

        if (self.checkbox1.isChecked() == False):        
            self.silentSMS(s,"exit")
            time.sleep(5)            

        
        return
        
        self.plainTextEdit.insertPlainText("2. Sending SMS Freq:" + str(frq) + "\n")
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        
        a_child_process = subprocess.Popen([lteue, lteue_conf+'1'])    
        time.sleep(3)            
        self.silentSMS(s,pnumber)
        time.sleep(9)
        a_child_process.terminate()
        time.sleep(5)
        cn1,rw1=self.getCandidates1(sendNumberOfSMS)
        print(cn)
        print(cn1)        
        print(rw)
        print(rw1)

        possibleTmsi1 = ""
        for r in rw1:
            possibleTmsi1 = possibleTmsi1 + str(r[0]) + ' - ' + str(r[1]) +' , '
        self.plainTextEdit.insertPlainText("2. Possible TMSI's : " + possibleTmsi1 + "\n")

        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()


        for r in rw:
            for r1 in rw1:
                if (r[0]==r1[0]):
                    if (tmsi=="-1"):
                        tmsi=""
                    if (tmsi==""):
                        tmsi=r[0]
                    else:
                        tmsi=tmsi+","+r[0]

        if (tmsi!="-1"):
            print("FOUND TMSI:",tmsi)            
            self.plainTextEdit.insertPlainText("FOUND TMSI: " + tmsi + "\n")
            self.findChild(QtWidgets.QLineEdit, 'lineEdit_5').setText(tmsi)
            frq=self.getGsmFreq(cn)
            self.findChild(QtWidgets.QLineEdit, 'lineEdit_3').setText(str(frq))
            celln1=cn
            QtWidgets.QApplication.processEvents()
            QtWidgets.QApplication.processEvents()
            QtWidgets.QApplication.processEvents()

        
        self.silentSMS(s,"exit")
        time.sleep(5)            


    def execlte1(self , cmd):
        towers=[1,2,3,4,5,7,8,11,12,13,14,17,18,19,20,21,24,25,26,28,29,30,31,32,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,65,66,67,68,69,70,71,72,73,74,75,76,85,87,88];
        cells=[];
        for i in towers:
            self.plainTextEdit.insertPlainText("Band: " + str(i) + "\n")
            print("Band :" + str(i))
            localCells=[]
            with Popen([ltesearch,'-b',str(i)], stdout=PIPE, bufsize=1, universal_newlines=True) as p:
                for line in p.stdout:
                    print(line, end='') # process line here
                    QtWidgets.QApplication.processEvents()
                    QtWidgets.QApplication.processEvents()
                    QtWidgets.QApplication.processEvents()
                    if (line.startswith("Found CELL") and len(line)>50):
                        line=line.replace("Found CELL ","")
                        line=line.replace(" MHz","")
                        line=line.replace(" EARFCN=","")
                        line=line.replace(" PHYID=","")
                        line=line.replace(" PRB","")
                        line=line.replace(" ports","")
                        line=line.replace(" PSS power=","")
                        line=line.replace(" dBm","")
                        #cells.append(line.split(","))
                        cells.append([float(x) for x in (line+",0").split(",")])                        
                        self.plainTextEdit.insertPlainText("FOUND LTE Cell " + line + ".\n")                    
                        
            if p.returncode != 0:
                # raise CalledProcessError(p.returncode, p.args)
                print(p.returncode)
            time.sleep(5)
        return cells

    def execlte(self , cmd):
        cells=[];
        with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                print(line, end='') # process line here
                QtWidgets.QApplication.processEvents()
                QtWidgets.QApplication.processEvents()
                QtWidgets.QApplication.processEvents()
                if (line.startswith("Found CELL") and len(line)>50):
                    line=line.replace("Found CELL ","")
                    line=line.replace(" MHz","")
                    line=line.replace(" EARFCN=","")
                    line=line.replace(" PHYID=","")
                    line=line.replace(" PRB","")
                    line=line.replace(" ports","")
                    line=line.replace(" PSS power=","")
                    line=line.replace(" dBm","")
                    #cells.append(line.split(","))
                    cells.append([float(x) for x in (line+',0').split(",")])
                    self.plainTextEdit.insertPlainText("FOUND LTE Cell " + line + ".\n")                    
                    
        if p.returncode != 0:
            raise CalledProcessError(p.returncode, p.args)
        return cells


    def execgsm1(self,cmd):        
        towers=["GSM900","DCS1800", "GSM850", "PCS1900", "GSM450","GSM480", "GSM-R"]
        cells=[];        
        for i in towers:
            self.plainTextEdit.insertPlainText("Band :" + i + ".\n")
            QtWidgets.QApplication.processEvents()
            QtWidgets.QApplication.processEvents()
            QtWidgets.QApplication.processEvents()
            with Popen([gsmsearch, "-b",i,"-g","90","-v"], stdout=PIPE, bufsize=1, universal_newlines=True) as p:
                for line in p.stdout:
                    print(line, end='') # process line here            
                    QtWidgets.QApplication.processEvents()
                    QtWidgets.QApplication.processEvents()
                    QtWidgets.QApplication.processEvents()
                    if (line.startswith("ARFCN: ") and len(line)>50):
                        line=line.replace("ARFCN: ","")
                        line=line.replace(" Freq: ","")
                        line=line.replace("M,",",")
                        line=line.replace(" CID:","")
                        line=line.replace(" LAC:","")
                        line=line.replace(" MCC:","")
                        line=line.replace(" MNC:","")
                        line=line.replace(" Pwr:","")
                        #cells.append(line.split(","))
                        cells.append([float(x) for x in line.split(",")])
                        self.plainTextEdit.insertPlainText("FOUND GSM Cell " + line + ".\n")
                        app.processEvents()
                        
                        
            # if p.returncode != 0:
                # raise CalledProcessError(p.returncode, p.args)
                # print(p.returncode)            
        return cells

    def execgsm(self,cmd):
        cells=[];
        with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                print(line, end='') # process line here            
                QtWidgets.QApplication.processEvents()
                QtWidgets.QApplication.processEvents()
                QtWidgets.QApplication.processEvents()
                if (line.startswith("ARFCN: ") and len(line)>50):
                    line=line.replace("ARFCN: ","")
                    line=line.replace(" Freq: ","")
                    line=line.replace("M,",",")
                    line=line.replace(" CID:","")
                    line=line.replace(" LAC:","")
                    line=line.replace(" MCC:","")
                    line=line.replace(" MNC:","")
                    line=line.replace(" Pwr:","")
                    #cells.append(line.split(","))
                    cells.append([float(x) for x in line.split(",")])
                    self.plainTextEdit.insertPlainText("FOUND GSM Cell " + line + ".\n")
                    app.processEvents()
                    
                    
        if p.returncode != 0:
            # raise CalledProcessError(p.returncode, p.args)
            print(p.returncode)
        return cells


    def setFreq(self,freq):
        f1 = open(lteue_conf, 'r')
        f2 = open(lteue_conf+'1', 'w')
        for line in f1:
            f2.write(line.replace('6400', freq))
        f1.close()
        f2.close()

    def print_stat(self,conn,occ):
        cur = conn.cursor()
        cur.execute("SELECT RTMSI,COUNT(*) as CC FROM LOGS GROUP BY 1 HAVING COUNT(*)>=" + str(occ-2) + " AND COUNT(*)<=" + str(occ) + " ORDER BY 2 DESC LIMIT 10")
        #cur.execute("SELECT RTMSI,COUNT(*) as CC FROM LOGS WHERE RTMSI='cd:c2:08:38' GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        #cur.execute("SELECT RTMSI,COUNT(*) as CC FROM LOGS WHERE SFN=60 OR SFN=124 OR SFN=188 OR SFN=252 OR SFN=316 OR SFN=380 OR SFN=444 OR SFN=508 OR SFN=572 OR SFN=636 OR SFN=700 OR SFN=764 OR SFN=828 OR SFN=892 OR SFN=956 OR SFN=1020 GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        rows = cur.fetchall()
        return rows

    def getCandidates(self , occ):
        cellno=""
        os.system("tshark -T fields -n -r /tmp/ue.pcap -E separator=/t -e lte-rrc.cellIdentity -e lte-rrc.trackingAreaCode -e lte-rrc.MCC_MNC_Digit -e lte-rrc.defaultPagingCycle -e lte-rrc.nB -e frame.time -e frame.number -e mac-lte.sfn -e mac-lte.subframe -e lte-rrc.mmec -e lte-rrc.m_TMSI  > /tmp/capture1.csv")

        #numpy
        path = "/tmp/capture1.csv"
        e18 = np.genfromtxt(path, dtype=str , delimiter = '\t')

        conn = sqlite3.connect('TestDB.db')

        conn.execute('''DROP TABLE IF EXISTS LOGS''')

        conn.execute('''CREATE TABLE LOGS
                ([generated_id] INTEGER PRIMARY KEY,[LOGDATE] text, [SFN] integer, [RTMSI] text)''')
        
        for r in e18:
            #print(r[5] + '-' + r[7] + '-' + r[10])
            if (r[2] != ""):
                cellno=r[2].replace(",","")

            rtmsi=r[10].split(',')        
            for r1 in rtmsi:
                tm=datetime.strptime(r[5].replace('000 BST',''),'%b %d, %Y %H:%M:%S.%f')
                sql = ''' INSERT INTO LOGS(LOGDATE,SFN,RTMSI)
                        VALUES(?,?,?) '''
                values=(tm.isoformat(),r[7],r1)
                cur = conn.cursor()
                cur.execute(sql, values)
        conn.commit()
        rows = self.print_stat(conn,occ)
        return cellno,rows

    def print_stat1(self,conn,occ):
        cur = conn.cursor()
        cur.execute("SELECT RTMSI,COUNT(*) as CC FROM LOGS GROUP BY 1 HAVING COUNT(*)>=1 ORDER BY 2")
        #cur.execute("SELECT RTMSI,COUNT(*) as CC FROM LOGS WHERE RTMSI='cd:c2:08:38' GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        #cur.execute("SELECT RTMSI,COUNT(*) as CC FROM LOGS WHERE SFN=60 OR SFN=124 OR SFN=188 OR SFN=252 OR SFN=316 OR SFN=380 OR SFN=444 OR SFN=508 OR SFN=572 OR SFN=636 OR SFN=700 OR SFN=764 OR SFN=828 OR SFN=892 OR SFN=956 OR SFN=1020 GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        rows = cur.fetchall()
        return rows

    def getCandidates1(self , occ):
        rows1 = []
        sendNumberOfSMS=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_6').text())
        waitSendSMS=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_7').text())
        waitSendSMS1=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_11').text())
        waitSendSMS2=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_12').text())
        searchInterval=int(self.findChild(QtWidgets.QLineEdit, 'lineEdit_10').text())

        cellno=0
        os.system("tshark -T fields -n -r /tmp/ue.pcap -E separator=/t -e lte-rrc.cellIdentity -e lte-rrc.trackingAreaCode -e lte-rrc.MCC_MNC_Digit -e lte-rrc.defaultPagingCycle -e lte-rrc.nB -e frame.time -e frame.number -e mac-lte.sfn -e mac-lte.subframe -e lte-rrc.mmec -e lte-rrc.m_TMSI  > /tmp/capture1.csv")

        #numpy
        path = "/tmp/capture1.csv"
        e18 = np.genfromtxt(path, dtype=str , delimiter = '\t')

        conn = sqlite3.connect('TestDB.db')

        conn.execute('''DROP TABLE IF EXISTS LOGS''')

        conn.execute('''CREATE TABLE LOGS
                ([generated_id] INTEGER PRIMARY KEY,[LOGDATE] text, [SFN] integer, [RTMSI] text,[TM] real)''')

                
        firstseconds= 0 
        for r in e18:
            # print(r[5] + '-' + r[7] + '-' + r[10])
            # print(len(r.shape))
            try:
                
                if (len(r.shape)>0 and r.shape[0]>=3 and r[2] != ""):
                    cellno=r[2].replace(",","")
            except NameError:
                    print("Some Error")

            if (len(r.shape)>0 and r.shape[0]>=10 and r[10] != ""):
                rtmsi=r[10].split(',')        
                for r1 in rtmsi:
                    if (r[5].find('000 BST')>=0):
                        tm=datetime.strptime(r[5].replace('000 BST',''),'%b %d, %Y %H:%M:%S.%f')

                    if (r[5].find('000 GMT')>=0):
                        tm=datetime.strptime(r[5].replace('000 GMT',''),'%b %d, %Y %H:%M:%S.%f')

                    currentSeconds = tm
                    if firstseconds == 0:
                            firstseconds = currentSeconds


                    sql = ''' INSERT INTO LOGS(LOGDATE,SFN,RTMSI,TM)
                            VALUES(?,?,?,?) '''
                    tm1=(currentSeconds-firstseconds).total_seconds()
                    if (r1 == "f66e5848"):
                        print(r1)
                        print(tm1)
                    values=(tm.isoformat(),r[7],r1,tm1)
                    if (r1!=''):                    
                        cur = conn.cursor()
                        cur.execute(sql, values)
        conn.commit()
        cur = conn.cursor()
        cur.execute("SELECT * FROM LOGS")
        with open('/tmp/output1.csv','w') as out_csv_file:
            csv_out = csv.writer(out_csv_file)
            # write header                        
            csv_out.writerow([d[0] for d in cur.description])
            # write data                          
            for result in cur:
                csv_out.writerow(result)
            
        
        rw1 = cur.fetchall()
        

        cur1 = conn.cursor()
        for j in range (-6,6):
            addSQL=""
            for i in range(1,sendNumberOfSMS):
                if (i == 1):
                    addSQL = addSQL + " OR ((TM>=" + str((waitSendSMS*i)-searchInterval+j)+ ") AND (TM<="+ str((waitSendSMS)+searchInterval+j)+ ")) "
                if (i == 2):
                    addSQL = addSQL + " OR ((TM>=" + str((waitSendSMS+waitSendSMS1)-searchInterval+j)+ ") AND (TM<="+ str((waitSendSMS+waitSendSMS1)+searchInterval+j)+ ")) "
                if (i == 3):
                    addSQL = addSQL + " OR ((TM>=" + str((waitSendSMS+waitSendSMS1+waitSendSMS2)-searchInterval+j)+ ") AND (TM<="+ str((waitSendSMS+waitSendSMS1+waitSendSMS2)+searchInterval+j)+ ")) "
                    
        
            cur.execute("SELECT RTMSI,COUNT(*) as CC FROM LOGS WHERE ((TM>=0) AND (TM<=3)) "+ addSQL + " GROUP BY 1 HAVING COUNT(*)>=" + str(sendNumberOfSMS-1) + " ORDER BY 2 DESC")
            print(str(j) + ". SELECT RTMSI,COUNT(*) as CC FROM LOGS WHERE ((TM>=0) AND (TM<=3)) "+ addSQL + " GROUP BY 1 HAVING COUNT(*)>=" + str(sendNumberOfSMS-1) + " ORDER BY 2 DESC")
            rows1 = rows1 + cur.fetchall()
            # if (len(rows1)>0):
            #    break
        rows=[]
        for tm in rows1:
            if tm not in rows:
                cur1.execute("SELECT TM FROM LOGS WHERE RTMSI='"+str(tm[0])+"'")
                tms=cur1.fetchall()
                cllst=[]
                for tms1 in tms:
                    cllst.append(tms1[0])
                df=[x - cllst[i - 1] for i, x in enumerate(cllst)][1:]
                if (min(df)<(waitSendSMS-4)):
                    d='exclude'    
                else:
                    rows.append(tm)
        # rows = rows1 
        # self.print_stat1(conn,occ)
        print(rows)
        return cellno,rows


app = QtWidgets.QApplication(sys.argv)
window = Ui( )
app.exec_()