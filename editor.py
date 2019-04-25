# IMSA Computational Science and Data Science Club: Editor Package
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

class Editor(Screen):

    ssh = None
    sftp = None

    def on_pre_enter(self):
        self.ssh = ssh
        self.sftp = sftp
        Window.size = (1280, 720)
        Window.top = 100
        Window.left = 100

    def editor(self, ssh, sftp):

    	   pass

manager  = ScreenManager()

class EditorApp(App):

    title = 'Brummet Editor v ' + load_csv("data/meta")[0][1]

    def build(self, ssh, sftp):

        manager.add_widget(Editor(name = 'editor'))

        self.manager.current = "editor"
        self.manager.current.editor(ssh, sftp)

        return manager

if __name__ == '__main__':
    BrummetApp().run()