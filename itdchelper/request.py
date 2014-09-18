# @author 		Avtandil Kikabidze aka LONGMAN
# @copyright 		Copyright (c) 2008-2014, Avtandil Kikabidze (akalongman@gmail.com)
# @link 			http://long.ge
# @license 		GNU General Public License version 2 or later;
import sublime, sublime_plugin, os, re, sys

libs_path = os.path.dirname(os.path.realpath(__file__))
if libs_path not in sys.path:
	sys.path.append(libs_path)

import json
import requests


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
			#print('Request: '+url)
			self.response = requests.get(url, timeout=self.timeout, headers=self.headers)
			#print('Response: '+self.response.text)
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
