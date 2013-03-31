package configuration examples
==============================

Files in this directory are examples of verwatch package configurations.

HOW TO USE THEM
---------------

Put any of these into `~/.verwatch/packages` and then use them with
`-p` / `--package-conf` option without `.json` postfix.

For example:

    cp git.json ~/.verwatch/packages/
    verw -p git

The `default.json` package config is used by default, so you can symlink your
favourite config:

    cd ~/.verwatch/packages
    ln -s git.json default.json
