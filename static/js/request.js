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
angular.module('request', ['logging'], ['$provide', function(p) {
    p.factory('jsonReq', ['$http', 'msgMgr', function($http, msgMgr) {
        return function (url, callback, error_name, err_cb) {
            $http.get(url, {
                cache: false,
                timeout: 10000
            }).success(callback).error(function (data, status) {
                msgMgr.add(error_name + " error: " + status, 'error');
                if (err_cb) {
                    err_cb(data, status);
                }
            });
        };
    }]);
}]);
