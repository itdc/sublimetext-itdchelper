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


class ItdchelperCreateCmsProjectCommand(sublime_plugin.TextCommand):
	db_host = '192.168.1.33'
	db_user = 'dev'
	db_name = ''
	db_pass = ''


	def run(self, edit):

		self.view.window().show_input_panel('Project Name:', '', lambda s: self.on_done(s), None, None)

	def on_done(self, text):


		thread = ItdchelperCreateCmsProjectProcess(text, self.view)
		thread.start()

		return



	def run2(self, edit):

		status = self.initialize()
		if (not status):
			return show_error("Error occured!")

		conn = pymysql.connect(host=self.db_host, unix_socket='/tmp/mysql.sock', user=self.db_user, passwd=self.db_pass, db=self.db_name, charset='utf8')
		cur = conn.cursor()
		cur.execute("SELECT * FROM app_users")
		for response in cur:
		    print(response)
		cur.close()
		conn.close()

	def is_enabled(self):
		#ret = False
		ret = True


		return ret

	def initialize(self):
		if ((self.db_name != '') and (self.db_pass != '')):
			return True

		project_data = sublime.active_window().project_data()
		project_folder = project_data['folders'][0]['path']
		filename = project_folder+'/app/config/database.php'
		file_object = open(filename, 'r')
		content = file_object.read()
		file_object.close()


		if (self.db_name == ''):
			database = re.findall('\[\'default\'\]\[\'database\'\] = \'(.*)\';\n', content)
			if (len(database) > 0):
				self.db_name = database[0]
			else:
				return False

		if (self.db_pass == ''):
			password = re.findall('\[\'default\'\]\[\'password\'\] = \'(.*)\';\n', content)
			if (len(password) > 0):
				self.db_pass = password[0]
			else:
				return False

		return True

def show_error(text):
    sublime.error_message(u'ITDCHelper\n\n%s' % text)



class ItdchelperCreateCmsProjectProcess(threading.Thread):
	service_url = 'http://tools.site.itdc.ge/project/process.php'
	domain = ''
	view = None
	window = None
	start_time = None

	def __init__(self, text, pview):
		self.start_time = time.time()
		self.domain = text
		self.view = pview
		self.window = self.view.window()
		threading.Thread.__init__(self)


	def run(self):
		if not hasattr(self, 'panel'):
			self.panel = ItdchelperCreateCmsProjectPanel(self.window)


		key = self.getKey()

		self.panel.append('Creating project "'+self.domain+'"')
		self.panel.append('Loading')

		thread2 = ItdchelperCreateCmsProjectLoading(self.panel)
		thread2.start()


		service_url = self.service_url + '?mode=create&name='+self.domain+'&key='+key

		#self.panel.append('DEBUG: request to '+service_url)

		try:
			response = urllib.request.urlopen(service_url).read().decode('utf-8')
			json_data = json.loads(response)
		except Exception as e:
			thread2.stop()

			stderr = str(e)
			elapsed = "\n\n= = = = = = = = = = = = = = =\nExecution time: %.3f sec" % round((time.time() - self.start_time), 3)
			txt = stderr + elapsed
			self.panel.replace(txt)
			return False


		# insert in service.itdc.ge



		thread2.stop()

		elapsed = "\n\n= = = = = = = = = = = = = = =\nExecution time: %.3f sec" % round((time.time() - self.start_time), 3)
		status = json_data['status']
		msg = json_data['msg'] + elapsed


		self.panel.replace(msg)

	def getKey(self):
		chars = "23456789abcdefghijkmnpqrstuvwxyzABCDEFGHKMNPQRSTUVWXYZ"
		key = ''.join(sample(chars, 40))
		return key




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


class ItdchelperCreateCmsProjectPanel(object):
	panel_name = 'ItdchelperCreateCmsProject'
	window = None
	header = 'Create ITDC CMS Project:'+"\n"


	def __init__(self, pwindow):
		self.window = pwindow
		if not hasattr(self, 'output_view'):
			self.output_view = self.window.get_output_panel(self.panel_name)

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


class EraseCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.erase(edit, sublime.Region(0, self.view.size()))