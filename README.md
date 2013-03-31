verwatch
========

`verwatch` is a python library and CLI tool for monitoring versions of
software packages at various sources like `git` or `rpm` repositories.

Packagers and maintainers might find this tool helpful, especially when
maintaining packages at multiple repositories and versions.

This software is being created at the moment, help me hack it!


WHAT CAN IT DO
--------------

 * fetch versions:
    * `git` (latest version tag)
    * `repoquery` (query rpm repos)
    * `bodhi` (Fedora updates)
    * `koji` (Fedora build system)
 * save versions locally and query them offline
 * use pretty colors to mark latest/old versions
 * tree version structure: package -> release -> repo -> branch
 * supports multiple package configurations
 * filter shown packages using regexp
 * easily write and plug custom version fetchers


WHAT IS PLANNED
---------------

 * HTML output (just a matter of transfroming JSON)
 * automatic fetch on old cache
 * tests?


REQUIREMENTS
------------

Following `python` packages are required:

 * `docopt` for beautiful option parsing
 * `blessings` for funky colors

I hacked it up on python 2.7.
