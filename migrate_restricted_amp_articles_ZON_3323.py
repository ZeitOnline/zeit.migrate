import migrate_properties
import sys


if __name__ == "__main__":
    """Disable `is_amp` on all articles, whose `access` is not `free`."""
    namespace = 'http://namespaces.zeit.de/CMS/document'
    migration_helper = migrate_properties.PropertyMigrationHelper()
    for uniqueId in sys.stdin:
        with migration_helper.properties(uniqueId.strip()) as props:
            if props['{%s}access' % namespace] != 'free':
                props['{%s}is_amp' % namespace] = 'no'
