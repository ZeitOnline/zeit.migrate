from zeit.migrate import migrate as zm
import sys


def migrate(props):
    """Disable `is_amp` on all articles, whose `access` is not `free`."""
    access = '{%s}access' % zm.NAMESPACE
    if props[access] not in ('free', None):
        props['{%s}is_amp' % zm.NAMESPACE] = 'no'


if __name__ == "__main__":
    for props in zm.main(uniqueIds=sys.stdin):
        migrate(props)
