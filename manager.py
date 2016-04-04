"""CfP Manager functionality"""

import endpoints
from datetime import datetime
from google.appengine.ext import ndb
from google.appengine.api import users
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from models import Conference
from models import ConferenceForm
from models import ConferencePublicForm
from models import ConferencePublicForms
from models import Speaker
from models import SpeakerForm
from models import SpeakerKeyForm
from models import Proposal
from models import ProposalForm
from models import ProposalKeyForm
from settings import *


PROPOSAL_SUBMIT_REQUEST = endpoints.ResourceContainer(
    ProposalForm,
    conferenceId=messages.StringField(1),
)

SPEAKER_BY_EMAIL_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    email=messages.StringField(1),
)


@endpoints.api(
    name='manager', version='v1', audiences=[ANDROID_AUDIENCE],
    allowed_client_ids=[
        WEB_CLIENT_ID, ANDROID_CLIENT_ID,
        endpoints.API_EXPLORER_CLIENT_ID,
        IOS_CLIENT_ID],
    scopes=[endpoints.EMAIL_SCOPE]
    )
class CfpManagerApi(remote.Service):
    """Call for Papers Manager"""

    def _copyToForm(self, src, trg):
        """Copy from an entity to a form"""
        for field in trg.all_fields():
            if hasattr(src, field.name):
                value = getattr(src, field.name)
                # does it contain 'Date'?
                if "Date" in field.name:
                    setattr(trg, field.name, str(value))
                # does it ask for a key?
                elif field.name == "key":
                    setattr(trg, field.name, value.urlsafe())
                else:
                    setattr(trg, field.name, value)
            else:
                if field.name == "id":
                    setattr(trg, "id", src.key.id())
        # check if all is OK
        trg.check_initialized()
        return trg

    @endpoints.method(
        message_types.VoidMessage, ConferencePublicForms,
        path='conference', http_method='GET',
        name='listConferences')
    def listConferences(self, request):
        """List all conferences with open CfP"""
        nowDate = datetime.now().date()
        confs = Conference.query(Conference.cfpDateTo >= nowDate)
        # further filter down the conferences
        confs = [c for c in confs if c.cfpDateFrom <= nowDate]
        return ConferencePublicForms(
            items=[self._copyToForm(conf, ConferencePublicForm())
                   for conf in confs]
        )

    @endpoints.method(
        ConferenceForm, ConferenceForm, path='conference',
        http_method='POST', name='createConference')
    def createConference(self, request):
        """Create a new Conference object"""
        if users.is_current_user_admin():
            # we only allow an admin user to create a conference
            if not request.name or not request.id:
                raise endpoints.BadRequestException(
                    "Required field (name and/or id) missing"
                )
            data = {field.name: getattr(request, field.name)
                    for field in request.all_fields()}
            # convert start/end dates
            if data['cfpDateFrom']:
                data['cfpDateFrom'] = datetime.strptime(
                    data['cfpDateFrom'][:10], "%Y-%m-%d").date()
            if data['cfpDateTo']:
                data['cfpDateTo'] = datetime.strptime(
                    data['cfpDateTo'][:10], "%Y-%m-%d").date()
            # set the created date/time stamp
            data['created'] = datetime.now()
            data['modified'] = data['created']
            # store in DataStore
            Conference(**data).put()
            return request
        else:
            raise endpoints.ForbiddenException(
                "Only administrators can create a conference"
            )

    @endpoints.method(
        SpeakerForm, SpeakerKeyForm, path='speaker',
        http_method='POST', name='createSpeaker')
    def createSpeaker(self, request):
        """Create a new speaker object"""
        if not request.email or not request.name or not request.surname:
            raise endpoints.BadRequestException(
                "Required field (name, surname and/or email) missing"
            )
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}
        # set the created date/time stamp
        data['created'] = datetime.now()
        data['modified'] = data['created']
        # store in Datastore
        speakerKey = Speaker(**data).put()
        speakerKeyForm = SpeakerKeyForm()
        speakerKeyForm.key = speakerKey.urlsafe()
        speakerKeyForm.email = request.email
        return speakerKeyForm

    @endpoints.method(
        SPEAKER_BY_EMAIL_REQUEST, SpeakerKeyForm,
        path='speaker/by_email/{email}',
        http_method='GET', name='speakerByEmail')
    def speakerByEmail(self, request):
        """Return speaker key for email"""
        if not request.email:
            raise endpoints.BadRequestException(
                "Missing email parameter"
            )
        # get speakers for email
        speakers = Speaker.query(Speaker.email == request.email)
        # and order by modified-date (reverse) to get the last one
        speakers = speakers.order(-Speaker.modified).iter()
        if speakers.has_next():
            lastSpeaker = speakers.next()
            retVal = SpeakerKeyForm()
            retVal.email = lastSpeaker.email
            retVal.key = lastSpeaker.key.urlsafe()
            return retVal
        raise endpoints.NotFoundException(
            "No speaker for this email found"
        )

    @endpoints.method(
        PROPOSAL_SUBMIT_REQUEST, ProposalKeyForm,
        path='conference/{conferenceId}/proposal',
        http_method='POST', name='submitProposal')
    def submitProposal(self, request):
        """Submit a new talk proposal"""
        if not request.title or not request.speaker:
            raise endpoints.BadRequestException(
                "Required field (title and/or speaker key) missing"
            )
        # get the speaker (check if it exists)
        speaker = ndb.Key(urlsafe=request.speaker).get()
        if not speaker:
            raise endpoints.BadRequestException(
                "Speaker entity not found"
            )
        if speaker.key.kind() != "Speaker":
            raise endpoints.BadRequestException(
                "Invalid key kind for speaker specified"
            )
        # get the conference (check if it exists)
        conf = Conference.get_by_id(request.conferenceId)
        if not conf:
            raise endpoints.BadRequestException(
                "Invalid conference identifier specified"
            )
        # TODO: check if call for papers is still open
        # fill the data structure for creating the entity
        data = {field.name: getattr(request, field.name)
                for field in request.all_fields()}
        # delete conference id, link to parent
        del data['conferenceId']
        data['parent'] = conf.key
        # update the speaker reference
        data['speaker'] = speaker.key
        # set the created date/time stamp
        data['created'] = datetime.now()
        data['modified'] = data['created']
        # store in Datastore - with correct parent
        proposalKey = Proposal(**data).put()
        # return value
        retVal = ProposalKeyForm()
        retVal.key = proposalKey.urlsafe()
        retVal.title = request.title
        return retVal
