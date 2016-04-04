"""CfP Manager - proposal submission"""

import webapp2
import urllib
import json
from datetime import datetime

from models import Conference
from models import Speaker
from models import Proposal
from settings import *


class ProposalHandler(webapp2.RequestHandler):
    def success(self):
        """Success return"""
        jsonReply = self.request.get("json-reply")
        if jsonReply:
            self.response.set_status(200)
            self.response.headers["Content-Type"] = "application/json"
            self.response.headers.add_header(
                "Access-Control-Allow-Origin", "*"
            )
            self.response.out.write(json.dumps({"message": "success"}))
        else:
            successUrl = str(self.request.get("success-url"))
            webapp2.redirect(successUrl, response=self.response)

    def error(self, text, status):
        """Error handling"""
        jsonReply = self.request.get("json-reply")
        if jsonReply:
            self.response.set_status(status)
            self.response.headers["Content-Type"] = "application/json"
            self.response.headers.add_header(
                "Access-Control-Allow-Origin", "*"
            )
            self.response.out.write(json.dumps({"message": text}))
        else:
            errorUrl = str(self.request.get("error-url"))
            if "?" in errorUrl:
                errorUrl = errorUrl + "&"
            else:
                errorUrl = errorUrl + "?"
            errorUrl = errorUrl + "message=" + urllib.quote(text, safe="")
            webapp2.redirect(errorUrl, response=self.response)

    def post(self, confid):
        """Accept proposals via POST requests"""
        # get parameters from request
        name = self.request.get("name")
        surname = self.request.get("surname")
        email = self.request.get("email")
        bio = self.request.get("bio")
        useOld = self.request.get("use-old")
        title = self.request.get("title")
        abstract = self.request.get("abstract")
        duration = int(self.request.get("duration"))
        comment = self.request.get("comment")
        # timestamp 'now'
        now = datetime.now()
        # search for conference
        conference = Conference.get_by_id(confid)
        if not conference:
            self.error("Conference not found", 404)
            return
        # search for speaker?
        speakerKey = None
        if useOld:
            # get speakers for email
            speakers = Speaker.query(Speaker.email == email)
            # and order by modified-date (reverse) to get the last one
            speakers = speakers.order(-Speaker.modified).iter()
            if speakers.has_next():
                speaker = speakers.next()
                speakerKey = speaker.key
        if not speakerKey:
            # create speaker object
            speaker = Speaker(name=name, surname=surname, email=email,
                              bio=bio, created=now, modified=now)
            speakerKey = speaker.put()
        # submit proposal
        proposal = Proposal(parent=conference.key, speaker=speakerKey,
                            abstract=abstract, duration=duration,
                            title=title, comment=comment, created=now,
                            modified=now)
        proposalKey = proposal.put()
        if proposalKey:
            self.success()
        else:
            self.error("Error when storing proposal", 500)
