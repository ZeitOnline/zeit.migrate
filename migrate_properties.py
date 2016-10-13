import UserDict
import contextlib
import lxml.etree
import lxml.objectify
import re
import sys
import tinydav
import urlparse

DAV_URL = 'http://cms-backend.staging.zeit.de:9000'


class WebDAVClient(tinydav.WebDAVClient):
    """Basically a `tinydav.WebDAVClient` with better support for properties.

    The Response object supports conversion of the XML response to a dict of
    DAV properties. For simplicity this specialized client does not support
    other parameters aside URI.

    """

    def propfind(self, uri):
        resp = super(WebDAVClient, self).propfind(uri)
        if resp == 301:
            resp = super(WebDAVClient, self).propfind(uri + '/')
        return WebDAVPropfindResponse(resp)


class WebDAVPropfindResponse(object):
    """A WebDAVPropfindResponse, which can be used for proppatches."""

    def __init__(self, response):
        self.xml = lxml.etree.fromstring(response.content)

    @property
    def properties(self):
        """Returns all CMS properties of the DAV Resource."""
        return self._parse_dav_properties(self.xml)

    def _parse_dav_properties(self, dav_xml):
        """Converts XML properties to dict and extracts CMS properties.

        Therefore properties from the `DAV:` namespace and
        `http://apache.org/dav/props/` namespace will be filtered.

        Adjusted copy of https://github.com/ZeitOnline/zeit.syncer.

        :Example:

           {'{http://namespaces.zeit.de/CMS/document}my_prop': 'my_val

        """
        # Select properties contained in XML response inside `{DAV:}prop` tag.
        all_props = next(dav_xml.iterfind('.//{DAV:}prop')).iterfind('*')
        # Filter properties that do not belong to the CMS namespace.
        cms_props = filter(
            lambda x: x.tag.startswith('{http://namespaces.zeit.de/CMS'),
            all_props)

        properties = {}
        for prop in cms_props:
            properties[prop.tag] = prop.text.strip() if prop.text else ''
        return properties


class PropertyMigrationHelper(object):
    """Migrate DAV properties of CMS content retrieved via uniqueId.

    To migrate DAV properties of a certain CMS content, call `properties` as a
    context manager, for example::

    helper = PropertyMigrationHelper()
    with helper.properties('http://xml.zeit.de/path/to/content') as props:
        props['{http://namespaces.zeit.de/CMS/document}access'] = 'free'

    """

    def __init__(self, client=None):
        if client is None:
            url = urlparse.urlparse(DAV_URL)
            self.client = WebDAVClient(url.hostname, url.port)
        else:
            self.client = client

    def _path(self, uniqueId):
        """Calculate URI for propfind / proppatch."""
        return '{}{}'.format('/cms/work', urlparse.urlparse(uniqueId).path)

    @contextlib.contextmanager
    def properties(self, uniqueId):
        """Read properties, yield them for migration and write back to DAV."""
        props = self.client.propfind(self._path(uniqueId)).properties
        xml = lxml.etree.fromstring(
            self.client.get(self._path(uniqueId)).content)
        yield Properties(props, xml)
        self.client.put(
            self._path(uniqueId),
            lxml.etree.tostring(xml, encoding='utf-8', xml_declaration=True))
        self.client.proppatch(self._path(uniqueId), props)


class Properties(UserDict.DictMixin):
    """Helper class to transparently manipulate DAV properties *and* body."""

    def __init__(self, dav_properties, body):
        self.dav_properties = dav_properties
        self.body = body

    def __getitem__(self, namespaced_key):
        """DAV properties are the "master" source, so we only look there."""
        return self.dav_properties[namespaced_key]

    def __setitem__(self, namespaced_key, value):
        """Set new value in DAV properties and inside the XML body.

        For DAV Properties `proppatch` takes care of creating new properties,
        but inside the XML body we have to create new nodes manually.

        """
        self.dav_properties[namespaced_key] = value

        namespace, key = re.match("\{(.+)\}(.+)", namespaced_key).groups()
        prop = self.body.find(
            ".//head/attribute[@ns='{}'][@name='{}']".format(namespace, key))
        if prop is not None:
            prop.text = value
        else:
            element = self._create_attribute(namespace, key, value)
            self.body.find('.//head').append(element)

    def _create_attribute(self, namespace, key, value):
        """Create new <attribute> to save property inside XML body.

        We try to keep the same order as the CMS, i.e. first `py:pytype`
        annotation followed by `ns` and `name`.

        """
        element = lxml.etree.Element("attribute")
        element.text = value
        lxml.objectify.annotate(element)
        element.set('ns', namespace)
        element.set('name', key)
        return element


if __name__ == "__main__":
    migration_helper = PropertyMigrationHelper()
    for uniqueId in sys.stdin:
        with migration_helper.properties(uniqueId.strip()) as props:
            props['{http://namespaces.zeit.de/CMS/document}access'] = (
                'registration')
