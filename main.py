# IMSA Computational Science and Data Science Club: Brummet Clinet
# Written for ssh into IMSA SLURM cluster
# Written by: Arthur Lu, Jacob Levine
# Use at one's own risk

__author__ = ("Arthur Lu <alu1@imsa.edu>", "Jacob Levine <jlevine@imsa.edu>")

from kivy.config import Config
Config.set('graphics', 'resizable', False)

from kivy.app import App

from kivy.properties import StringProperty, ObjectProperty

from kivy.core.window import Window

from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition

import csv
import paramiko
#import os

def load_csv(filepath):
    with open(filepath, newline='') as csvfile:
        file_array = list(csv.reader(csvfile))
        csvfile.close() 
    return file_array

class Connect(Screen):
    Window.size = (600, 350)
    def routine(self, host, port, username, password):

        #print(username, password)
        self.ids.status.text = "connecting"
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        sftp = None

        try:
            self.ids.status.text = "attempting to connect to " + host + ":" + str(port)
            ssh.connect(host, port, username, password)
            self.ids.status.text = "connected to " + host + ":" + str(port)

            transport = paramiko.Transport((host, port))
            transport.connect(username = username, password = password)
            sftp = paramiko.SFTPClient.from_transport(transport)

        except Exception as e:
            ssh.close()
            self.ids.status.text = "connection failed: " + str(e)

class Login(Screen):
    Window.size = (600, 300)

    def do_login(self, loginText, passwordText, hostText, portText):
        app = App.get_running_app()

        if hostText == "":
            hostText = "slurm.imsa.edu"
        if portText == "":
            portText = "22"

        host = hostText
        port = int(portText)
        
        username = loginText
        password = passwordText

        self.manager.transition = SlideTransition(direction = "left")
        self.manager.current = "connect"

        self.manager.get_screen('connect').routine(host, port, username, password)

    def resetForm(self):
        self.ids['login'].text = ""
        self.ids['password'].text = ""

class BrummetApp(App):
    username = StringProperty(None)
    password = StringProperty(None)

    title = 'Brummet Client v ' + load_csv("data/meta")[0][1]

    def build(self):
        manager = ScreenManager()

        manager.add_widget(Login(name = 'login'))
        manager.add_widget(Connect(name = 'connect'))

        return manager

if __name__ == '__main__':
    BrummetApp().run()