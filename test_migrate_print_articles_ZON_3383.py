import lxml.etree
import migrate_print_articles_ZON_3383 as migrate
import migrate_properties

BODY_TEMPLATE = """\
<?xml version="1.0" encoding="utf-8"?>
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
<head>
    {attributes}
</head>
<body><title>Title</title></body>
</article>
"""

ACCESS_KEY = '{%s}access' % migrate_properties.NAMESPACE


def test_migration_sets_access_to_registration():
    body = BODY_TEMPLATE.format(attributes="""\
<attribute py:pytype="str" ns="{namespace}" name="access">free</attribute>
""".format(namespace=migrate_properties.NAMESPACE))
    props = migrate_properties.Properties(
        {ACCESS_KEY: 'free'},
        lxml.etree.fromstring(body))

    migrate.migrate(props)
    assert 'registration' == props.dav_properties[ACCESS_KEY]
    assert 'registration' == props.body.find(
        ".//head/attribute[@name='access']").text
