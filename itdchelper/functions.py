# @author 		Avtandil Kikabidze aka LONGMAN
# @copyright 		Copyright (c) 2008-2014, Avtandil Kikabidze (akalongman@gmail.com)
# @link 			http://long.ge
# @license 		GNU General Public License version 2 or later;

import sublime, sublime_plugin

def show_error(text):
    sublime.error_message(u'ITDCHelper\n\n%s' % text)
