import verwatch.fetchers.bodhi
import verwatch.fetchers.git
import verwatch.fetchers.koji
import verwatch.fetchers.repoquery
try:
    import verwatch.fetchers.distgit
except ImportError:
    # TODO: Something more sofisticated would be nice.
    print "Failed to import distgit fetcher. rpm module missing?"
