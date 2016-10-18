Installation
============

We need a customized fork of tinydav, which fixes an issue in proppatch.

>>> git clone git@github.com:ZeitOnline/tinydav.git ../tinydav
>>> virtualenv .
>>> ./bin/pip install -e ../tinydav
>>> ./bin/pip install lxml

We cannot install our custom tinydav like below, since somehow the
``__init__.py`` is missing, which contains almost everything of tinydav.

>>> ./bin/pip install tinydav -i http://devpi.zeit.de:4040/zeit/default --trusted-host devpi.zeit.de


Usage
=====

To restrict access to print articles to `registration` use::

>>> ./bin/python migrate_print_articles_ZON_3383.py < example_uniqueids.txt

To disable `is_amp` on articles whose `access` is not `free` use::

>>> ./bin/python migrate_restricted_amp_articles_ZON_3323.py < example_uniqueids.txt


Testing
=======

>>> ./bin/pip install pytest pytest-cov
>>> ./bin/pip install mock
>>> ./bin/pytest test_migrate_properties.py
