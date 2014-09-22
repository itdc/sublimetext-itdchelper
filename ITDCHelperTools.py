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



### Chmod path
class ItdchelperToolsChmodCommand(sublime_plugin.TextCommand):
	chmods = ['0777', '0755']
	path = None
	recursively = False

	def run(self, edit, paths, recursively):

		path = self.get_first(paths)
		if (not path):
			show_error('Path is empty')

		self.path = path
		self.recursively = recursively

		items = []
		item = []
		item.append('Chmod 777 (rwx-rwx-rwx)')
		item.append(self.path)
		items.append(item)

		item = []
		item.append('Chmod 755 (rwxr-xr-x)')
		item.append(self.path)
		items.append(item)

		self.view.window().show_quick_panel(items, self.on_done_final)
		return





	def on_done_final(self, choice):
		if (choice == -1):
			return

		try:
			chmod = self.chmods[choice]
		except IndexError:
			return

		if (not self.path):
			return

		thread = ItdchelperToolsChmodProcess(self.path, chmod, self.recursively, self.view)
		thread.start()




	def get_first(self, iterable, default=None):
		if iterable:
			for item in iterable:
				return item
		return default


	def is_enabled(self):
		ret = True
		return ret


class ItdchelperToolsChmodProcess(threading.Thread):
	settings = None
	localservice_url = ''
	path = ''
	recursively = False
	chmod = False
	view = None
	window = None
	start_time = None


	def __init__(self, path, chmod, recursively, pview):
		self.settings = sublime.load_settings('ITDCHelper.sublime-settings')
		self.start_time = time.time()
		self.path = path
		if (recursively is True):
			self.recursively = 1
		else:
			self.recursively = 0


		self.chmod = chmod
		self.view = pview
		self.window = self.view.window()
		self.localservice_url = 'http://tools.local.itdc.ge/project/chmod.php'
		threading.Thread.__init__(self)



	def run(self):
		if not hasattr(self, 'panel'):
			self.panel = ItdchelperProjectPanel(self.window, 'ItdchelperToolsChmod', 'Chmod Path: "'+self.path+'"'+"\n")


		self.panel.append('Chmodding path "'+self.path+'"')
		self.panel.append('Loading')

		thread2 = ItdchelperLoading(self.panel)
		thread2.start()


		service_url = self.localservice_url + '?mode=chmod&chmod='+self.chmod+'&recursively='+str(self.recursively)+'&path='+self.path
		#print(service_url)
		#self.panel.append('DEBUG: request to '+service_url)

		request = ITDCRequest(service_url)
		if (request.isError()):
			thread2.stop()
			stderr = "Error: "+request.getError()
			elapsed = "\n= = = = = = = = = = = = = = =\nExecution time: %.3f sec" % round((time.time() - self.start_time), 3)
			txt = stderr + elapsed
			self.panel.replace(txt)
			self.panel.finish()
			return False
		json_data = request.getJSON()


		#self.panel.append(' Success', False)

		thread2.stop()

		elapsed = "\n= = = = = = = = = = = = = = =\nExecution time: %.3f sec" % round((time.time() - self.start_time), 3)
		status = json_data['status']
		msg = json_data['msg'] + elapsed
		if (status == "ERROR"):
			msg = "Error: "+msg

		self.panel.replace(msg)
		self.panel.finish()


	def isRunning(self):
		return self.running



### CMD
class ItdchelperToolsCmdCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		self.view.window().show_input_panel('CMD:', '', lambda s: self.on_done(s), None, None)
		return


	def on_done(self, cmd):
		if (len(cmd) < 1):
			show_error('Command is empty!')
			return
		thread = ItdchelperToolsCmdProcess(cmd, self.view)
		thread.start()
		return


	def is_enabled(self):
		settings = sublime.load_settings('ITDCHelper.sublime-settings')
		cmd_enabled = settings.get('cmd_enabled', 0)
		if (cmd_enabled):
			return True
		return False


class ItdchelperToolsCmdProcess(threading.Thread):
	settings = None
	localservice_url = ''
	path = ''
	recursively = False
	chmod = False
	view = None
	window = None
	start_time = None


	def __init__(self, cmd, pview):
		self.settings = sublime.load_settings('ITDCHelper.sublime-settings')
		self.start_time = time.time()
		self.cmd = cmd
		self.view = pview
		self.window = self.view.window()
		self.localservice_url = 'http://tools.local.itdc.ge/project/cmd.php'
		threading.Thread.__init__(self)



	def run(self):
		if not hasattr(self, 'panel'):
			self.panel = ItdchelperProjectPanel(self.window, 'ItdchelperToolsCmd', 'Command: "'+self.cmd+'"'+"\n")


		self.panel.append('Executing command')
		self.panel.append('Loading')

		thread2 = ItdchelperLoading(self.panel)
		thread2.start()


		service_url = self.localservice_url + '?cmd='+self.cmd
		#print(service_url)
		#self.panel.append('DEBUG: request to '+service_url)

		request = ITDCRequest(service_url)
		if (request.isError()):
			thread2.stop()
			stderr = "Error: "+request.getError()
			elapsed = "\n= = = = = = = = = = = = = = =\nExecution time: %.3f sec" % round((time.time() - self.start_time), 3)
			txt = stderr + elapsed
			self.panel.replace(txt)
			self.panel.finish()
			return False
		json_data = request.getJSON()


		#self.panel.append(' Success', False)

		thread2.stop()

		elapsed = "\n= = = = = = = = = = = = = = =\nExecution time: %.3f sec" % round((time.time() - self.start_time), 3)
		status = json_data['status']
		msg = json_data['msg'] + elapsed
		if (status == "ERROR"):
			msg = "Error: "+msg

		self.panel.replace(msg)
		self.panel.finish()


	def isRunning(self):
		return self.running


