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
angular.module('room_temp', ['logging', 'request', 'popup_form', 'ui.bootstrap'], ['$provide', function(p) {
    p.factory('roomTempMgr', ['msgMgr', 'jsonReq', '$dialog', 'popupForm', function(msgMgr, jsonReq, dlg, popupForm) {
        var url_prefix = ScriptLoader.get_context('room_temp_prefix');
        function RoomTempMgr() {
            this._init.apply(this, arguments);
        }

        RoomTempMgr.prototype = {
            _init: function () {
                this.server_ids = [];
                this.servers = {};
                this.update_servers();
                this.cur_server = null;
                this.server_devices = {};
                this.all_devices = {};
                this.update_devices();
            },
            _show_device_dialog: function (values, cb) {
                var servers = [];
                for (var i in this.server_ids) {
                    var id = this.server_ids[i];
                    servers.push(this.servers[id]);
                }
                var inputs = [{
                    id: 'name',
                    name: 'Name',
                    longname: 'Device Name',
                    required: true
                }, {
                    id: 'unit',
                    name: 'Unit',
                    longname: 'Server Unit',
                }, {
                    id: 'server',
                    name: 'Server',
                    type: 'select',
                    opts: servers,
                    required: true,
                }, {
                    id: 'order',
                    name: 'Order',
                    longname: 'Device Order',
                    type: 'number',
                    advanced: true
                }];
                var f = new popupForm('Device Setting', inputs, values);
                f.open().then(cb);
            },
            add_device: function () {
                var that = this;
                this._show_device_dialog({
                    order: 0.0,
                    unit: "\xB0C",
                    server: this.cur_server
                }, function (res) {
                    if (!res)
                        return;
                    var url = url_prefix + 'add-device/?' + $.param(res);
                    jsonReq(url, function (data, status) {
                        msgMgr.add('Successfully added device "' +
                                   data.name + '".', 'success');
                        that.update_devices();
                    }, 'Add Server');
                });
            },
            edit_device: function (id) {
                var url = url_prefix + 'get-device-setting/' + id + '/';
                var that = this;
                jsonReq(url, function (data, status) {
                    that._show_device_dialog(data, function (res) {
                        if (!res)
                            return;
                        if ('id' in res)
                            delete res.id;
                        var url = url_prefix + 'edit-device/' + id;
                        url += '/?' + $.param(res);
                        jsonReq(url, function (data, status) {
                            msgMgr.add('Successfully edited device "' +
                                       data.name + '".', 'success');
                            that.update_devices();
                        }, 'Edit device');
                    });
                }, "Get device setting.");
            },
            remove_device: function (id) {
                var that = this;
                var server = this.all_devices[id];
                var msgbox = dlg.messageBox(
                    'Delete Device',
                    'Do you REALLY want to delete device' + server.name + '?',
                    [{
                        label: "Yes, I'm sure",
                        result: 'yes',
                        cssClass: 'btn-danger'
                    }, {
                        label: "Nope",
                        result: 'no'
                    }]);
                msgbox.open().then(function (result) {
                    if (!(result === 'yes'))
                        return;
                    var url = url_prefix + 'del-device/' + id + '/';
                    jsonReq(url, function (data, status) {
                        msgMgr.add('Successfully deleted device "' +
                                   server.name + '".', 'success');
                        that.update_devices();
                    }, 'Delete device');
                });
            },
            update_devices: function () {
                var that = this;
                jsonReq(url_prefix + 'get-devices/', function (data, status) {
                    that.server_devices = {};
                    for (var id in data) {
                        if (!data.hasOwnProperty(id))
                            continue;
                        var devices = data[id];
                        var ids = [];
                        that.server_devices[id] = ids;
                        for (var j in devices) {
                            if (!devices.hasOwnProperty(j))
                                continue;
                            var device = devices[j];
                            ids.push(device.id);
                            that.all_devices[device.id] = device;
                        }
                    }
                }, "Get devices list.");
            },
            update_servers: function () {
                var that = this;
                jsonReq(url_prefix + 'get-servers/', function (data, status) {
                    that.server_ids = [];
                    that.servers = {};
                    for (var i in data) {
                        if (!data.hasOwnProperty(i))
                            continue;
                        var server = data[i];
                        that.server_ids.push(server.id);
                        that.servers[server.id] = server;
                        if (!(that.cur_server in that.servers)) {
                            that.cur_server = null;
                        }
                    }
                }, "Get servers list.");
            },
            set_current_server: function (id) {
                this.cur_server = id;
            },
            _show_server_dialog: function (values, cb) {
                var inputs = [{
                    id: 'name',
                    name: 'Name',
                    longname: 'Server Name',
                    required: true
                }, {
                    id: 'addr',
                    name: 'Address',
                    longname: 'Server Address',
                    required: true
                }, {
                    id: 'port',
                    name: 'Port',
                    longname: 'Server Port',
                    type: 'number',
                    step: 1,
                    min: 1,
                    max: 65535,
                    required: true
                }, {
                    id: 'order',
                    name: 'Order',
                    longname: 'Server Order',
                    type: 'number',
                    advanced: true
                }];
                var f = new popupForm('Server Setting', inputs, values);
                f.open().then(cb);
            },
            add_server: function () {
                var that = this;
                this._show_server_dialog({
                    order: 0.0,
                    port: 23,
                }, function (res) {
                    if (!res)
                        return;
                    var url = url_prefix + 'add-server/?' + $.param(res);
                    jsonReq(url, function (data, status) {
                        msgMgr.add('Successfully added server "' +
                                   data.name + '".', 'success');
                        that.update_servers();
                        that.update_devices();
                    }, 'Add Server');
                });
            },
            edit_server: function (id) {
                var url = url_prefix + 'get-server-setting/' + id + '/';
                var that = this;
                jsonReq(url, function (data, status) {
                    that._show_server_dialog(data, function (res) {
                        if (!res)
                            return;
                        if ('id' in res)
                            delete res.id;
                        var url = url_prefix + 'edit-server/' + id;
                        url += '/?' + $.param(res);
                        jsonReq(url, function (data, status) {
                            msgMgr.add('Successfully edited server "' +
                                       data.name + '".', 'success');
                            that.update_servers();
                            that.update_devices();
                        }, 'Edit server');
                    });
                }, "Get server setting.");
            },
            remove_server: function (id) {
                var that = this;
                var server = this.servers[id];
                var msgbox = dlg.messageBox(
                    'Delete Server',
                    'Do you REALLY want to delete server' + server.name + '?',
                    [{
                        label: "Yes, I'm sure",
                        result: 'yes',
                        cssClass: 'btn-danger'
                    }, {
                        label: "Nope",
                        result: 'no'
                    }]);
                msgbox.open().then(function (result) {
                    if (!(result === 'yes'))
                        return;
                    var url = (url_prefix + 'del-server/' + id + '/');
                    jsonReq(url, function (data, status) {
                        msgMgr.add('Successfully deleted server "' +
                                   server.name + '".', 'success');
                        that.update_servers();
                        that.update_devices();
                    }, 'Delete server');
                });
            },
        };

        return new RoomTempMgr();
    }]);
}]);
