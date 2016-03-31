"""Data models for the CfP Manager.

The following models are defined in this module:
Conference - a conference for which a CfP is to be managed
Speaker - a (hopeful) speaker
Proposal - a talk proposal for a conference (child of Conference)
Review - a review by a reviewer for a talk proposal (child of Talk)
"""

from google.appengine.ext import ndb
from protorpc import messages


class Conference(ndb.Model):
    """A conference entity represents a specific instance
    for which a call for papers is open.
    """
    name = ndb.StringProperty(required=True)
    subtitle = ndb.StringProperty()
    cfpDateFrom = ndb.DateProperty()
    cfpDateTo = ndb.DateProperty()
    details = ndb.TextProperty()
    reviewers = ndb.StringProperty(repeated=True)
    created = ndb.DateTimeProperty()
    modified = ndb.DateTimeProperty()


class ConferenceForm(messages.Message):
    """Inbound form for creating a conference form"""
    name = messages.StringField(1, required=True)
    subtitle = messages.StringField(2)
    id = messages.StringField(3, required=True)
    cfpDateFrom = messages.StringField(4)
    cfpDateTo = messages.StringField(5)
    details = messages.StringField(6)
    reviewers = messages.StringField(7, repeated=True)


class ConferencePublicForm(messages.Message):
    """Outbound form - publicly available info on a conference"""
    name = messages.StringField(1, required=True)
    subtitle = messages.StringField(2)
    id = messages.StringField(3, required=True)
    cfpDateFrom = messages.StringField(4)
    cfpDateTo = messages.StringField(5)
    details = messages.StringField(6)


class ConferencePublicForms(messages.Message):
    """Outbound form for getting all open CfPs for conferences"""
    items = messages.MessageField(ConferencePublicForm, 1, repeated=True)


class Speaker(ndb.Model):
    """A (hopeful) speaker at a conference."""
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    bio = ndb.TextProperty()
    created = ndb.DateTimeProperty()
    modified = ndb.DateTimeProperty()


class SpeakerForm(messages.Message):
    """Inbound form for creating a new speaker record."""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)
    bio = messages.StringField(3)


class SpeakerKeyForm(messages.Message):
    """Outbound form returned to identify a speaker record."""
    key = messages.StringField(1)
    email = messages.StringField(2)


class Proposal(ndb.Model):
    """A proposal for a call for papers."""
    title = ndb.StringProperty()
    speaker = ndb.KeyProperty(kind=Speaker)
    abstract = ndb.TextProperty()
    duration = ndb.IntegerProperty()
    comment = ndb.TextProperty()
    created = ndb.DateTimeProperty()
    modified = ndb.DateTimeProperty()


class ProposalForm(messages.Message):
    """Inbound form for a talk proposal."""
    title = messages.StringField(1, required=True)
    speaker = messages.StringField(2, required=True)
    abstract = messages.StringField(3)
    duration = messages.IntegerField(4)
    comment = messages.StringField(5)


class ProposalKeyForm(messages.Message):
    """Outbound for returned to identify a proposal."""
    key = messages.StringField(1)
    title = messages.StringField(2)


class Review(ndb.Model):
    reviewer = ndb.StringProperty()
    rating = ndb.IntegerProperty()
