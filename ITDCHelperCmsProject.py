# @author 		Avtandil Kikabidze aka LONGMAN
# @copyright 		Copyright (c) 2008-2014, Avtandil Kikabidze (akalongman@gmail.com)
# @link 			http://long.ge
# @license 		GNU General Public License version 2 or later;

import sublime, sublime_plugin, os, re, sys

directory = os.path.dirname(os.path.realpath(__file__))
libs_path = os.path.join(directory, "itdchelper")

if libs_path not in sys.path:
	sys.path.append(libs_path)

import pymysql
import urllib.request
import json
import threading
from random import sample
import time

import requests

settings = sublime.load_settings('ITDCHelper.sublime-settings')

def show_error(text):
    sublime.error_message(u'ITDCHelper\n\n%s' % text)


class ItdchelperProjectPanel(object):
	panel_name = ''
	window = None
	header = ''

	def __init__(self, pwindow, pname, pheader):
		self.panel_name = pname
		self.header = pheader
		self.window = pwindow
		if not hasattr(self, 'output_view'):
			self.output_view = self.window.get_output_panel(self.panel_name)

		self.output_view.set_read_only(False)
		self.output_view.run_command('set_setting', {"setting": 'word_wrap', "value": True})
		self.output_view.run_command('set_setting', {"setting": 'wrap_width', "value": 80})

		self.show()
		self.addHeader()


	def show(self):
		self.window.run_command('show_panel', {'panel': 'output.'+self.panel_name})


	def add(self, text):
		self.show()
		self.output_view.run_command('append', {'characters': text})

	def addHeader(self):
		self.add(self.header)




	def append(self, text, new_line=True):
		self.show()
		if (new_line):
			self.output_view.run_command('append', {'characters': "\n"+text})
		else:
			self.output_view.run_command('append', {'characters': text})

		self.output_view.run_command('move', {"by": "lines", "forward": True})




	def replace(self, text):
		self.show()
		self.erase()
		self.addHeader()
		self.add("\n"+text)


	def erase(self):
		self.show()
		self.output_view.run_command('erase')

	def finish(self):
		self.output_view.set_read_only(True)




class EraseCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.erase(edit, sublime.Region(0, self.view.size()))



class ITDCRequest(object):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding': 'gzip,deflate,sdch',
		'Accept-Language': 'en-US,en;q=0.8,ka;q=0.6,ru;q=0.4',
	}
	timeout = 120
	response = None
	error = False
	stderr = ''
	json = ''

	def __init__(self, url):
		try:
			self.response = requests.get(url, timeout=self.timeout, headers=self.headers)
			print('Response: '+self.response.text)
			self.json = self.response.json()
		except Exception as e:
			self.error = True
			self.stderr = str(e)

	def isError(self):
		return self.error == True

	def getError(self):
		return self.stderr

	def getJSON(self):
		return self.json





### Create CMS Project
class ItdchelperCreateCmsProjectCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.window().show_input_panel('Project Name to Create:', '', lambda s: self.on_done(s), None, None)

	def on_done(self, text):
		thread = ItdchelperCreateCmsProjectProcess(text, self.view, settings)
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


	def __init__(self, text, pview, psettings):
		self.settings = psettings
		self.start_time = time.time()
		self.domain = text
		self.view = pview
		self.window = self.view.window()

		api_key = settings.get('api_key')
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

		thread2 = ItdchelperCreateCmsProjectLoading(self.panel)
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


class ItdchelperCreateCmsProjectLoading(threading.Thread):
	panel = None
	running = False

	def __init__(self, ppanel):
		self.panel = ppanel
		self.running = True
		threading.Thread.__init__(self)


	def run(self):

		for i in range(1000000):
			time.sleep(0.3)
			if not self.running:
				break
			self.panel.append(".", False)

	def stop(self):
		self.running = False



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

		thread = ItdchelperDeleteCmsProjectProcess(self.project, self.view, settings)
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

	def __init__(self, text, pview, psettings):
		self.settings = psettings
		self.start_time = time.time()
		self.domain = text
		self.view = pview
		self.window = self.view.window()

		api_key = settings.get('api_key')
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

		thread2 = ItdchelperCreateCmsProjectLoading(self.panel)
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

class ItdchelperDeleteCmsProjectLoading(threading.Thread):
	panel = None
	running = False

	def __init__(self, ppanel):
		self.panel = ppanel
		self.running = True
		threading.Thread.__init__(self)

	def run(self):

		for i in range(1000000):
			time.sleep(0.3)
			if not self.running:
				break
			self.panel.append(".", False)

	def stop(self):
		self.running = False

