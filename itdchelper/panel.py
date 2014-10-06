# @author 		Avtandil Kikabidze aka LONGMAN
# @copyright 		Copyright (c) 2008-2014, Avtandil Kikabidze (akalongman@gmail.com)
# @link 			http://long.ge
# @license 		GNU General Public License version 2 or later;

import sublime, sublime_plugin, os, re, sys

directory = os.path.dirname(os.path.realpath(__file__))
libs_path = os.path.join(directory, "itdchelper")

if libs_path not in sys.path:
	sys.path.append(libs_path)



class ItdchelperProjectPanel(object):
	panel_name = ''
	window = None
	header = ''
	theme = 'Packages/ITDCHelper/itdchelper/ITDCHelper.hidden-tmTheme'
	syntax = 'Packages/ITDCHelper/itdchelper/ITDCHelper.hidden-tmLanguage'

	def __init__(self, pwindow, pname, pheader):
		self.panel_name = pname
		self.header = pheader
		self.window = pwindow
		if not hasattr(self, 'output_view'):
			self.output_view = self.window.get_output_panel(self.panel_name)

		self.output_view.set_read_only(False)
		self.output_view.run_command('set_setting', {"setting": 'word_wrap', "value": True})
		self.output_view.run_command('set_setting', {"setting": 'wrap_width', "value": 80})
		self.output_view.run_command('set_setting', {"setting": 'font_size', "value": 11})
		self.output_view.run_command('set_setting', {"setting": 'line_numbers', "value": False})



		self.output_view.settings().set("color_scheme", self.theme)
		self.output_view.set_syntax_file(self.syntax)

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


