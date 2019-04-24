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
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label

from kivy.lang.builder import Builder

from kivy.clock import Clock

import csv
import paramiko
#import time
from datetime import datetime

def load_csv(filepath):
    with open(filepath, newline='') as csvfile:
        file_array = list(csv.reader(csvfile))
        csvfile.close() 
    return file_array

class FileTemplate(Button):

    sftp = None

    def changedir(self, path):

        try:

            self.sftp.chdir(path)

        except:

            file = self.sftp.file(path.split(",")[-1], mode = 'w+')

class Client(Screen):

    def on_pre_enter(self, *args):
        Window.size = (1280, 720)
        Window.top = 100
        Window.left = 100

    def client(self, ssh, sftp):

        self.ssh = ssh
        self.sftp = sftp

        self.sftp.chdir('brummet_projects')

        Clock.schedule_interval(self.auto, 1)

    def auto(self, dt):

        projects = self.sftp.listdir('.')

        for file in projects:

            if file[0] == ".":

                projects.remove(file)

        list_view = self.ids.list_files

        list_view.clear_widgets()

        if self.sftp.getcwd().split("/")[-1].split(",")[-1] == "brummet_projects":

            self.ids.dirname.text = "Projects"
            self.ids.labeltext.text = "Project Name"

        else:

            self.ids.dirname.text = self.sftp.getcwd().split("/")[-1].split(",")[-1]
            self.ids.labeltext.text = "File Name"

        for file in projects:

            template = FileTemplate()
            template.sftp = self.sftp
            try:
                parse = file.split(",")
                template.ids.filename.text = parse[1]
                template.ids.filetype.text = parse[0]
                template.ids.fileimage.source = "data\customui\\" + parse[0] + ".png"
                template.ids.filetime.text = str(datetime.fromtimestamp(self.sftp.lstat(file).st_mtime))
            except:
                template.ids.filename.text = file
                template.ids.filetype.text = ""
                template.ids.fileimage.source = ""
                template.ids.filetime.text = str(datetime.fromtimestamp(self.sftp.lstat(file).st_mtime))

            list_view.add_widget(template)

    def cddotdot(self):

        if not self.sftp.getcwd().split("/")[-1].split(",")[-1] == "brummet_projects":

            self.sftp.chdir("..")

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


manager  = ScreenManager()

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