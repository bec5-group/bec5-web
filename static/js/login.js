/**
 *   Copyright (C) 2013~2013 by Yichao Yu
 *   yyc1992@gmail.com
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 **/
var login_app = angular.module(
    'login', ['ui.bootstrap'],
    ['$interpolateProvider', '$dialogProvider', function(interpolate, dlg) {
        interpolate.startSymbol('{[');
        interpolate.endSymbol(']}');
    }]
);
login_app
    .directive('redirectCnt', function () {
        return {
            link: function ($scope, $ele, $attrs) {
                var url = $attrs.titleBtn;
                var timeout = parseInt($attrs.timeout);
                if (!url)
                    url = "/";
                if (url.search('#') < 0)
                    url += location.hash;
                if (!timeout || timeout <= 0)
                    timeout = 5;

                function check_timeout() {
                    $ele.text(timeout);
                    if (timeout) {
                        timeout--;
                    } else {
                        clearInterval(interval_id);
                        window.location = url;
                    }
                }

                check_timeout();
                var interval_id = setInterval(check_timeout, 1000);
            }
        };
    })
    .directive('hrefHash', function () {
        return {
            link: function ($scope, $ele, $attrs) {
                var attr = $attrs.hrefHash;
                if (!attr)
                    attr = "href";
                var url = $attrs[attr];
                if (!url)
                    url = "";
                url += location.hash;
                $ele.attr(attr, url);
            }
        };
    });
