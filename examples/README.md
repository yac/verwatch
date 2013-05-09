package configuration examples
==============================

Files in this directory are examples of verwatch package configurations:

 * `git.json`, `repoquery.json`, `bodhi.json` and `koji.json` are simple
   examples of individual fetchers.
 * `nova.json` is a complex example showing most verwatch functionality and
   fetchers on the OpenStack Nova project.
 * `openstack-clients.json` is a config I use daily to monitor OpenStack
   clients. Nice for testing package and release regex matching.
 * `openstack.json` is a massive config covering many OpenStack components.


HOW TO USE THEM
---------------

Put any of these into `~/.verwatch/packages` and then use them with
`-p` / `--package-conf` option without `.json` postfix.

For example:

    cp git.json ~/.verwatch/packages/
    verw -p git

The `default.json` package config is used by default so you can symlink your
favourite config:

    cd ~/.verwatch/packages
    ln -s git.json default.json
    verw
