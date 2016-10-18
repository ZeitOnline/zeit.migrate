import migrate_properties
import sys


def migrate(props):
    """Restrict access to all print articles to `registration`."""
    props['{%s}access' % migrate_properties.NAMESPACE] = 'registration'


if __name__ == "__main__":
    for props in migrate_properties.main(uniqueIds=sys.stdin):
        migrate(props)
