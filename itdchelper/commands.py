# @author 		Avtandil Kikabidze aka LONGMAN
# @copyright 		Copyright (c) 2008-2014, Avtandil Kikabidze (akalongman@gmail.com)
# @link 			http://long.ge
# @license 		GNU General Public License version 2 or later;

import sublime, sublime_plugin

class EraseCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.erase(edit, sublime.Region(0, self.view.size()))

