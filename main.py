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

    def on_pre_enter(self, *args):
        Window.size = (1280, 720)
        Window.top = 100
        Window.left = 100

    def client(self, ssh, sftp):

        self.ssh = ssh
        self.sftp = sftp

        self.ssh.chdir('brummet_projects')

        Clock.schedule_interval(self.auto, 1)

    def auto(self, dt):

        projects = self.sftp.listdir('.')

        list_view = self.ids.list_files

        print(projects)
        
        for file in projects:

            list_view.add_widget("""
                Button:
                        background_color: 0,0,0,0
                        Image:
                            source:'data\customui\client_file_bar.png'
                            x: self.parent.x
                            y: self.parent.y
                            width: self.parent.width
                            height: self.parent.height
                            allow_stretch: True
                            keep_ratio: False

                        Image:
                            source:'data\customui\python.png'
                            y: self.parent.y + 10
                            x: - self.parent.width/2 + 25
                            width: self.parent.width - 20
                            height: self.parent.height - 20

                        Label:
                            size_hint:(0.9, 1)
                            text: "hello there"
                            y: self.parent.y
                            x: self.parent.x + self.parent.width*0.05
                            width: self.parent.width
                            height: self.parent.height
                            text_size: self.size
                            font_size: self.height - 30
                            halign: 'left'
                            valign: 'middle'

                        Label:
                            size_hint:(0.9, 1)
                            text: "no u"
                            y: self.parent.y
                            x: self.parent.x + self.parent.width*0.7
                            width: self.parent.width
                            height: self.parent.height
                            text_size: self.size
                            font_size: self.height - 30
                            halign: 'left'
                            valign: 'middle'

                        Label:
                            size_hint:(0.9, 1)
                            text: "dong big dumb"
                            y: self.parent.y
                            x: self.parent.x + self.parent.width*0.8
                            width: self.parent.width
                            height: self.parent.height
                            text_size: self.size
                            font_size: self.height - 30
                            halign: 'left'
                            valign: 'middle'
                """)

class Connect(Screen):
    def on_pre_enter(self, *args):
        Window.size = (600, 300)

    def routine(self, host, port, username, password):

        ssh = None
        sftp = None

        #print(username, password)
        self.ids.status.text = "connecting"

        try:
            self.ids.status.text = "attempting to connect to " + host + ":" + str(port)
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port, username, password)
            
            transport = paramiko.Transport((host, port))
            transport.connect(username = username, password = password)
            sftp = paramiko.SFTPClient.from_transport(transport)

            self.ids.status.text = "connected to " + host + ":" + str(port)

            Clock.schedule_once(self.continue_to_client, 0.1)
            self.manager.get_screen('client').client(ssh, sftp)
            

        except Exception as e:
            if sftp is not None:
                sftp.close()
            if ssh is not None:
                ssh.close()

            self.ids.status.text = "connection failed: " + str(e)
            Clock.schedule_once(self.return_to_login, 4)
            #self.manager.current = 'login'

    def return_to_login(self, *args):
        self.manager.transition = SlideTransition(direction = "right")
        self.manager.current = 'login'
            #time.sleep(5)

    def continue_to_client(self, *args):

        self.manager.transition = NoTransition()
        self.manager.current = 'client'
            

class Login(Screen):

    def on_pre_enter(self, *args):
        Window.size = (600, 300)

    def do_login(self, loginText, passwordText, hostText, portText):
        app = App.get_running_app()

        if hostText == "":
            hostText = "titanrobotics.ddns.net"
        if portText == "":
            portText = "60022"

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


manager = ScreenManager()

class BrummetApp(App):

    username = StringProperty(None)
    password = StringProperty(None)

    title = 'Brummet Client v ' + load_csv("data/meta")[0][1]

    def check_resize(self, instance, x, y):
        # resize X
        #screenName = manager.current
        #print(screenName)
        if manager.current != "client":

            target_x = 600
            target_y = 300


            if x >  target_x:
                Window.size = (target_x, Window.size[1])

            if y > target_y:
                Window.size = (Window.size[0], target_y)

            if x <  target_x:
                Window.size = (target_x, Window.size[1])

            if y < target_y:
                Window.size = (Window.size[0], target_y)

        if manager.current == "client":

            target_x = 1280
            target_y = 720

            if x <  target_x:
                Window.size = (target_x, Window.size[1])

            if y < target_y:
                Window.size = (Window.size[0], target_y)

    def build(self):

        manager.add_widget(Login(name = 'login'))
        manager.add_widget(Connect(name = 'connect'))
        manager.add_widget(Client(name = 'client'))

        Window.bind(on_resize=self.check_resize)

        return manager

if __name__ == '__main__':
    BrummetApp().run()