#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import re


st_version = 2
if sublime.version() == '' or int(sublime.version()) > 3000:
	st_version = 3

# fix for ST2
cprint = globals()["__builtins__"]["print"]









def plugin_loaded():
	cprint('ITDCHelper: Plugin Initialized')

if st_version == 2:
	plugin_loaded()




class ITDCCompletions(sublime_plugin.EventListener):
	completions = {
			'global': [
				# ArrayHelper
				("ArrayHelper::filter()\t Filter array as key=>value", "ArrayHelper::filter(${1:\$key}, ${2:\$val}, ${3:\$search_array}, ${4:\$equal = 'equal'})$0"),
				("ArrayHelper::toAssoc()\t Get key values from array", "ArrayHelper::toAssoc(${1:\$array}, ${2:\$fields_array}, ${3:\$first_null = false}, ${4:\$delimiter = false})$0"),
				("ArrayHelper::entityFilter()\t Filter entities object array", "ArrayHelper::entityFilter(${1:\$entities_array}, ${2:\$key}, ${3:\$val}, ${4:\$equal = true})$0"),
				("ArrayHelper::convert()\t Convert php array to other language array", "ArrayHelper::convert(${1:\$array}, ${2:\$opts = array()}, ${3:\$format = 'js'})$0"),

				# CryptHelper
				("CryptHelper::encrypt()\t Encrypt string with encryption key", "CryptHelper::encrypt(${1:\$string})$0"),

				# HTMLHelper
				("HTMLHelper::getBootstrapLangDropdown()\t Get bootstrap language dropdown", "HTMLHelper::getBootstrapLangDropdown()$0"),
				("HTMLHelper::getLangDropdown()\t Get language dropdown", "HTMLHelper::getLangDropdown()$0"),
				("HTMLHelper::getLangTabs()\t Get language tabs", "HTMLHelper::getLangTabs(${1:\$lang_array}, ${2:\$url}, ${3:\$active = false}, ${4:\$css = false})$0"),
				("HTMLHelper::getOrderByLink()\t Get order by links", "HTMLHelper::getOrderByLink(${1:\$segment}, ${2:\$field}, ${3:\$text = ''})$0"),
				("HTMLHelper::encodeParams()\t Encode params array for url", "HTMLHelper::encodeParams(${1:\$params})$0"),
				("HTMLHelper::decodeParams()\t Decode params string for url", "HTMLHelper::decodeParams(${1:\$params_string})$0"),
				("HTMLHelper::parseAttributes()\t Parse html attributes", "HTMLHelper::parseAttributes(${1:\$string})$0"),
				("HTMLHelper::langSwitchTo()\t Display language switcher ul->li", "HTMLHelper::langSwitchTo(${1:\$ul_attr = ''})$0"),
				("HTMLHelper::showBlock()\t Show block", "HTMLHelper::showBlock(${1:\$place_id})$0"),
				("HTMLHelper::escape()\t Escape string", "HTMLHelper::escape(${1:\$string}, ${2:\$strip_tags = true})$0"),
				("HTMLHelper::parseBBTags()\t Parse BB tags", "HTMLHelper::parseBBTags(${1:\$text}, ${2:\$tags = array()})$0"),

				# MediaHelper
				("MediaHelper::getThumb()\t Get image thumb", "MediaHelper::getThumb(${1:\$parray}, ${2:\$size = false}, ${3:\$default = 'imgs/no_image.png'})$0"),

				# StringHelper
				("StringHelper::isJson()\t Checks if string has a json format", "StringHelper::isJson(${1:\$string})$0"),

				# Constants
				("BASEPATH\t Constant: Path to system folder", "BASEPATH$0"),
				("FCPATH\t Constant: Path to public_html", "FCPATH$0"),

			],

			# completions in model scope
			'model': [
				#("parent::__construct()\t Call parent constructor", "parent::__construct()$0"),
				("this->add()\t Insert data in table", "this->add(${1:\$data}, ${2:\$debug = false}, ${3:\$check_perms = true})$0"),
				("this->clearTableFieldsCache()\t Clear table fields cache", "this->clearTableFieldsCache()$0"),
				("this->delete()\t Delete data from table", "this->delete(${1:\$options}, [${2:\$debug = false}, ${3:\$check_perms = true}])$0"),
				("this->getEntityName()\t Get entity name", "this->getEntityName([${1:\$name = null}])$0"),
				("this->get()\t Get data", "this->get([${1:\$options}, ${2:\$debug = false}, ${3:\$check_perms = true}])$0"),
				("this->getRow()\t Get row", "this->getRow([${1:\$options}, ${2:\$debug = false}, ${3:\$check_perms = true}])$0"),
				("this->getTableName()\t Get table name", "this->getTableName([${1:\$tbl = null}])$0"),
				("this->getTotal()\t Get total count of data", "this->getTotal()$0"),
				("this->update()\t Update data in table", "this->update(${1:\$data}, ${2:\$options}, [${3:\$debug = false}, ${4:\$check_perms = true}])$0"),

			],

			# completions in controller scope
			'controller': [
				#("parent\:\:__construct()\t Call parent constructor", "parent::__construct()$0"),
				("this->redirect()\t Redirect with status message", "this->redirect(${1:\$url = null}, ${2:\$msg = ''}, ${3:\$msg_type = 'message'})$0"),
			]
	}

	completions_extra = {
			'model': {
				'this->': [
					#("this->redirect()\t Redirect with message", "this->add([${1:url}, ${2:msg}, ${3:msg_type}])$0"),
				]
			},
			'controller': {
				'this->': [
					# load library
					("load->css() \tLoad CSS file", "load->css(${1:path}, [${2:url}, ${3:media}])$0"),
					("load->driver() \tLoad driver", "load->driver(${1:library}, [${2:params}, ${3:object_name}])$0"),
					("load->js() \tLoad JavaScript file", "load->js(${1:path}, [${2:url}])$0"),
					("load->tpl() \tLoad view file", "load->tpl([${1:content}, ${2:toString}, ${3:opts}])$0"),
					("load->view() \tLoad view file", "load->view([${1:view}, ${2:vars}, ${3:return}])$0"),

					# conf library
					("conf->get() \tGet config value", "conf->get(${1:name}, [${2:default}, ${3:description}])$0"),

					# Input library
					("input->get() \tFetch an item from the GET array", "input->get([${1:index}, ${2:xss_clean}])$0"),
					("input->post() \tFetch an item from the POST array", "input->post([${1:index}, ${2:xss_clean}])$0"),
					("input->get_post() \tFetch an item from either the GET array or the POST", "input->get_post([${1:index}, ${2:xss_clean}])$0"),
					("input->cookie() \tFetch an item from the COOKIE array", "input->cookie([${1:index}, ${2:xss_clean}])$0"),


					# messages library
					("message->addError() \tAdd error message", "message->addError(${1:msg})$0"),



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

		cprint(final_comp)

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
