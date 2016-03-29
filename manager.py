"""CfP Manager functionality"""

import endpoints
from datetime import datetime
from google.appengine.ext import ndb
from google.appengine.api import users
from protorpc import messages
from protorpc import remote

from models import Conference
from models import ConferenceForm
from settings import *

@endpoints.api(
    name='manager', version='v1', audiences=[ANDROID_AUDIENCE],
    allowed_client_ids=[WEB_CLIENT_ID, ANDROID_CLIENT_ID,
                        endpoints.API_EXPLORER_CLIENT_ID,
                        IOS_CLIENT_ID],
    scopes=[endpoints.EMAIL_SCOPE]
)
class CfpManagerApi(remote.Service):
    """Call for Papers Manager"""
    
    @endpoints.method(
        ConferenceForm, ConferenceForm, path='conference',
        http_method='POST', name='createConference')
    def createConference(self, request):
        """Create a new Conference object"""
        if users.is_current_user_admin():
            # we only allow an admin user to create a conference
            if not request.name or not request.ident:
                raise endpoints.BadRequestException(
                    "Required field (name and/or ident) missing"
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
            # store in DataStore
            Conference(**data).put()
            return request

