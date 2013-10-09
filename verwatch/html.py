# -*- encoding: utf-8 -*-
#
# This decadent code is a tribute to the "good" old PHP times of doing
# everything yourself in one file. Enjoy!
#

import verwatch.util


CSS = \
"""div.release, div.repo, div.branches { padding: 0; margin: 9px 30px; }
h2.package, h3.release, h4.repo { margin: 0; padding: 0.3em 0 0.2em 8px; }

div.package { margin-bottom: 3em; }
h2.package { font-size: 36px; color: #034769; padding-left: 0px; }

div.release { margin-bottom: 1em; }
h3.release { font-size: 24px; color: #086FA1; }

h4.repo { font-size: 18px; color: #04819E; }

table.branches { margin-left: 30px; }
table.branches td { padding: 0 0.5em 0.2em; }
table.branches td.branch { font-weight: bold; text-align: right; }
table.branches td.version { font-weight: bold; padding-left: 0.4em; }

.ver-old, .ver-unknown { color: #CC9900; }
.ver-new { color: #336633; }
.ver-error { color: #A60000; }
.ver-sep { color: #9A9A9A; font-weight: normal; }
.ver-extra { color: #444444; font-weight: normal; }
"""


PAGE_TEMPLATE="""
<!DOCTYPE html>
<html>
<head>
<title>%(title)s</title>
<style type="text/css">
body { padding: 0; margin: 0; }

%(css)s
</style>
</head>

<body>
%(body)s
</body>
</html>
"""

def render_version_html(ver, max_ver=None, show_error=False):
    s = ''
    if 'version' in ver:
        if 'epoch' in ver:
            s += ('<span class="ver-epoch ver-extra">%s</span>'
                  '<span class="ver-sep">:</span>' % ver['epoch'])
        v = ver['version']
        if max_ver and v == max_ver:
            s += '<span class="ver-new">%s</span>' % v
        else:
            s += '<span class="ver-old">%s</span>' % v
        if 'release' in ver:
            r = ver['release']
            s += ('<span class="ver-sep">-</span>'
                  '<span class="ver-release ver-extra">%s</span>'
                  % ver['release'])
    else:
        if show_error:
            try:
                err_msg = ver['error']
            except KeyError:
                err_msg = ("BUG: No version fetched but fetcher didn't return "
                           "error. Fetcher bug!")
        else:
            err_msg = '!!'
        s += '<span class="ver-error">%s</span>' % err_msg
    if 'next' in ver:
        next_ver = ver['next']
        if not verwatch.util.is_same_version(ver, next_ver):
            s += ' &nbsp; &rarr; &nbsp; ' + \
                 render_version_html(next_ver, max_ver)
    return s


def render_versions_html(pkg_conf, vers):
    first = True
    pkgs = pkg_conf['packages']
    html = "<div class='versions'>\n"
    for pkg in pkgs:
        rlss = pkg['releases']
        pkg_name = pkg['name']
        if first:
            first = False
        else:
            html += "\n"
        html += ("<div class=\"package\" id=\"pkg-%s\"><h2 class=\"package\">"
                 "%s</h2>\n" % (pkg_name, pkg_name))
        for rls in rlss:
            html += "<div class=\"release\"><h3 class=\"release\">%s</h3>\n" \
                    % rls['name']
            max_ver = verwatch.util.release_latest_version(rls, vers, pkg_name)
            # print all release versions
            for repo in rls['repos']:
                repo_name = repo['repo']
                repo_title = verwatch.util.get_repo_title(pkg_conf, repo_name)
                html += "<div class=\"repo\">\n<h4 class=\"repo\">%s</h4>\n" \
                        % repo_title
                html += "<table class=\"branches\">\n"
                for branch in repo['branches']:
                    try:
                        ver = vers[pkg_name][repo_name][branch]
                        ver_str = render_version_html(ver, max_ver)
                    except KeyError:
                        ver_str = '<span class="ver-unknown">??</span>'
                    html += ("<tr><td class=\"branch\">%s:</td>"
                             "<td class=\"version\">%s</td></tr>\n"
                             % (branch, ver_str))
                html += "</table>\n</div>\n"
            html += "</div>\n"
        html += "</div>\n"
    html += "</div>\n"
    return html


def render_versions_html_page(pkg_conf, vers, title="verwatch versions"):
    page = PAGE_TEMPLATE % {
           'css': CSS,
           'body': render_versions_html(pkg_conf, vers),
           'title': title
           }
    return page
