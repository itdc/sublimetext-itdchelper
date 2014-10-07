# @author 		Avtandil Kikabidze aka LONGMAN
# @copyright 		Copyright (c) 2008-2014, Avtandil Kikabidze (akalongman@gmail.com)
# @link 			http://long.ge
# @license 		GNU General Public License version 2 or later;

import sublime, sublime_plugin, os, re, sys

directory = os.path.dirname(os.path.realpath(__file__))
libs_path = os.path.join(directory, "itdchelper")

if libs_path not in sys.path:
	sys.path.append(libs_path)

import threading
from random import sample
import time

from functions import *
from panel import ItdchelperProjectPanel
from request import ITDCRequest
from loading import ItdchelperLoading
from commands import (EraseCommand)

import subprocess

### Create CMS Project
class ItdchelperPhpUnitCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		thread = ItdchelperPhpUnitProcess(self.view)
		thread.start()

	def is_enabled(self):
		ret = True
		return ret


class ItdchelperPhpUnitProcess(threading.Thread):
	settings = None
	view = None
	window = None
	start_time = None

	server_addr = None
	server_user = None
	server_pass = None
	plink_path = None
	pu_folder = 'cmsv3'


	def __init__(self, pview):
		self.settings = sublime.load_settings('ITDCHelper.sublime-settings')
		self.start_time = time.time()
		self.view = pview
		self.window = self.view.window()

		project_data = self.window.project_data()
		if (project_data is None):
			show_error("Project Data not found!")
			return


		project_folder = project_data['folders'][0]['path']
		if (project_folder is None):
			show_error("Project folder not found!")
			return


		if not os.path.isfile("%s" % os.path.join(project_folder, 'phpunit.xml')) and not os.path.isfile("%s" % os.path.join(project_folder, 'phpunit.xml.dist')):
			show_error("phpunit.xml or phpunit.xml.dist not found!")
			return


		path = project_folder.replace('\\', '/')
		pu_folder = path.rsplit("/",1)[1]
		if (pu_folder is None):
			show_error("Project folder not found!")
			return
		self.pu_folder = pu_folder


		self.server_addr = self.settings.get('server_addr')
		if ((self.server_addr is None) or (len(self.server_addr) == 0)):
			show_error("Server address not defined")
			return

		self.server_user = self.settings.get('server_user')
		if ((self.server_user is None) or (len(self.server_user) == 0)):
			show_error("Server user not defined")
			return

		self.server_pass = self.settings.get('server_pass')
		if ((self.server_pass is None) or (len(self.server_pass) == 0)):
			show_error("Server password not defined")
			return

		self.plink_path = self.settings.get('plink_path')

		threading.Thread.__init__(self)



	def run(self):
		if not hasattr(self, 'panel'):
			self.panel = ItdchelperProjectPanel(self.window, 'ItdchelperPHPUnit', 'PHPUnit Tests: '+self.pu_folder+"\n")


		self.panel.append('PHPUnit is running')
		self.panel.append('Loading')

		thread2 = ItdchelperLoading(self.panel)
		thread2.start()



		try:
			if (sublime.platform() == "windows"):
				startupinfo = subprocess.STARTUPINFO()
				startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
				startupinfo.wShowWindow = subprocess.SW_HIDE
				cmd = ["plink", "-pw", self.server_pass, self.server_user+"@"+self.server_addr, "cd "+self.pu_folder+" && phpunit"]
				p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, shell=False, creationflags=subprocess.SW_HIDE)
			else:
				p = subprocess.Popen(["ssh", "", "-l", filters, "-f", "-", "-o", "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout, stderr = p.communicate()
		except Exception as e:
			stderr = str(e)
			thread2.stop()
			stderr = "Error: "+stderr
			elapsed = "\n= = = = = = = = = = = = = = =\nExecution time: %.3f sec" % round((time.time() - self.start_time), 3)
			txt = stderr + elapsed
			self.panel.replace(txt)
			self.panel.finish()
			return False



		if (not stderr and not stdout):
			thread2.stop()
			stderr = "Unknown error!"
			stderr = "Error: "+stderr
			elapsed = "\n= = = = = = = = = = = = = = =\nExecution time: %.3f sec" % round((time.time() - self.start_time), 3)
			txt = stderr + elapsed
			self.panel.replace(txt)
			self.panel.finish()
			return False


		thread2.stop()

		elapsed = "\n= = = = = = = = = = = = = = =\nExecution time: %.3f sec" % round((time.time() - self.start_time), 3)
		msg = stdout.decode('UTF-8') + elapsed

		self.panel.replace(msg)
		self.panel.finish()


	def isRunning(self):
		return self.running


