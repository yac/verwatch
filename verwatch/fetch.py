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

    def __init__(self, paths=None, options=None):
        pass

    def get_version(self, pkg_name, branch):
        """
        This must return a hash with either 'version' or 'error'.

        Optionally, 'next_version' hash can be provided as well.
        """
        raise NotImplementedError
