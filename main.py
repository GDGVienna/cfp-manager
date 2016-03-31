"""Main module (app) for the AppEngine application"""

import webapp2
import endpoints
from manager import CfpManagerApi
from proposal import ProposalHandler
from speaker import SpeakerHandler

app = webapp2.WSGIApplication([
    # here the web routes will be listed
    ('/proposal/(.*)', ProposalHandler),
    ('/email/(.*)', SpeakerHandler),
], debug=True)

api = endpoints.api_server([CfpManagerApi])  # register API
