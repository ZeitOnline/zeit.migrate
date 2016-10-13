import collections
import migrate_properties
import pytest


Response = collections.namedtuple('Response', ['content'])


class FakeClient(object):

    properties_result = None
    body_result = None

    def __init__(self, properties, body):
        self.properties = properties
        self.body = body

    def propfind(self, url):
        return migrate_properties.WebDAVPropfindResponse(
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
    helper = migrate_properties.PropertyMigrationHelper(client)
    with helper.properties('http://xml.zeit.de/foobar'):
        pass
    assert all(['DAV' not in key for key in client.properties_result.keys()])


def test_changes_existing_property_in_dav_and_body(client):
    access_key = '{http://namespaces.zeit.de/CMS/document}access'
    helper = migrate_properties.PropertyMigrationHelper(client)
    with helper.properties('http://xml.zeit.de/foobar') as prop:
        prop[access_key] = 'abo'
    assert 'abo' == client.properties_result[access_key]
    assert 'name="access">abo</attribute>' in client.body_result


def test_creates_new_property_in_dav_and_body_if_missing(client):
    foobar_key = '{http://namespaces.zeit.de/CMS/document}foobar'
    helper = migrate_properties.PropertyMigrationHelper(client)
    with helper.properties('http://xml.zeit.de/foobar') as prop:
        prop[foobar_key] = 'lorem'
    assert 'lorem' == client.properties_result[foobar_key]
    assert 'name="foobar">lorem</attribute>' in client.body_result
