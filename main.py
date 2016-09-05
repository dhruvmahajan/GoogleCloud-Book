# Copyright 2016 Google Inc. All rights reserved.
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

import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote

from google.appengine.ext import ndb

from google.appengine.api import memcache

class Book(messages.Message):
	name = messages.StringField(1);
	author = messages.StringField(2);


class BookModel(ndb.Model):
    name = ndb.StringProperty(required=True)
    author = ndb.StringProperty(required=True)

class BookCollection(messages.Message):
    items = messages.MessageField(Book, 1, repeated=True)


@endpoints.api(name='books', version='v1')
class BooksApi(remote.Service):

    @endpoints.method(
        message_types.VoidMessage,
        BookCollection,
        path='books',
        http_method='GET',
        name='books.list')
    def list_books(self, unused_request):
    	cache_data = memcache.get('booksKey:BookCollection')
    	if cache_data is None:
    		result = []
    		for ans in BookModel.query():
    			result.append(Book(name=ans.name, author=ans.author))
    		finalResult = BookCollection(items=result)
    		memcache.add('booksKey:BookCollection', finalResult)
    		return finalResult
    	else:
    		return cache_data			

    @endpoints.method(
    	Book, Book,
    	name='books.add',
    	http_method='POST',	
    	path='add',
    	)

    def add_book(self, request):
    	BookModel(name=request.name, author=request.author).put()
    	memcache.delete('booksKey:BookCollection')
    	return request


api = endpoints.api_server([BooksApi])
