import migrate_properties
import sys


def migrate(props):
    """Disable `is_amp` on all articles, whose `access` is not `free`."""
    access = '{%s}access' % migrate_properties.NAMESPACE
    if props[access] not in ('free', None):
        props['{%s}is_amp' % migrate_properties.NAMESPACE] = 'no'


if __name__ == "__main__":
    for props in migrate_properties.main(uniqueIds=sys.stdin):
        migrate(props)
