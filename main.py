"""Main module (app) for the AppEngine application"""

import webapp2

app = webapp2.WSGIApplication([
    # here the web routes will be listed
], debug=True)