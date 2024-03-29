#!/usr/bin/env python

import requests
import time
import math

try:
    import simplejson as json
except ImportError:
    import json
from pprint import pprint

import base64

class GitlabAPI(object):
    """Basic wrapper for the Gitlab api. For further information on the API
    itself see: http://developer.gitlab.com/documentation/
    """

    def __init__(self, apikey, debug=False):
        self.debug = debug
        self.gitlab_url = "https://app.gitlab.com/api"
        self.api_version = "1.0"
        self.aurl = "/".join([self.gitlab_url, self.api_version])
        self.apikey = apikey
        self.bauth = self.get_basic_auth()

    def get_basic_auth(self):
        """Get basic auth creds
        :returns: the basic auth string
        """
        s = self.apikey + ":"
        return base64.b64encode(s.encode('utf-8')).rstrip()

    def _gitlab(self, api_target):
        """Peform a GET request

        :param <api_target:></api_target:> API URI path for request
        """
        target = "/".join([self.aurl, api_target])

        if self.debug:
            pprint("-> Calling: %s" % target)

        r = requests.get(target, auth=(self.apikey, ""), verify=False)

        if self._ok_status(r.status_code) and r.status_code is not 404:
            if r.headers['content-type'].split(';')[0] == 'application/json':
                return json.loads(r.text)['data']
            else:
                raise Exception('Did not receive json from api: %s' % str(r))
        else:
            if self.debug:
                pprint("-> Got: %s" % r.status_code)
                pprint("-> %s" % r.text)
            raise Exception('Received non 2xx or 404 status code on call')

    def _gitlab_post(self, api_target, data):
        """Peform a POST request

        :param api_target: API URI path for request
        :param data: POST payload
        """
        target = "/".join([self.aurl, api_target])
        if self.debug:
            pprint("-> Posting to: %s" % target)
            pprint("-> Post payload:")
            pprint(data)
        r = requests.post(target, auth=(self.apikey, ""), data=data, verify=False)
        if self._ok_status(r.status_code) and r.status_code is not 404:
            if r.headers['content-type'].split(';')[0] == 'application/json':
                return json.loads(r.text)['data']
            else:
                raise Exception('Did not receive json from api: %s' % str(r))
        else:
            if self.debug:
                pprint("-> Got: %s" % r.status_code)
                pprint("-> %s" % r.text)
            raise Exception("Gitlab API error: %s" % r.text)

    def _gitlab_put(self, api_target, data):
        """Peform a PUT request

        :param api_target: API URI path for request
        :param data: PUT payload
        """
        target = "/".join([self.aurl, api_target])
        if self.debug:
            pprint("-> PUTting to: %s" % target)
            pprint("-> PUT payload:")
            pprint(data)
        r = requests.put(target, auth=(self.apikey, ""), data=data, verify=False)
        if self._ok_status(r.status_code) and r.status_code is not 404:
            if r.headers['content-type'].split(';')[0] == 'application/json':
                return json.loads(r.text)['data']
            else:
                raise Exception('Did not receive json from api: %s' % str(r))
        else:
            if self.debug:
                pprint("-> Got: %s" % r.status_code)
                pprint("-> %s" % r.text)
            raise Exception("Gitlab API error: %s" % r.text)

    @classmethod
    def _ok_status(cls, status_code):
        """Check whether status_code is a ok status i.e. 2xx or 404"""

        if math.floor(status_code / 200) == 1:
            return True
        elif math.floor(status_code / 400) == 1:
            if status_code == 404:
                return True
            else:
                return False
        elif status_code == 500:
            return False

    def user_info(self, user_id="me"):
        """Obtain user info on yourself or other users.

        :param user_id: target user or self (default)
        """
        return self._gitlab('users/%s' % user_id)

    def list_users(self, workspace=None, filters=None):
        """List users

        :param workspace: list users in given workspace
        :param filters: Optional [] of filters you want to apply to listing
        """
        if workspace:
            return self._gitlab('workspaces/%s/users' % workspace)
        else:
            if filters:
                fkeys = [x.strip().lower() for x in filters]
                fields = ",".join(fkeys)
                return self._gitlab('users?opt_fields=%s' % fields)
            else:
                return self._gitlab('users')

    def list_tasks(self, workspace, assignee):
        """List tasks

        :param workspace: workspace id
        :param assignee: assignee
        """
        target = "tasks?workspace=%d&assignee=%s" % (workspace, assignee)
        return self._gitlab(target)

    def get_task(self, task_id):
        """Get a task

        :param task_id: id# of task"""
        return self._gitlab("tasks/%d" % task_id)

    def list_projects(self, workspace=None):
        """"List projects in a workspace

        :param workspace: workspace whos projects you want to list"""
        if workspace:
            return self._gitlab('workspaces/%d/projects' % workspace)
        else:
            return self._gitlab('projects/?opt_fields=workspace,name,archived')

    def get_project(self, project_id):
        """Get project

        :param project_id: id# of project
        """
        return self._gitlab('projects/%d/' % project_id)

    def get_project_tasks(self, project_id):
        """Get project tasks

        :param project_id: id# of project
        """

        return self._gitlab('projects/%d/tasks?opt_fields=completed,name' % project_id)

    def list_stories(self, task_id):
        """List stories for task

        :param task_id: id# of task
        """
        return self._gitlab('tasks/%d/stories' % task_id)

    def get_story(self, story_id):
        """Get story

        :param story_id: id# of story
        """
        return self._gitlab('stories/%d' % story_id)

    def list_workspaces(self):
        """List workspaces"""
        return self._gitlab('workspaces')

    def create_task(self, name, workspace, assignee=None, assignee_status=None,
                    completed=False, due_on=None, followers=None, notes=None):
        """Create a new task

        :param name: Name of task
        :param workspace: Workspace for task
        :param assignee: Optional assignee for task
        :param assignee_status: status
        :param completed: Whether this task is completed (defaults to False)
        :param due_on: Optional due date for task
        :param followers: Optional followers for task
        :param notes: Optional notes to add to task
        """
        payload = {'assignee': assignee or 'me', 'name': name,
                   'workspace': workspace}
        if assignee_status in ['inbox', 'later', 'today', 'upcoming']:
            payload['assignee_status'] = assignee_status
        if completed:
            payload['completed'] = 'true'
        if due_on:
            try:
                time.strptime(due_on, '%Y-%m-%d')
                payload['due_on'] = due_on
            except ValueError:
                raise Exception('Bad task due date: %s' % due_on)
        if followers:
            for pos, person in enumerate(followers):
                payload['followers[%d]' % pos] = person
        if notes:
            payload['notes'] = notes

        return self._gitlab_post('tasks', payload)

    def update_task(self, task, name=None, assignee=None, assignee_status=None,
                    completed=False, due_on=None, notes=None):
        """Update an existing task

        :param task: task to update
        :param name: Update task name
        :param assignee: Update assignee
        :param assignee_status: Update status
        :param completed: Update whether the task is completed
        :param due_on: Update due date
        :param notes: Update notes
        """
        payload = {}
        if name:
            payload['name'] = name
        if assignee:
            payload['assignee'] = assignee
        if assignee_status:
            payload['assignee_status'] = assignee_status
        if completed:
            payload['completed'] = completed
        if due_on:
            try:
                time.strptime(due_on, '%Y-%m-%d')
                payload['due_on'] = due_on
            except ValueError:
                raise Exception('Bad task due date: %s' % due_on)
        if notes:
            payload['notes'] = notes

        return self._gitlab_put('tasks/%s' % task, payload)

    def create_project(self, name, workspace, notes=None, archived=False):
        """Create a new project

        :param name: Name of project
        :param workspace: Workspace for task
        :param notes: Optional notes to add
        :param archived: Whether or not project is archived (defaults to False)
        """
        payload = {'name': name, 'workspace': workspace}
        if notes:
            payload['notes'] = notes
        if archived:
            payload['archived'] = 'true'
        return self._gitlab_post('projects', payload)

    def update_project(self, project_id, name=None, notes=None,
                       archived=False):
        """Update project

        :param project_id: id# of project
        :param name: Update name
        :param notes: Update notes
        :param archived: Update archive status
        """
        payload = {}
        if name:
            payload['name'] = name
        if notes:
            payload['notes'] = notes
        if archived:
            payload['archived'] = 'true'
        return self._gitlab_put('projects/%s' % project_id, payload)

    def update_workspace(self, workspace_id, name):
        """Update workspace

        :param workspace_id: id# of workspace
        :param name: Update name
        """
        payload = {'name': name}
        return self._gitlab_put('workspaces/%s' % workspace_id, payload)

    def add_project_task(self, task_id, project_id):
        """Add project task

        :param task_id: id# of task
        :param project_id: id# of project
        """
        return self._gitlab_post('tasks/%d/addProject' % task_id,
                                {'project': project_id})

    def rm_project_task(self, task_id, project_id):
        """Remove a project from task

        :param task_id: id# of task
        :param project_id: id# of project
        """
        return self._gitlab_post('tasks/%d/removeProject' % task_id,
                                {'project': project_id})

    def add_story(self, task_id, text):
        """Add a story to task

        :param task_id: id# of task
        :param text: story contents
        """
        return self._gitlab_post('tasks/%d/stories' % task_id, {'text': text})

    def add_tag_task(self, task_id, tag_id):
        """Tag a task

        :param task_id: id# of task
        :param tag_id: id# of tag to add
        """
        return self._gitlab_post('tasks/%d/addTag' % task_id, {'tag': tag_id})

    def get_tags(self, workspace):
        """Get available tags for workspace

        :param workspace: id# of workspace
        """
        return self._gitlab('workspaces/%d/tags' % workspace)

    def get_tag_tasks(self, tag_id):
        """Get tasks for a tag

        :param tag_id: id# of task
        """
        return self._gitlab('tags/%d/tasks' % tag_id)
