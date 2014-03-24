import fetchers.bodhi
import fetchers.debug
import fetchers.git
import fetchers.koji
import fetchers.repoquery
try:
    import fetchers.cnu
except ImportError:
    print "Failed to import cnucnu fetcher. cnucnu module missing?"
try:
    import fetchers.distgit
except ImportError:
    # TODO: Something more sofisticated would be nice.
    print "Failed to import distgit fetcher. rpm module missing?"
