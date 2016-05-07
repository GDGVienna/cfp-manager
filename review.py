"""CfP Manager - review"""

import webapp2
import jinja2
import urllib
import json
import os
from datetime import datetime
from google.appengine.ext import ndb
from google.appengine.api import users

from models import Conference
from models import Speaker
from models import Proposal
from models import Review

from settings import *

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

class ReviewHandler(webapp2.RequestHandler):
    def get(self, confid):
        user = users.get_current_user()
        if not user:
            login_url = users.create_login_url(self.request.url)
            self.redirect(login_url)
            return
        # get the conference
        conference = Conference.get_by_id(confid)
        # check if the user is an admin
        if user.email() not in conference.reviewers:
        	self.response.out.write("You are not authorized")
        	return
        # get existing proposals
        proposals = Proposal.query(ancestor=conference.key).fetch()
        # get existing reviews
        reviews = Review.query(ancestor=conference.key).fetch()
        # filter by this users
        reviews = [r for r in reviews if r.key.id() == user.email()]
        # add the review to the matching proposal
        for r in reviews:
            for p in proposals:
                if r.key.parent() == p.key:
                    p.review = r
        # set of stuff to display in the template
        template_values = {
            'user': user,
            'logout_url': users.create_logout_url(self.request.url),
            'conference': conference,
            'proposals': proposals,
            'reviews': reviews,
        }
        # display template with the reviews & proposals
        template = JINJA_ENVIRONMENT.get_template('review.html')
        self.response.write(template.render(template_values))

    def post(self, confid):
        user = users.get_current_user()
        if not user:
            login_url = users.create_login_url(self.request.url)
            self.redirect(login_url)
            return
        # get the conference
        conference = Conference.get_by_id(confid)
        # check if the user is an admin
        if user.email() not in conference.reviewers:
            self.response.out.write("You are not authorized")
            return
        # get proposal id & proposal
        proposal_id = long(self.request.get('proposal_id'))
        proposal = Proposal.get_by_id(id=proposal_id, parent=conference.key)
        if not proposal:
            self.response.out.write("No proposal found for this id (" + str(proposal_id) + ")")
            return
        # get existing review by this user
        review = Review.get_by_id(id=user.email(), parent=proposal.key)
        if not review:
            review = Review(id=user.email(), parent=proposal.key)
        # store value for the review
        review.comment = self.request.get('comment')
        if self.request.get('rating'):
            review.rating = int(self.request.get('rating'))
        # store in Data Store
        review.put()
        # redirect to get
        self.redirect(self.request.url)

