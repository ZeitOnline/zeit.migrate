=====================
DAV migration helpers
=====================

Installation
============

This package also contains the individual migration scripts; we don't have a
pythonic way to package those into an egg yet, so you need to clone this
repository and run::

   $ ./bootstrap.sh


Usage
=====

To restrict access to print articles to `registration` use::

   $ bin/python migrate_print_articles_ZON_3383.py < example_uniqueids.txt

To disable `is_amp` on articles whose `access` is not `free` use::

   $ bin/python migrate_restricted_amp_articles_ZON_3323.py < example_uniqueids.txt


Running tests
=============

::

    $ bin/pytest
