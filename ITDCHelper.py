# @author 		Avtandil Kikabidze aka LONGMAN
# @copyright 		Copyright (c) 2008-2014, Avtandil Kikabidze (akalongman@gmail.com)
# @link 			http://long.ge
# @license 		GNU General Public License version 2 or later;

import sublime
import sublime_plugin
import re
import sys
import imp

st_version = 2
if sublime.version() == '' or int(sublime.version()) > 3000:
	st_version = 3

from ITDCHelper.itdchelper.functions import *
from ITDCHelper.itdchelper.panel import ItdchelperProjectPanel
from ITDCHelper.itdchelper.request import ITDCRequest
from ITDCHelper.itdchelper.loading import ItdchelperLoading
from ITDCHelper.itdchelper.commands import EraseCommand


# fix for ST2
cprint = globals()["__builtins__"]["print"]


def plugin_loaded():
	cprint('ITDCHelper: Plugin Initialized')
	#print(sublime.active_window().project_data())

if st_version == 2:
	plugin_loaded()




class ITDCCompletions(sublime_plugin.EventListener):
	completions = {
			'global': [
			],

			# completions in model scope
			'model': [
			],

			# completions in controller scope
			'controller': [
			]
	}

	completions_extra = {
			'model': {
				'this->': [
				]
			},
			'controller': {
				'this->': [
				]
			},
	}




	def on_query_completions1(self, view, prefix, locations):
		completions = self.completions
		if not view.match_selector(locations[0], "source.php"):
			#cprint("ITDC: not php scope!")
			return []

		#cprint("CALLED!")


		proposals = []
		if len(locations) > 0:
			proposals = view.extract_completions(prefix, locations[0])
		else:
			proposals = view.extract_completions(prefix)


		file_text = sublime.Region(0, view.size())
		file_text_utf = view.substr(file_text)

		# cprint('Default:')
		# cprint(proposals)

		final_comp = []
		final_comp.extend(completions['global'])


		find = re.findall(r'extends\s[a-zA-Z_]+(Model|Controller)', file_text_utf)
		for classtype in find:
			classtype = classtype.lower()
			if (classtype in completions):
				final_comp.extend(completions[classtype])
				#proposals = list(set(proposals))

		#cprint("Prefix: "+prefix)
		# cprint('Changed:')
		# cprint(proposals)
		for pp in proposals:
			final_comp.append((pp, pp))

		#cprint(final_comp)

		#final_comp.extend(proposals)


		# proposals.append(("abs2\tabs2 fn", "abs2(${1:number})$0"),)

		completion_flags = 0
		#completion_flags = sublime.INHIBIT_WORD_COMPLETIONS
		#completion_flags |= sublime.INHIBIT_EXPLICIT_COMPLETIONS

		#@TODO: fix sort
		#proposals.sort(key=lambda tup: tup[1])
		#sorted(proposals, key=keyfunction)

		return (final_comp, completion_flags)

	def on_modified_async1(self, view):
		completions = self.completions
		completions_extra = self.completions_extra

		view_sel = view.sel()
		sel = view_sel[0]
		pos = sel.end()

		if not view.match_selector(pos, "source.php"):
			cprint("ITDC: not php scope!")
			return []

		show_autocomplete = False


		text = view.substr(sublime.Region(pos - 6, pos))
		if text == 'this->':
			show_autocomplete = True
			self.completions['controller'].extend(completions_extra['controller'][text])
			self.completions['controller'] = list(set(self.completions['controller']))

			self.completions['model'].extend(completions_extra['model'][text])
			self.completions['model'] = list(set(self.completions['model']))




		#cprint(compl)
		if not show_autocomplete:
			return


		view.run_command('auto_complete', {
		                            'disable_auto_insert': True,
		                            'api_completions_only': False,
		                            'next_completion_if_showing': False,
		                            'auto_complete_commit_on_tab': True,
		                        })





def keyfunction(x):
	v = x[0]
	if isinstance(v, int): v = '0%d' % v
	return v












