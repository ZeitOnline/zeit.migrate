import contextlib
import lxml.etree
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

    def __init__(self):
        url = urlparse.urlparse(DAV_URL)
        self.client = WebDAVClient(url.hostname, url.port)

    def _path(self, uniqueId):
        """Calculate URI for propfind / proppatch."""
        return '{}{}'.format('/cms/work', urlparse.urlparse(uniqueId).path)

    @contextlib.contextmanager
    def properties(self, uniqueId):
        """Read properties, yield them for migration and write back to DAV."""
        props = self.client.propfind(self._path(uniqueId)).properties
        yield props
        self.client.proppatch(self._path(uniqueId), props)


if __name__ == "__main__":
    migration_helper = PropertyMigrationHelper()
    for uniqueId in sys.stdin:
        with migration_helper.properties(uniqueId.strip()) as props:
            props['{http://namespaces.zeit.de/CMS/document}access'] = (
                'registration')
