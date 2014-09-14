import sublime, sublime_plugin, os, re, sys, tempfile
import threading, subprocess, http.server, socketserver

directory = os.path.dirname(os.path.realpath(__file__))
libs_path = os.path.join(directory, "itdchelper")

if libs_path not in sys.path:
	sys.path.append(libs_path)

class ItdchelperOpenFileCommand(sublime_plugin.WindowCommand):
	def run(self,path):
		self.window.open_file(path,1)

class Handler(http.server.BaseHTTPRequestHandler):
	def do_GET(s):
		if re.match('^/edit/', s.path):
			path = re.sub('^/edit/', '', s.path)
			sublime.active_window().run_command('itdchelper_open_file',{'path':path})
		s.send_response(200)
		s.send_header("Content-type", "text/plain")
		s.end_headers()
		s.wfile.write(bytes("OK", 'UTF-8'))
	def log_message(*m):
		return

def HttpServerThread():
	httpd = socketserver.TCPServer(("", 8881), Handler)
	httpd.serve_forever()

threading.Thread(target=HttpServerThread).start()




