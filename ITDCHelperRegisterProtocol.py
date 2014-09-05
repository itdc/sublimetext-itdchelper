
import sublime, sublime_plugin, os, re, sys, tempfile

directory = os.path.dirname(os.path.realpath(__file__))
libs_path = os.path.join(directory, "itdchelper")

if libs_path not in sys.path:
	sys.path.append(libs_path)

# Here your code



class OpenFileFromUrlCommand(sublime_plugin.WindowCommand):
	def run(self,url):
		replaced = re.sub('^subl://', '', url)
		self.window.open_file(replaced,1)

def plugin_loaded():
	return

def plugin_unloaded():
	return

