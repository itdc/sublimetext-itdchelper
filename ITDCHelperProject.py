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



### Create CMS Project
class ItdchelperCreateCmsProjectCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.window().show_input_panel('Project Name to Create:', '', lambda s: self.on_done(s), None, None)

	def on_done(self, text):
		thread = ItdchelperCreateCmsProjectProcess(text, self.view)
		thread.start()
		return

	def is_enabled(self):
		ret = True
		return ret


class ItdchelperCreateCmsProjectProcess(threading.Thread):
	settings = None
	localservice_url = ''
	remoteservice_url = ''
	domain = ''
	view = None
	window = None
	start_time = None


	def __init__(self, text, pview):
		self.settings = sublime.load_settings('ITDCHelper.sublime-settings')
		self.start_time = time.time()
		self.domain = text
		self.view = pview
		self.window = self.view.window()

		api_key = self.settings.get('api_key')
		if ((api_key is None) or (len(api_key) != 40)):
			show_error("API KEY not found")
			return

		self.localservice_url = 'http://tools.local.itdc.ge/project/process.php'
		self.remoteservice_url = 'http://service.itdc.ge/api/addproject/token/'+api_key

		threading.Thread.__init__(self)



	def run(self):
		if not hasattr(self, 'panel'):
			self.panel = ItdchelperProjectPanel(self.window, 'ItdchelperCreateCmsProject', 'Create ITDC CMS Project:'+"\n")

		key = self.getKey()

		self.panel.append('Creating project "'+self.domain+'"')
		self.panel.append('Loading')

		thread2 = ItdchelperLoading(self.panel)
		thread2.start()


		service_url = self.localservice_url + '?mode=create&name='+self.domain+'&key='+key

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

		# insert in service.itdc.ge

		service_url = self.remoteservice_url + '/name/'+self.domain+'/key/'+key

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
		json_data2 = request.getJSON()

		#self.panel.append(' Success', False)

		thread2.stop()

		elapsed = "\n= = = = = = = = = = = = = = =\nExecution time: %.3f sec" % round((time.time() - self.start_time), 3)
		status = json_data['status']
		msg = json_data['msg'] + elapsed
		if (status == "ERROR"):
			msg = "Error: "+msg

		self.panel.replace(msg)
		self.panel.finish()

	def getKey(self):
		chars = "23456789abcdefghijkmnpqrstuvwxyzABCDEFGHKMNPQRSTUVWXYZ"
		key = ''.join(sample(chars, 40))
		return key

	def isRunning(self):
		return self.running



### Delete CMS Project
class ItdchelperDeleteCmsProjectCommand(sublime_plugin.TextCommand):
	project = ''
	def run(self, edit):

		self.view.window().show_input_panel('Project Name to Delete:', '', lambda s: self.on_done(s), None, None)

	def on_done(self, text):
		self.project = text

		items = []
		item = []
		item.append('Yes, delete')
		item.append('Delete project '+self.project)
		items.append(item)

		item = []
		item.append('No')
		item.append('Cancel operation')
		items.append(item)

		self.view.window().show_quick_panel(items, self.on_done_final)
		return

	def on_done_final(self, choice):
		if (choice == 1 or choice == -1):
			return

		thread = ItdchelperDeleteCmsProjectProcess(self.project, self.view)
		thread.start()

	def is_enabled(self):
		ret = True
		return ret


class ItdchelperDeleteCmsProjectProcess(threading.Thread):
	settings = None
	localservice_url = ''
	remoteservice_url = ''
	domain = ''
	view = None
	window = None
	start_time = None

	def __init__(self, text, pview):
		self.settings = sublime.load_settings('ITDCHelper.sublime-settings')
		self.start_time = time.time()
		self.domain = text
		self.view = pview
		self.window = self.view.window()

		api_key = self.settings.get('api_key')
		if ((api_key is None) or (len(api_key) != 40)):
			show_error("API KEY not found")
			return

		self.localservice_url = 'http://tools.local.itdc.ge/project/process.php'
		self.remoteservice_url = 'http://service.itdc.ge/api/deleteproject/token/'+api_key

		threading.Thread.__init__(self)


	def run(self):
		if not hasattr(self, 'panel'):
			self.panel = ItdchelperProjectPanel(self.window, 'ItdchelperDeleteCmsProject', 'Delete ITDC CMS Project:'+"\n")

		self.panel.append('Deleting project "'+self.domain+'"')
		self.panel.append('Loading')

		thread2 = ItdchelperLoading(self.panel)
		thread2.start()


		service_url = self.localservice_url + '?mode=delete&name='+self.domain

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

		# insert in service.itdc.ge

		service_url = self.remoteservice_url + '/name/'+self.domain

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
		json_data2 = request.getJSON()

		#self.panel.append(' Success', False)


		thread2.stop()

		elapsed = "\n= = = = = = = = = = = = = = =\nExecution time: %.3f sec" % round((time.time() - self.start_time), 3)
		status = json_data['status']
		msg = json_data['msg'] + elapsed
		if (status == "ERROR"):
			msg = "Error: "+msg

		self.panel.replace(msg)
		self.panel.finish()


### Backup CMS Project
class ItdchelperBackupCmsProjectCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		self.view.window().show_input_panel('Project Name to Backup:', '', lambda s: self.on_done(s), None, None)

	def on_done(self, text):
		thread = ItdchelperBackupCmsProjectProcess(text, self.view)
		thread.start()
		return

	def is_enabled(self):
		ret = True
		return ret


class ItdchelperBackupCmsProjectProcess(threading.Thread):
	settings = None
	localservice_url = ''
	domain = ''
	view = None
	window = None
	start_time = None

	def __init__(self, text, pview):
		self.settings = sublime.load_settings('ITDCHelper.sublime-settings')
		self.start_time = time.time()
		self.domain = text
		self.view = pview
		self.window = self.view.window()



		self.localservice_url = 'http://tools.local.itdc.ge/project/process.php'

		threading.Thread.__init__(self)


	def run(self):
		if not hasattr(self, 'panel'):
			self.panel = ItdchelperProjectPanel(self.window, 'ItdchelperBackupCmsProject', 'Backup ITDC CMS Project:'+"\n")

		self.panel.append('Backuping project "'+self.domain+'"')
		self.panel.append('Loading')

		thread2 = ItdchelperLoading(self.panel)
		thread2.start()


		service_url = self.localservice_url + '?mode=backup&name='+self.domain

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




# = = = = = = = = = = = = = = = = = = =

### Create Empty Project
class ItdchelperCreateEmptyProjectCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.window().show_input_panel('Project Name to Create:', '', lambda s: self.on_done(s), None, None)

	def on_done(self, text):
		thread = ItdchelperCreateEmptyProjectProcess(text, self.view)
		thread.start()
		return

	def is_enabled(self):
		ret = True
		return ret


class ItdchelperCreateEmptyProjectProcess(threading.Thread):
	settings = None
	localservice_url = ''
	domain = ''
	view = None
	window = None
	start_time = None


	def __init__(self, text, pview):
		self.settings = sublime.load_settings('ITDCHelper.sublime-settings')
		self.start_time = time.time()
		self.domain = text
		self.view = pview
		self.window = self.view.window()

		self.localservice_url = 'http://tools.local.itdc.ge/project/process.php'

		threading.Thread.__init__(self)



	def run(self):
		if not hasattr(self, 'panel'):
			self.panel = ItdchelperProjectPanel(self.window, 'ItdchelperCreateEmptyProject', 'Create ITDC Empty Project:'+"\n")


		self.panel.append('Creating project "'+self.domain+'"')
		self.panel.append('Loading')

		thread2 = ItdchelperLoading(self.panel)
		thread2.start()


		service_url = self.localservice_url + '?mode=createhost&name='+self.domain

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



### Delete Empty Project
class ItdchelperDeleteEmptyProjectCommand(sublime_plugin.TextCommand):
	project = ''
	def run(self, edit):

		self.view.window().show_input_panel('Project Name to Delete:', '', lambda s: self.on_done(s), None, None)

	def on_done(self, text):
		self.project = text

		items = []
		item = []
		item.append('Yes, delete')
		item.append('Delete project '+self.project)
		items.append(item)

		item = []
		item.append('No')
		item.append('Cancel operation')
		items.append(item)

		self.view.window().show_quick_panel(items, self.on_done_final)
		return

	def on_done_final(self, choice):
		if (choice == 1 or choice == -1):
			return

		thread = ItdchelperDeleteCmsProjectProcess(self.project, self.view)
		thread.start()

	def is_enabled(self):
		ret = True
		return ret


class ItdchelperDeleteCmsProjectProcess(threading.Thread):
	settings = None
	localservice_url = ''
	domain = ''
	view = None
	window = None
	start_time = None

	def __init__(self, text, pview):
		self.settings = sublime.load_settings('ITDCHelper.sublime-settings')
		self.start_time = time.time()
		self.domain = text
		self.view = pview
		self.window = self.view.window()

		self.localservice_url = 'http://tools.local.itdc.ge/project/process.php'

		threading.Thread.__init__(self)


	def run(self):
		if not hasattr(self, 'panel'):
			self.panel = ItdchelperProjectPanel(self.window, 'ItdchelperDeleteEmptyProject', 'Delete ITDC Empty Project:'+"\n")

		self.panel.append('Deleting project "'+self.domain+'"')
		self.panel.append('Loading')

		thread2 = ItdchelperLoading(self.panel)
		thread2.start()


		service_url = self.localservice_url + '?mode=deletehost&name='+self.domain

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


### Backup Empty Project
class ItdchelperBackupEmptyProjectCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		self.view.window().show_input_panel('Project Name to Backup:', '', lambda s: self.on_done(s), None, None)

	def on_done(self, text):
		thread = ItdchelperBackupEmptyProjectProcess(text, self.view)
		thread.start()
		return

	def is_enabled(self):
		ret = True
		return ret


class ItdchelperBackupEmptyProjectProcess(threading.Thread):
	settings = None
	localservice_url = ''
	domain = ''
	view = None
	window = None
	start_time = None

	def __init__(self, text, pview):
		self.settings = sublime.load_settings('ITDCHelper.sublime-settings')
		self.start_time = time.time()
		self.domain = text
		self.view = pview
		self.window = self.view.window()



		self.localservice_url = 'http://tools.local.itdc.ge/project/process.php'

		threading.Thread.__init__(self)


	def run(self):
		if not hasattr(self, 'panel'):
			self.panel = ItdchelperProjectPanel(self.window, 'ItdchelperBackupEmptyProject', 'Backup ITDC Empty Project:'+"\n")

		self.panel.append('Backuping project "'+self.domain+'"')
		self.panel.append('Loading')

		thread2 = ItdchelperLoading(self.panel)
		thread2.start()


		service_url = self.localservice_url + '?mode=backuphost&name='+self.domain

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




