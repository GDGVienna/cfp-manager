"""CfP Manager - backup"""

import webapp2
import urllib
import json
from datetime import datetime
from google.appengine.ext import ndb

from models import Conference
from models import Speaker
from models import Proposal

from settings import *


class DatastoreEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ndb.Key):
            return "kind=" + obj.kind() + ",id=" + str(obj.id())
        return json.JSONEncoder.default(self, obj)

class BackupHandler(webapp2.RequestHandler):
    def get(self, confid):
        """Download all speakers and proposals for a conference"""
        # get conference
        conference = Conference.get_by_id(confid)
        # check if the provided secret is correct
        if conference.secret != self.request.get("secret"):
            self.response.http_status_message(403)
            return
        speakers = Speaker.query()
	proposals = Proposal.query(ancestor=conference.key)
        speakers_dict = [dict(s.to_dict(), **dict(id=s.key.id()))
                         for s in speakers]
        proposals_dict = [dict(p.to_dict(), **dict(id=p.key.id()))
                         for p in proposals]
        self.response.headers['Content-Type'] = 'application/json'
        obj = {
            'speakers': speakers_dict,
            'proposals': proposals_dict,
          }
        self.response.out.write(json.dumps(obj, cls=DatastoreEncoder))
