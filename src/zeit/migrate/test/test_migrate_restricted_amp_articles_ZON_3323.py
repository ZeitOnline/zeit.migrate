import lxml.etree
import migrate_restricted_amp_articles_ZON_3323 as migrate
import zeit.migrate.migrate

BODY_TEMPLATE = """\
<?xml version="1.0" encoding="utf-8"?>
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
<head>
    {attributes}
</head>
<body><title>Title</title></body>
</article>
"""

ACCESS_KEY = '{%s}access' % zeit.migrate.migrate.NS_DOCUMENT
IS_AMP_KEY = '{%s}is_amp' % zeit.migrate.migrate.NS_DOCUMENT


def test_migration_restricts_amp_for_restricted_articles():
    body = BODY_TEMPLATE.format(attributes="""\
<attribute py:pytype="str" ns="{namespace}" name="access">abo</attribute>
<attribute py:pytype="str" ns="{namespace}" name="is_amp">yes</attribute>
""".format(namespace=zeit.migrate.migrate.NS_DOCUMENT))
    props = zeit.migrate.migrate.Properties(
        {ACCESS_KEY: 'abo', IS_AMP_KEY: 'yes'},
        lxml.etree.fromstring(body))

    migrate.migrate(props)
    assert 'no' == props.dav_properties[IS_AMP_KEY]
    assert 'no' == props.body.find(".//head/attribute[@name='is_amp']").text


def test_migration_does_not_change_is_amp_if_access_is_free():
    body = BODY_TEMPLATE.format(attributes="""\
<attribute py:pytype="str" ns="{namespace}" name="access">free</attribute>
<attribute py:pytype="str" ns="{namespace}" name="is_amp">yes</attribute>
""".format(namespace=zeit.migrate.migrate.NS_DOCUMENT))
    props = zeit.migrate.migrate.Properties(
        {ACCESS_KEY: 'free', IS_AMP_KEY: 'yes'},
        lxml.etree.fromstring(body))

    migrate.migrate(props)
    assert 'yes' == props.dav_properties[IS_AMP_KEY]
    assert 'yes' == props.body.find(".//head/attribute[@name='is_amp']").text


def test_migration_treats_missing_access_as_free():
    body = BODY_TEMPLATE.format(attributes="""\
<attribute py:pytype="str" ns="{namespace}" name="is_amp">yes</attribute>
""".format(namespace=zeit.migrate.migrate.NS_DOCUMENT))
    props = zeit.migrate.migrate.Properties(
        {IS_AMP_KEY: 'yes'},
        lxml.etree.fromstring(body))

    migrate.migrate(props)
    assert 'yes' == props.dav_properties[IS_AMP_KEY]
    assert 'yes' == props.body.find(".//head/attribute[@name='is_amp']").text
