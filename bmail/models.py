from google.appengine.ext import ndb

class Sporocilo(ndb.Model):
    posiljatelj = ndb.StringProperty()
    prejemnik = ndb.StringProperty()
    sporocilo = ndb.TextProperty()
    nastanek = ndb.DateTimeProperty(auto_now_add=True)