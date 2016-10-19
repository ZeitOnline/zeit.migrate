import collections
import zeit.migrate.migrate
import mock
import pytest


Response = collections.namedtuple('Response', ['content'])


class FakeClient(object):

    properties_result = None
    body_result = None

    def __init__(self, properties, body):
        self.properties = properties
        self.body = body

    def propfind(self, url):
        return zeit.migrate.migrate.WebDAVPropfindResponse(
            Response(self.properties))

    def proppatch(self, url, properties):
        self.properties_result = properties

    def get(self, url):
        return Response(self.body)

    def put(self, url, xml):
        self.body_result = xml


@pytest.fixture
def client():
    properties = """\
<?xml version="1.0" encoding="utf-8"?>
<D:multistatus xmlns:D="DAV:">
<D:response xmlns:g0="http://namespaces.zeit.de/CMS/document" xmlns:lp1="DAV:">
<D:propstat><D:prop>
    <g0:year>2008</g0:year>
    <g0:volume>26</g0:volume>
    <g0:access>free</g0:access>
    <g0:is_amp>yes</g0:is_amp>
    <lp1:creationdate>2016-10-12T14:24:02Z</lp1:creationdate>
    <lp1:getcontentlength>13843</lp1:getcontentlength>
</D:prop></D:propstat></D:response></D:multistatus>"""

    body = """\
<?xml version="1.0" encoding="utf-8"?>
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
<head>
    <attribute py:pytype="str" ns="{namespace}" name="year">2008</attribute>
    <attribute py:pytype="str" ns="{namespace}" name="volume">26</attribute>
    <attribute py:pytype="str" ns="{namespace}" name="access">free</attribute>
    <attribute py:pytype="str" ns="{namespace}" name="is_amp">yes</attribute>
</head>
<body><title>Title</title></body>
</article>
""".format(namespace="http://namespaces.zeit.de/CMS/document")

    return FakeClient(properties, body)


def test_filters_non_cms_properties(client):
    helper = zeit.migrate.migrate.PropertyMigrationHelper(client)
    with helper.properties('http://xml.zeit.de/foobar'):
        pass
    assert all(['DAV' not in key for key in client.properties_result.keys()])


def test_changes_existing_property_in_dav_and_body(client):
    access_key = '{http://namespaces.zeit.de/CMS/document}access'
    helper = zeit.migrate.migrate.PropertyMigrationHelper(client)
    with helper.properties('http://xml.zeit.de/foobar') as prop:
        prop[access_key] = 'abo'
    assert 'abo' == client.properties_result[access_key]
    assert 'name="access">abo</attribute>' in client.body_result


def test_creates_new_property_in_dav_and_body_if_missing(client):
    foobar_key = '{http://namespaces.zeit.de/CMS/document}foobar'
    helper = zeit.migrate.migrate.PropertyMigrationHelper(client)
    with helper.properties('http://xml.zeit.de/foobar') as prop:
        prop[foobar_key] = 'lorem'
    assert 'lorem' == client.properties_result[foobar_key]
    assert 'name="foobar">lorem</attribute>' in client.body_result


@pytest.mark.parametrize(
    ['prop', 'result'], [('access', 'free'), ('foobar', None)])
def test_can_read_existing_property(client, prop, result):
    key = '{http://namespaces.zeit.de/CMS/document}%s' % prop
    helper = zeit.migrate.migrate.PropertyMigrationHelper(client)
    with helper.properties('http://xml.zeit.de/foobar') as prop:
        assert result == prop[key]


def test_WebDAVClient_propfind_returns_WebDAVPropfindResponse():
    with mock.patch('tinydav.WebDAVClient.propfind') as propfind:
        propfind.return_value = Response('<foo/>')
        client = zeit.migrate.migrate.WebDAVClient('example.com')
        result = client.propfind('test.uri')
    assert isinstance(result, zeit.migrate.migrate.WebDAVPropfindResponse)


def test_WebDAVClient_propfind_retries_on_301_with_ending_slash():
    with mock.patch('tinydav.WebDAVClient.propfind') as propfind:
        propfind.side_effect = [301, Response('<foo/>')]
        client = zeit.migrate.migrate.WebDAVClient('example.com')
        client.propfind('test.uri')
    assert 'test.uri/' == propfind.call_args[0][0]


def test_PropertyMigrationHelper_automatically_creates_a_WebDAVClient():
    helper = zeit.migrate.migrate.PropertyMigrationHelper()
    assert isinstance(helper.client, zeit.migrate.migrate.WebDAVClient)


def test_main_calls_properties_for_each_uniqueId():
    with mock.patch(
            'zeit.migrate.migrate.PropertyMigrationHelper.properties') as props:
        list(zeit.migrate.migrate.main(
            ['http://xml.zeit.de/foobar', 'http://xml.zeit.de/foobaz']))
        assert 2 == props.call_count
