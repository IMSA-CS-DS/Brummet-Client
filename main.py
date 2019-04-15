# IMSA Computational Science and Data Science Club: Brummet Client
# Written for ssh into IMSA SLURM cluster
# Written by: Arthur Lu, Jacob Levine
# Use at one's own risk

__author__ = ("Arthur Lu <alu1@imsa.edu>", "Jacob Levine <jlevine@imsa.edu>")

from kivy.config import Config
#Config.set('graphics', 'resizable', False)

from kivy.app import App

from kivy.properties import StringProperty, ObjectProperty

from kivy.core.window import Window

from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition

from kivy.clock import Clock

import csv
import paramiko
import time
#import os

def load_csv(filepath):
    with open(filepath, newline='') as csvfile:
        file_array = list(csv.reader(csvfile))
        csvfile.close() 
    return file_array

class Client(Screen):
    Window.size = (1280, 720)

class Connect(Screen):
    Window.size = (600, 300)

    def routine(self, host, port, username, password):

        #print(username, password)
        self.ids.status.text = "connecting"
               
        ssh = None
        sftp = None

        try:
            self.ids.status.text = "attempting to connect to " + host + ":" + str(port)
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port, username, password)
            
            transport = paramiko.Transport((host, port))
            transport.connect(username = username, password = password)
            sftp = paramiko.SFTPClient.from_transport(transport)

            self.ids.status.text = "connected to " + host + ":" + str(port)

            Clock.schedule_once(self.continue_to_client, 2)

        except Exception as e:
            if sftp is not None:
                sftp.close()
            if ssh is not None:
                ssh.close()

            self.ids.status.text = "connection failed: " + str(e)
            Clock.schedule_once(self.return_to_login, 2)
            #self.manager.current = 'login'

    def return_to_login(self, *args):
        self.manager.transition = SlideTransition(direction = "right")
        self.manager.current = 'login'
            #time.sleep(5)

    def continue_to_client(self, *args):
        self.manager.transition = NoTransition()
        self.manager.current = 'client'
            

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

target_x = 600
target_y = 300

manager = ScreenManager()

class BrummetApp(App):

    username = StringProperty(None)
    password = StringProperty(None)

    screenName = StringProperty(None)

    title = 'Brummet Client v ' + load_csv("data/meta")[0][1]

    def check_resize(self, instance, x, y):
        # resize X
        screenName = manager.current
        print(screenName)
        if manager.current != "client":

            if x >  target_x:
                Window.size = (target_x, Window.size[1])

            if y > target_y:
                Window.size = (Window.size[0], target_y)

            if x <  target_x:
                Window.size = (target_x, Window.size[1])

            if y < target_y:
                Window.size = (Window.size[0], target_y)

    def build(self):

        manager = ScreenManager()
        loginScr = Screen(name = 'login')
        loginScr.add_widget(Login())
        manager.add_widget(loginScr)

        connectScr = Screen(name = 'connect')
        connectScr.add_widget(Connect())
        manager.add_widget(connectScr)

        clientScr = Screen(name = 'client')
        clientScr.add_widget(Client())
        manager.add_widget(clientScr)

        Window.bind(on_resize=self.check_resize)

        return manager

if __name__ == '__main__':
    BrummetApp().run()