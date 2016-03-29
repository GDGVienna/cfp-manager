"""Main module (app) for the AppEngine application"""

import webapp2
import endpoints
from manager import CfpManagerApi

app = webapp2.WSGIApplication([
    # here the web routes will be listed
], debug=True)

api = endpoints.api_server([CfpManagerApi])  # register API
