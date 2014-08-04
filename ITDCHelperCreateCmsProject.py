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
	service_url = 'http://tools.local.itdc.ge/project/process.php'
	domain = ''
	view = None
	window = None

	def __init__(self, text, pview):
		self.domain = text
		self.view = pview
		self.window = self.view.window()
		threading.Thread.__init__(self)


	def run(self):
		if not hasattr(self, 'panel'):
			self.panel = ItdchelperCreateCmsProjectPanel(self.window)


		key = self.getKey()
		self.panel.append('Loading...')



		service_url = self.service_url + '?mode=create&name='+self.domain+'&key='+key

		try:
			response = urllib.request.urlopen(service_url, timeout=3600).read().decode('utf-8')
			json_data = json.loads(response)
		except Exception as e:
			stderr = str(e)
			txt = 'Create ITDC CMS Project:'+"\n\nError: "+stderr
			self.panel.replace(txt)
			return False


		status = json_data['status']
		msg = json_data['msg']
		self.panel.replace(msg)

	def getKey(self):
		chars = "23456789abcdefghijkmnpqrstuvwxyzABCDEFGHKMNPQRSTUVWXYZ"
		key = ''.join(sample(chars, 40))
		return key



class ItdchelperCreateCmsProjectPanel(object):
	window = None
	header = 'Create ITDC CMS Project:'+"\n"


	def __init__(self, pwindow):
		panel_name = 'ItdchelperCreateCmsProject'
		self.window = pwindow
		if not hasattr(self, 'output_view'):
			self.output_view = self.window.get_output_panel(panel_name)

		self.window.run_command('show_panel', {'panel': 'output.'+panel_name})
		self.add(self.header)

	def add(self, text):
		self.output_view.run_command('append', {'characters': text})

	def append(self, text):
		self.output_view.run_command('append', {'characters': "\n"+text})

	def replace(self, text):
		self.erase()
		self.add(self.header)
		self.add("\n"+text)


	def erase(self):
		self.output_view.run_command('erase')


class EraseCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.erase(edit, sublime.Region(0, self.view.size()))