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
import time


class ItdchelperLoading(threading.Thread):
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
