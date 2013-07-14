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
angular.module('logging', [], ['$provide', function($provide) {
    $provide.factory('msgMgr', function () {
        var __msg_id_cnt = 0;
        function MessageManager() {
            this._init.apply(this, arguments);
        }
        MessageManager.prototype = {
            _init: function () {
                this.msgs = [];
            },
            close: function (id) {
                for (var i in this.msgs) {
                    if (!this.msgs.hasOwnProperty(i))
                        continue;
                    if (this.msgs[i].id == id) {
                        this.msgs.remove(i);
                        break;
                    }
                }
            },
            add: function (msg, type) {
                if (!msg)
                    return;
                type = type || "";
                if (this.msgs.length >= 5)
                    this.msgs.length = 4;
                var id = __msg_id_cnt++;
                this.msgs.unshift({
                    id: id,
                    msg: msg,
                    type: type,
                    date: new Date()
                });
                return id;
            },
            has_error: function () {
                for (var i in this.msgs) {
                    if (!this.msgs.hasOwnProperty(i))
                        continue;
                    if (this.msgs[i].type == 'error') {
                        return true;
                    }
                }
                return false;
            }
        };
        return new MessageManager();
    });
}]);
