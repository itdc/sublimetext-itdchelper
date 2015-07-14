# @package    ITDCHelper
# @author       Avtandil Kikabidze aka LONGMAN
# @copyright   Copyright (c) 2008-2015, Avtandil Kikabidze (akalongman@gmail.com)
# @link            http://long.ge
# @license       http://opensource.org/licenses/mit-license.php  The MIT License (MIT)

import sublime, sublime_plugin, os, re, sys

directory = os.path.dirname(os.path.realpath(__file__))
libs_path = os.path.join(directory, "itdchelper")

if libs_path not in sys.path:
    sys.path.append(libs_path)

import pymysql

class ItdcHelperCreateModuleCommand(sublime_plugin.TextCommand):
    db_host = '192.168.1.33'
    db_user = 'dev'
    db_name = ''
    db_pass = ''

    def run(self, edit):

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
