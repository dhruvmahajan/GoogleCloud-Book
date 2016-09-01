#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import cgi
import datetime
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import memcache

book_key = ndb.Key('book', 'default_book')

class Book(ndb.Model):
  name = ndb.StringProperty()
  author = ndb.StringProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>')

    self.response.out.write("""
          <form action="/add" method="post">
            <div>Book Name<br><input type="text" name="book_name" ></input></div>
            <div>Author Name<br><input type="text" name="book_author"></input></div>
            <input type="submit" value="Add Book"></form>
          </form>
          <a href="/show">Show</a><br>
        </body>
      </html>""")


class addBook(webapp2.RequestHandler):
  def post(self):
    book = Book(parent=book_key)

    book.name = self.request.get('book_name')
    book.author = self.request.get('book_author')
    book.put()
    self.response.out.write('Added<br>')
    self.response.out.write('<a href="/">Add More</a><br>')


class showBooks(webapp2.RequestHandler):
	def get(self):
		result=[]
		cache_data = memcache.get('key')
		if cache_data is not None:
			books = cache_data
			self.response.out.write('from cache<br>')
		else:
			books = ndb.gql('SELECT * FROM Book WHERE ANCESTOR IS :1 ORDER BY date DESC LIMIT 10', book_key)
			memcache.add('key', books, 60)

		for book in books:
			result.append([book.name.encode('ascii'), book.author.encode('ascii')])
			memcache.add('key', data, 60)

		self.response.out.write(result)


app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/add', addBook),
  ('/show', showBooks)
], debug=True)
