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
 * use colors to mark latest/old versions
 * tree version structure: package -> release -> repo -> branch
 * supports multiple package configurations
 * filter shown packages and releases using regexp
 * easily write, plug in and contribute custom version fetchers


WHAT IS PLANNED
---------------

 * HTML output (just a matter of transfroming JSON)
 * selective fetch (fetching can take a long time)
 * automatic fetch on old cache
 * documentation
 * tests?


REQUIREMENTS
------------

Following `python` packages are required:

 * `docopt` for beautiful option parsing
 * `blessings` for funky colors

I hacked it up on python 2.7.


CONFIGURATION
-------------

See `examples` folder for sample package configurations.

`examples/README.md` explains where to put them and how to use them.


USAGE
-----

There is `verw` CLI frontend. Some use cases:

 * `verw` :  lists versions for default packages.
 * `verw -u` :  updates and shows versions for default packages.
 * `verw -p clients` :  use `~/.verwatch/packages/clients.json` package config.
 * `verw 'nova|cinder'` :  show versions for packages matching supplied regex.

For library usage, see `shell.py`.


QUICKSTART
----------

    # your package manager or at least `pip` are better choices for installing
    # python packages, but `easy_install` Just Works (TM)
    sudo easy_install blessings docopt
    git clone git@github.com:yac/verwatch.git
    cd verwatch
    sudo python setup.py install
    mkdir -p ~/.verwatch/packages
    cp examples/nova.json ~/.verwatch/packages
    cd ~/.verwatch/packages
    ln -s nova.json default.json
    verw


MAKE YOUR OWN VERSION FETCHER - EASY AS PIE!
--------------------------------------------

Long story short:

 1. Copy a builtin fetcher of your choice from `verwatch/fetchers` to `~/.verwatch/plugins`.
 2. Modify to your needs. Check out `verwatch/fetch.py:VersionFetcher` for moar info.
 3. ???
 4. **Profit!**

`~/.verwatch/plugins/*.py` are loaded automatically and any subclasses of
`verwatch.fetch.VersionFetcher` are registered as version fetchers.

To use your shiny new fetcher, just reference it in package configuration by
its `name`.
