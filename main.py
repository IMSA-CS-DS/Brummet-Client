from kivy.config import Config
Config.set('graphics', 'resizable', False)

from kivy.app import App

from kivy.properties import StringProperty

from kivy.core.window import Window

from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

import csv
import paramiko
#import os

global username
global password

def load_csv(filepath):
    with open(filepath, newline='') as csvfile:
        file_array = list(csv.reader(csvfile))
        csvfile.close()
    return file_array

class Connect(Screen):
    Window.size = (600, 300)
    def routine(self):

        host = 'titanrobotics.ddns.net'
        port = 60022
        print(username, password)
        self.ids.status.text = "connecting"
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.ids.status.text = "attempting to connect to " + host
            ssh.connect(host, port, username, password)
            yield ssh
            self.ids.status.text = "connected to " + host

        finally:
            ssh.close()
            self.ids.status.text = "connection failed"

        #print("here")
    #ssh = loginroutine(username, password)

class Login(Screen):
    Window.size = (600, 300)
    def do_login(self, loginText, passwordText):
        app = App.get_running_app()

        username = loginText
        password = passwordText

        self.manager.transition = SlideTransition(direction = "left")
        self.manager.current = "connect"

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