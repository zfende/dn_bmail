#!/usr/bin/env python
import os
import jinja2
import webapp2
import cgi
import json

from google.appengine.api import urlfetch
from google.appengine.api import users
from models import Sporocilo

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, spremenljivke=None):
        if not spremenljivke:
            spremenljivke = {}

        user = users.get_current_user()
        spremenljivke["user"] = user
        if user:
            logiran = True
            logout_url = users.create_logout_url('/')

            url = "http://api.openweathermap.org/data/2.5/weather?q=Kranj,si&units=metric&appid=2497e798920f2b87383d818b7be99c56"
            data = urlfetch.fetch(url).content
            json_podatki = json.loads(data)


            sporocila = Sporocilo.query(Sporocilo.prejemnik == user.email()).order(-Sporocilo.nastanek).fetch()
            sporocila_poslana = Sporocilo.query(Sporocilo.posiljatelj == user.email()).order(-Sporocilo.nastanek).fetch()

            spremenljivke = {
                "sporocila": sporocila,
                "sporocila_poslana": sporocila_poslana,
                "user": user,
                "logout_url": logout_url,
                "logiran": logiran,
                "json_podatki": json_podatki,
            }

        else:
            logiran = False
            login_url = users.create_login_url('/')

            spremenljivke = {
                "user": user,
                "login_url": login_url,
                "logiran": logiran,
            }

        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(spremenljivke))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("main.html")

class PosljiSporociloHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            return self.write("Niste prijavljeni, prijavite se!")

        return self.render_template("poslji_sporocilo.html")

    def post(self):
        posiljatelj = cgi.escape(self.request.get("posiljatelj"))
        prejemnik = cgi.escape(self.request.get("prejemnik"))
        sporocilo = cgi.escape(self.request.get("sporocilo"))
        spr = Sporocilo(posiljatelj=posiljatelj, prejemnik=prejemnik, sporocilo=sporocilo)
        spr.put()
        return self.redirect("/poslji")


class PrejetaSporocilaHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            return self.write("Niste prijavljeni, prijavite se!")

        return self.render_template("prejeta_sporocila.html")

class PoslanaSporocilaHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            return self.write("Niste prijavljeni, prijavite se!")

        return self.render_template("poslana_sporocila.html")

class VremeHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            return self.write("Niste prijavljeni, prijavite se!")

        return self.render_template("vreme.html")

class IzbrisiPrejetoSporociloHandler(BaseHandler):
    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        sporocilo.key.delete()
        return self.redirect("/prejeta")

class IzbrisiPoslanoSporociloHandler(BaseHandler):
    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        sporocilo.key.delete()
        return self.redirect("/poslana")


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/poslji', PosljiSporociloHandler),
    webapp2.Route('/prejeta', PrejetaSporocilaHandler),
    webapp2.Route('/poslana', PoslanaSporocilaHandler),
    webapp2.Route('/prejeta/<sporocilo_id:\d+>/izbrisi', IzbrisiPrejetoSporociloHandler),
    webapp2.Route('/poslana/<sporocilo_id:\d+>/izbrisi', IzbrisiPoslanoSporociloHandler),
    webapp2.Route('/vreme', VremeHandler),
], debug=True)
