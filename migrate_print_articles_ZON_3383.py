from zeit.migrate import migrate as zm
import sys


def migrate(props):
    """Restrict access to all print articles to `registration`."""
    props['{%s}access' % zm.NS_DOCUMENT] = 'registration'


if __name__ == "__main__":
    for props in zm.main(uniqueIds=sys.stdin):
        migrate(props)
