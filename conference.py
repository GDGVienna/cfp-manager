"""CfP Manager - manage conferences"""

import webapp2
import jinja2
import urllib
import json
import os
from datetime import datetime
from google.appengine.ext import ndb
from google.appengine.api import users

from models import Conference

from settings import *

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

class ConferenceHandler(webapp2.RequestHandler):
    def get(self, confid='none'):
        user = users.get_current_user()
        if not user:
            login_url = users.create_login_url('/')
            self.redirect(login_url)
            return
        # check if the user is admin
        if not users.is_current_user_admin():
            self.response.out.write("You are not authorized")
            return
        # list existing conferences
        conferences = Conference.query().fetch()
        # set of stuff to display in the template
        template_values = {
            'user': user,
            'logout_url': users.create_logout_url('/'),
            'conferences': conferences,
        }
        # display template with the reviews & proposals
        template = JINJA_ENVIRONMENT.get_template('conferences.html')
        self.response.write(template.render(template_values))

    def post(self, confid=''):
        user = users.get_current_user()
        if not user:
            login_url = users.create_login_url('/')
            self.redirect(login_url)
            return
        # check if the user is admin
        if not users.is_current_user_admin():
            self.response.out.write("You are not authorized")
            return
        # get conference
        if not confid:
            confid = self.request.get('id')
        conference = Conference.get_by_id(confid)
        if not conference:
            conference = Conference(id=confid)
        # update fields of the conference
        conference.name = self.request.get('name')
        conference.subtitle = self.request.get('subtitle')
        conference.reviewers = self.request.get('reviewers').split()
        # put the changes conference element
        conference.put()
        # redirect to the get page
        self.redirect(self.request.url)