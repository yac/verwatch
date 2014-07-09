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
    * `distgit` (RPM specfile version in git)
    * `repoquery` (query rpm repos)
    * `bodhi` (Fedora updates)
    * `koji` (Fedora build system, brew also works)
 * save versions locally and query them offline
 * use colors to mark latest/old versions
 * HTML output (whole page or just embeddable/stylable tags)
 * tree version structure: package -> release -> repo -> branch
 * supports multiple package configurations
 * filter listed/updated packages and releases using regexp
   (easy selective update)
 * easily write, plug in and contribute custom version fetchers
 * give false feeling of safety during development with few unit tests


WHAT MIGHT BE DONE IN FUTURE
----------------------------

 * better documentation?
 * automatic update on old cache?


REQUIREMENTS
------------

Following `python` packages are required:

 * `blessings` for terminal colors
 * `docopt` for beautiful option parsing

In case above list isn't up to date, [requirements.txt](requirements.txt)
should be.

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
 * `verw -p clients` :  use `~/.verwatch/packages/clients.yaml` package config.
 * `verw 'nova|cinder'` :  show versions of packages matching supplied regex.
 * `verw -U -r 'grizzly' 'nova|cinder'` :  update versions/releases of packages
   matching supplied regexes and exit.

For library usage, see `shell.py`.


QUICKSTART
----------

    # your package manager or at least `pip` are better choices for installing
    # python packages, but `easy_install` Just Works (TM)
    sudo easy_install blessings docopt
    git clone https://github.com/yac/verwatch.git
    cd verwatch
    sudo python setup.py install
    mkdir -p ~/.verwatch/packages
    cp examples/nova.yaml ~/.verwatch/packages
    cd ~/.verwatch/packages
    ln -s nova.yaml default.yaml
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


TESTS
-----

There are unit tests in case you'd like to hack verwatch.

You'll need `py.test`. Run it in top verwatch directory:

    py.test

Or run `./run_tests.sh` script which does exactly that.
