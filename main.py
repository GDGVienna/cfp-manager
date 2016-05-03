"""Main module (app) for the AppEngine application"""

import webapp2
import endpoints
from manager import CfpManagerApi
from proposal import ProposalHandler
from speaker import SpeakerHandler
from backup import BackupHandler

app = webapp2.WSGIApplication([
    # here the web routes will be listed
    ('/proposal/(.*)', ProposalHandler),
    ('/email/(.*)', SpeakerHandler),
    ('/backup/(.*)', BackupHandler),
], debug=True)

api = endpoints.api_server([CfpManagerApi])  # register API
