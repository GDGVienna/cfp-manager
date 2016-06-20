"""CfP Manager - backup"""

import webapp2
import json
from datetime import datetime
from google.appengine.ext import ndb

from models import Conference
from models import Speaker
from models import Proposal
from models import Review

from settings import *


class DatastoreEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ndb.Key):
            return "kind=" + obj.kind() + ",id=" + str(obj.id())
        return json.JSONEncoder.default(self, obj)


class BackupHandler(webapp2.RequestHandler):
    def get(self, confid, secret):
        """Download all speakers and proposals for a conference"""
        # Super-Reviewers
        committee = []
        if confid == 'droidcon-2016':
            committee = ['peda.riegler@gmail.com',
                         'klemens.zleptnig@gmail.com']
        # get conference
        conference = Conference.get_by_id(confid)
        # check if the provided secret is correct
        if conference.secret != secret:
            self.response.http_status_message(403)
            return
        speakers = Speaker.query()
        proposals = Proposal.query(ancestor=conference.key)
        reviews = Review.query()
        speakers_dict = [dict(s.to_dict(), **dict(id=s.key.id()))
                         for s in speakers]
        proposals_dict = []
        for p in proposals:
            p_dict = p.to_dict()
            p_dict['id'] = p.key.id()
            p_r = {}
            p_sum = 0
            for r in reviews:
                if r.key.parent() == p.key:
                    p_r[r.key.id()] = r.to_dict()
                    if r.rating:
                        if r.key.id() in committee:
                            # double the rating!
                            p_sum = p_sum + r.rating
                        p_sum = p_sum + r.rating
            for s in speakers:
                if s.key == p.speaker:
                    p_dict['speaker-email'] = s.email
                    p_dict['speaker-name'] = s.name
                    p_dict['speaker-surname'] = s.surname
                    if s.rating:
                        p_sum = p_sum + s.rating
            p_dict['reviews'] = p_r
            p_dict['rating'] = p_sum
            proposals_dict.append(p_dict)
        self.response.headers['Content-Type'] = 'application/json'
        obj = {
            'speakers': speakers_dict,
            'proposals': proposals_dict,
        }
        self.response.out.write(json.dumps(obj, cls=DatastoreEncoder))
