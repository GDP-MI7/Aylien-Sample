# Copyright 2015 Aylien, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import uuid
import glob
import json
import unittest
import httpretty

from nose.tools import eq_
from nose.tools import ok_
from nose.tools import raises

from aylienapiclient import http
from aylienapiclient import textapi
from aylienapiclient.errors import HttpError
from aylienapiclient.errors import MissingParameterError
from aylienapiclient.errors import MissingCredentialsError

try:
  from StringIO import StringIO
except ImportError:
  from io import StringIO

@raises(MissingCredentialsError)
def test_raises_missing_credentials_error():
  client = textapi.Client("", "")

def test_generator():
  pattern = re.compile(r'^tests/fixtures/(\w+).json$')
  files = glob.glob('tests/fixtures/*.json')
  for f in files:
    method = pattern.sub(r'\1', f)
    request = http.Request(method.replace('_', '/'))
    fixtures = open(f)
    test_data = json.load(fixtures)
    for test in test_data['tests']:
      io = StringIO()
      json.dump(test['output'], io)
      yield 'check_' + method, request.uri, test['input'], test['input_type'], io.getvalue()

def test_generic_generator():
  pattern = re.compile(r'^tests/fixtures/(\w+).json$')
  files = glob.glob('tests/fixtures/*.json')
  for f in files:
    endpoint = pattern.sub(r'\1', f)
    if endpoint not in ["microformats"]:
      yield check_auth, endpoint
    yield check_options, endpoint
    if endpoint not in ["related"]:
      yield check_bad_request, endpoint

@httpretty.activate
@raises(HttpError)
def check_auth(endpoint):
  client = textapi.Client("app_id", "app_key")
  request = http.Request(endpoint)
  httpretty.register_uri(httpretty.POST, request.uri, status=403,
      body="Authentication parameters missing")
  method = getattr(client, endpoint.title().replace('_', ''))
  method('random')

@raises(MissingParameterError)
def check_options(endpoint):
  client = textapi.Client("app_id", "app_key")
  method = getattr(client, endpoint.title().replace('_', ''))
  method({})

@httpretty.activate
@raises(HttpError)
def check_bad_request(endpoint):
  client = textapi.Client("app_id", "app_key")
  request = http.Request(endpoint)
  httpretty.register_uri(httpretty.POST, request.uri, status=400,
      body='{"error" : "requirement failed: provided url is not valid."}')
  method = getattr(client, endpoint.title().replace('_', ''))
  method({'url': 'invalid-url'})

@httpretty.activate
def check_extract(uri, test_input, input_type, expected_output):
  client = textapi.Client("app_id", "app_key")
  httpretty.register_uri(httpretty.POST, uri, body=expected_output)
  article = client.Extract(test_input)
  ok_('url' in httpretty.last_request().parsed_body)
  ok_('author' in article)
  ok_('title' in article)

@httpretty.activate
def check_sentiment(uri, test_input, input_type, expected_output):
  client = textapi.Client("app_id", "app_key")
  httpretty.register_uri(httpretty.POST, uri, body=expected_output)
  sentiment = client.Sentiment(test_input)
  ok_(input_type in httpretty.last_request().parsed_body)
  for prop in ['polarity', 'subjectivity', 'subjectivity_confidence', 'polarity_confidence']:
    ok_(prop in sentiment)

@httpretty.activate
def check_classify(uri, test_input, input_type, expected_output):
  client = textapi.Client("app_id", "app_key")
  httpretty.register_uri(httpretty.POST, uri, body=expected_output)
  classification = client.Classify(test_input)
  ok_(input_type in httpretty.last_request().parsed_body)
  ok_('categories' in classification)
  ok_(hasattr(classification['categories'], "__getitem__"))

@httpretty.activate
def check_concepts(uri, test_input, input_type, expected_output):
  client = textapi.Client("app_id", "app_key")
  httpretty.register_uri(httpretty.POST, uri, body=expected_output)
  concepts = client.Concepts(test_input)
  ok_(input_type in httpretty.last_request().parsed_body)

@httpretty.activate
def check_entities(uri, test_input, input_type, expected_output):
  client = textapi.Client("app_id", "app_key")
  httpretty.register_uri(httpretty.POST, uri, body=expected_output)
  entities = client.Entities(test_input)
  ok_(input_type in httpretty.last_request().parsed_body)
  ok_('entities' in entities)
  ok_('person' in entities['entities'])

@httpretty.activate
def check_hashtags(uri, test_input, input_type, expected_output):
  client = textapi.Client("app_id", "app_key")
  httpretty.register_uri(httpretty.POST, uri, body=expected_output)
  hashtags = client.Hashtags(test_input)
  ok_(input_type in httpretty.last_request().parsed_body)

@httpretty.activate
def check_language(uri, test_input, input_type, expected_output):
  client = textapi.Client("app_id", "app_key")
  httpretty.register_uri(httpretty.POST, uri, body=expected_output)
  language = client.Language(test_input)
  ok_(input_type in httpretty.last_request().parsed_body)
  ok_('lang' in language)

@httpretty.activate
def check_summarize(uri, test_input, input_type, expected_output):
  client = textapi.Client("app_id", "app_key")
  httpretty.register_uri(httpretty.POST, uri, body=expected_output)
  summary = client.Summarize(test_input)
  ok_(input_type in httpretty.last_request().parsed_body)
  ok_('sentences' in summary)

@httpretty.activate
def check_related(uri, test_input, input_type, expected_output):
  client = textapi.Client("app_id", "app_key")
  httpretty.register_uri(httpretty.POST, uri, body=expected_output)
  related = client.Related(test_input)
  ok_(input_type in httpretty.last_request().parsed_body)
  ok_('related' in related)

@httpretty.activate
def check_microformats(uri, test_input, input_type, expected_output):
  client = textapi.Client("app_id", "app_key")
  httpretty.register_uri(httpretty.POST, uri, body=expected_output)
  microformats = client.Microformats(test_input)
  ok_(input_type in httpretty.last_request().parsed_body)
  ok_('hCards' in microformats)

@httpretty.activate
def check_unsupervised_classify(uri, test_input, input_type, expected_output):
  client = textapi.Client("app_id", "app_key")
  uri = uri.replace('unsupervised/classify', 'classify/unsupervised')
  httpretty.register_uri(httpretty.POST, uri, body=expected_output)
  classes = client.UnsupervisedClassify(test_input)
  ok_(input_type in httpretty.last_request().parsed_body)
  ok_('classes' in classes)

@httpretty.activate
def test_check_for_auth_headers_in_request():
  app_id = str(uuid.uuid4())
  app_key = str(uuid.uuid4())
  client = textapi.Client(app_id, app_key)
  request = http.Request('sentiment')
  httpretty.register_uri(httpretty.POST, request.uri, body="[]")
  client.Sentiment('random')
  for k in ['id', 'key']:
    ok_('x-aylien-textapi-application-' + k in httpretty.last_request().headers)
  eq_(httpretty.last_request().headers['x-aylien-textapi-application-id'], app_id)
  eq_(httpretty.last_request().headers['x-aylien-textapi-application-key'], app_key)

@httpretty.activate
def test_check_ratelimits():
  client = textapi.Client('app_id', 'app_key')
  request = http.Request('sentiment')
  limit = 1000
  reset = 1420761600
  remaining = 954
  httpretty.register_uri(httpretty.POST, request.uri,
      body="[]",
      adding_headers={
        'X-RateLimit-Limit': limit, 'X-RateLimit-Remaining': remaining,
        'X-RateLimit-Reset': reset, 'Date': 'Thu, 08 Jan 2015 12:02:19 GMT'
      })
  client.Sentiment('random')
  ratelimits = client.RateLimits()
  eq_(ratelimits['remaining'], remaining)
  eq_(ratelimits['limit'], limit)
  eq_(ratelimits['reset'], reset)
