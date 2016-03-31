"""CfP Manager - check for speaker record"""

import webapp2
import urllib
import json
from google.appengine.ext import ndb

from models import Speaker
from settings import *


class SpeakerHandler(webapp2.RequestHandler):
    def get(self, email):
        """Check if a speaker exists for an email"""
        # search for speaker
        speakers = Speaker.query(Speaker.email == email).iter()
        self.response.headers["Content-Type"] = "application/json"
        if speakers.has_next():
            self.response.set_status(200)
            self.response.out.write("1")
        else:
            self.response.set_status(404)
            self.response.out.write("0")
