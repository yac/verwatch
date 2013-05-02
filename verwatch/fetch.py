class VersionFetcherMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'fetchers'):
            cls.fetchers = {}
        else:
            cls.fetchers[cls.name] = cls


class VersionFetcher:
    """
    Subclass this to create a version fetcher.

    Provide:
      * `name` attribute
      * `get_version()` function
    """
    __metaclass__ = VersionFetcherMount

    def __init__(self, paths=None, options=None, title=None,
                 alter_pkg_name=None):
        """
        If you override __init__(), don't forget to call this!

        Only keyword arguments are used so you can use::

            def __init__(self, **kwargs):
                VersionFetcher.__init__(self, **kwargs)
                # inspect kwargs here

        to create a fetcher resiliant to argument changes.
        """
        self.title = title
        self.alter_pkg_name = alter_pkg_name

    def get_real_pkg_name(self, pkg_name):
        """
        Apply self.alter_pkg_name if provided.

        Do *not* modify.
        """
        if self.alter_pkg_name:
            if "prefix" in self.alter_pkg_name:
                pkg_name = self.alter_pkg_name["prefix"] + pkg_name
            if "postfix" in self.alter_pkg_name:
                pkg_name += self.alter_pkg_name["postfix"]
        return pkg_name

    def get_version(self, pkg_name, branch):
        """
        Do *not* modify, see _get_version() below.
        """
        real_pkg_name = self.get_real_pkg_name(pkg_name)
        return self._get_version(real_pkg_name, branch)

    def _get_version(self, pkg_name, branch):
        """
        Override this in your subclass, this is where magic happens.

        Must return a dict with either 'version' or 'error' key.

        returned dict can also optionaly contain:
          * 'release'
          * 'epoch'
          * recursive 'next' dict(s) of next/pending/candidate versions
        """
        raise NotImplementedError
