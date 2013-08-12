#   Copyright (C) 2013~2013 by Yichao Yu
#   yyc1992@gmail.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

_google_cdn = '//ajax.googleapis.com/ajax/libs/'
_bootstrap_cdn = '//netdna.bootstrapcdn.com/'
# _cloudflare_cdn = '//cdnjs.cloudflare.com/ajax/libs/'

jsmodules = {
    'array': {
        'url': 'jsmodule/js/array.js',
        'static': True
    },
    'angular': {
        'url': _google_cdn + 'angularjs/1.1.3/angular.min.js'
    },
    'angular.loader': {
        'url': _google_cdn + 'angularjs/1.1.3/angular-loader.min.js',
    },
    'jquery': {
        'url': _google_cdn + 'jquery/2.0.2/jquery.min.js'
    },
    'bootstrap': {
        'url': _bootstrap_cdn + 'twitter-bootstrap/2.3.2/js/bootstrap.min.js',
        'sync_deps': ('jquery',),
    },
    'angular.ui.bootstrap': {
        'url': "jsmodule/js/ui-bootstrap-tpls-0.3.0.min.js",
        'static': True,
        'deps': ('angular',),
        'sync_deps': ('angular.loader',),
    },
    'angular.gravatar': {
        'url': "jsmodule/js/gravatar-directive.js",
        'static': True,
        'deps': ('angular.md5', 'angular',),
        'sync_deps': ('jquery', 'angular.loader',),
    },
    'angular.md5': {
        'url': "jsmodule/js/md5-service.js",
        'static': True,
        'deps': ('angular',),
        'sync_deps': ('angular.loader',),
    },
    'becv.logging': {
        'url': "jsmodule/js/logging.js",
        'static': True,
        'deps': ('angular',),
        'sync_deps': ('angular.loader', 'array',),
    },
    'becv.request': {
        'url': "jsmodule/js/request.js",
        'static': True,
        'deps': ('angular', 'becv.logging',),
        'sync_deps': ('angular.loader',),
    },
    'bootstrap.datetimepicker': {
        'url': "jsmodule/js/bootstrap-datetimepicker.min.js",
        'static': True,
        'sync_deps': ('jquery', 'bootstrap'),
    },
}
