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
angular.module('log_mgr', ['request'], ['$provide', function($provide) {
    $provide.factory('logMgr', ['jsonReq', function (jsonReq) {
        function LogMgr() {
            this._init.apply(this, arguments);
        }

        LogMgr.prototype = {
            update: function (from, to) {
                var that = this;
                this._cur_id++;
                var cur_id = this._cur_id;
                var _url = this._url + '?' + $.param({
                    from: from,
                    to: to
                });
                jsonReq(_url, function (data, status) {
                    if (that._cur_id != cur_id)
                        return
                    that.cur = data.logs;
                    that.is_all = data.is_all;
                }, "Get " + this._name + " Logs.");
            },
            _init: function (_url, _name) {
                this._url = _url;
                this._name = _name;
                this.cur = [];
                this.is_all = true;
                this._cur_id = 0;
            }
        };

        return LogMgr;
    }]);
}]);
