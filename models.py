"""Data models for the CfP Manager.

The following models are defined in this module:
Conference - a conference for which a CfP is to be managed
Speaker - a (hopeful) speaker
Talk - a talk submission for a conference (child of conference)
Review - a review by a reviewer for a talk proposal (child of Talk)
"""

from google.appengine.ext import ndb
from protorpc import messages

class Conference(ndb.Model):
    name = ndb.StringProperty(required=True)
    subtitle = ndb.StringProperty()
    cfpDateFrom = ndb.DateProperty()
    cfpDateTo = ndb.DateProperty()
    details = ndb.TextProperty()
    reviewers = ndb.StringProperty(repeated=True)

class ConferenceForm(messages.Message):
    name = messages.StringField(1, required=True)
    subtitle = messages.StringField(2)
    id = messages.StringField(3, required=True)
    cfpDateFrom = messages.StringField(4)
    cfpDateTo = messages.StringField(5)
    details = messages.BytesField(6)
    reviewers = messages.StringField(7, repeated=True)
    
class Speaker(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    bio = ndb.TextProperty()

class Talk(ndb.Model):
    title = ndb.StringProperty()
    speaker = ndb.KeyProperty(kind=Speaker)
    abstract = ndb.TextProperty()
    duration = ndb.IntegerProperty()
    comment = ndb.TextProperty()

class Review(ndb.Model):
    reviewer = ndb.StringProperty()
    rating = ndb.IntegerProperty()

