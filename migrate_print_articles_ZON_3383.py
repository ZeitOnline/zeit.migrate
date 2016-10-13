import migrate_properties
import sys


if __name__ == "__main__":
    """Restrict access to all print articles to `registration`."""
    namespace = 'http://namespaces.zeit.de/CMS/document'
    migration_helper = migrate_properties.PropertyMigrationHelper()
    for uniqueId in sys.stdin:
        with migration_helper.properties(uniqueId.strip()) as props:
            props['{%s}access' % namespace] = 'registration'
