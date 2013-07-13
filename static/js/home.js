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
becv_app
    .constant("titleBtnConfig", {
        activeClass: "active"
    })
    .directive('titleBtn', ['titleBtnConfig', '$parse', function (titleBtnConfig,
                                                                  $parse) {
        var _activeClass = titleBtnConfig.activeClass || 'active';
        return {
            link: function ($scope, $ele, $attrs) {
                var name = $scope.$eval($attrs.titleBtn);
                var model_name = $attrs.titleBtnModel;
                var on_click = $scope.$eval($attrs.titleBtnClicked);
                var activeClass = $attrs.titleBtnActive || _activeClass;

                $scope.$watch(function () {
                    return $scope.$eval(model_name);
                }, function (modelValue) {
                    if (angular.equals(modelValue, name)){
                        $ele.addClass(activeClass);
                    } else {
                        $ele.removeClass(activeClass);
                    }
                });

                $ele.bind("click", function () {
                    if (on_click) {
                        on_click(name);
                    } else {
                        $scope.$apply(function () {
                            $parse(model_name).assign($scope, name);
                        });
                    }
                });
            }
        };
    }]);
becv_app.directive('condDisp', function () {
    return {
        link: function ($scope, $ele, $attrs) {
            var exp = $attrs.condDisp;
            var value = $scope.$eval(exp);
            var disp_type = $attrs.condDispType;
            if (!disp_type)
                disp_type = "inline-block";

            $scope.$watch(function () {
                value = $scope.$eval(exp);
                if ($.isPlainObject(value))
                    value = !$.isEmptyObject(value)
                return value;
            }, function (modelValue) {
                if (value){
                    $ele.css("display", disp_type);
                } else {
                    $ele.css("display", "none");
                }
            });
        }
    };
});
// Array Remove - By John Resig (MIT Licensed)
Array.prototype.remove = function(from, to) {
    if (from)
        from = parseInt(from);
    if (to)
        to = parseInt(to);
    var rest = this.slice((to || from) + 1 || this.length);
    this.length = from < 0 ? this.length + from : from;
    return this.push.apply(this, rest);
};

becv_app.controller('HomePageCtrl', ['$scope', '$http', '$dialog', '$location', function ($scope, $http, $dialog, $location) {
    $scope.init = function (permissions, user) {
        $scope.show_advanced_actions = false;
        $scope.condVar = function (cond, t, f) {
            if (cond)
                return t;
            return f;
        };
        $scope.user = user;
        $scope.redirect_to_login = function (name) {
            window.location = '/accounts/login/?next=/#' + name
        };
        var permission_alert_count = {};
        $scope.redirect_or_message = function (name) {
            if (!$scope.user.username) {
                $scope.redirect_to_login(name);
            } else {
                if (permission_alert_count[name])
                    return;
                permission_alert_count[name] = 1;
                alert('Sorry your account ' + $scope.user.username +
                      ' is not allowed to preform this action.');
                // Some how doesn't work properly.
                // var msgbox = $dialog.messageBox(
                //     'Sorry',
                //     ('Sorry your account ' + $scope.user.username +
                //      'is not allowed to preform this action.'), [{
                //          label: "Close",
                //          result: 'close'
                //      }]);
                // msgbox.open();
            }
        }
        $scope.permissions = permissions;
        $scope.home_tabs = {
            all: [{
                id: 'oven-temp',
                name: 'Oven Temperature'
            }, {
                id: 'oven-control',
                name: 'Oven Control'
            }],
            log: [{
                id: 'oven-action-log',
                name: 'User Action Log'
            }, {
                id: 'oven-ctrl-log',
                name: 'Oven Controller Log'
            }, {
                id: 'oven-temp-log',
                name: 'Oven Temperature Log'
            }, {
                id: 'room-temp-log',
                name: 'Room Temperature Log'
            }],
            active: 'oven-temp'
        }
        function is_in_tabs(perm, tabs) {
            for (var i in tabs) {
                if (perm == tabs[i].id) {
                    return true;
                }
            }
            return false;
        }
        function is_tab(perm) {
            return (is_in_tabs(perm, $scope.home_tabs.all) ||
                    is_in_tabs(perm, $scope.home_tabs.log));
        }
        $scope.has_advanced_actions = false;
        for (var perm in permissions) {
            if ((!permissions[perm]) || is_tab(perm))
                continue;
            $scope.has_advanced_actions = true;
            break;
        }
        if ($location.path()) {
            var hash_tab = $location.path().substring(1);
            var all_tabs = $scope.home_tabs.all.concat($scope.home_tabs.log);
            for (var i in all_tabs) {
                if (all_tabs[i].id == hash_tab) {
                    if ($scope.permissions[hash_tab]) {
                        $scope.home_tabs.active = hash_tab;
                    } else if ($scope.user.username) {
                        $location.path('/');
                    } else {
                        $scope.redirect_to_login('/' + hash_tab);
                    }
                    break;
                }
            }
        }

        $scope.messages = [];
        $scope.close_message = function (id) {
            for (var i in $scope.messages) {
                if (!$scope.messages.hasOwnProperty(i))
                    continue;
                if ($scope.messages[i].id == id) {
                    $scope.messages.remove(i);
                    break;
                }
            }
        };
        var message_id_cnt = 0;
        function add_message(msg, type) {
            if (!msg)
                return;
            type = type || "";
            if ($scope.messages.length >= 5)
                $scope.messages.length = 4;
            var id = message_id_cnt++;
            $scope.messages.unshift({
                id: id,
                message: msg,
                type: type,
                date: new Date()
            });
            return id;
        };
        $scope.message_has_error = function () {
            for (var i in $scope.messages) {
                if (!$scope.messages.hasOwnProperty(i))
                    continue;
                if ($scope.messages[i].type == 'error') {
                    return true;
                }
            }
            return !$.isEmptyObject($scope.TProfile.cur_error);
        };

        function json_request(url, callback, error_name, err_cb) {
            $http.get(url, {
                cache: false,
                timeout: 10000
            }).success(callback).error(function (data, status) {
                add_message(error_name + " error: " + status, 'error');
                if (err_cb) {
                    err_cb(data, status);
                }
            });
        }

        $scope.TControls = [];
        $scope.auto_temp = false;

        $scope.TValues = {};

        function get_ovens() {
            json_request('/oven-control/get-ovens/', function (data, status) {
                $scope.TControls = data;
            }, "Get ovens list");
        }

        function get_profiles() {
            json_request('/oven-control/get-profiles/', function (data, status) {
                $scope.TProfile.set_profiles(data);
            }, "Get profile list");
        }

        function update_temps() {
            json_request('/oven-control/get-temps/', function (data, status) {
                $scope.TValues = data;
            }, "Get temperatures");
        }
        get_ovens();
        get_profiles();
        update_temps();

        setInterval(function () {
            if ($scope.auto_temp) {
                update_temps();
                $scope.TProfile.update_cur_errors();
            }
        }, 10000);

        function TempProfileMgr() {
            this._init.apply(this, arguments);
        }

        TempProfileMgr.prototype = {
            set_profiles: function (profiles) {
                var ids = [];
                var all = {};
                for (var i in profiles) {
                    ids[i] = profiles[i].id;
                    all[profiles[i].id] = profiles[i];
                }
                this.ids = ids;
                this.all = all;
            },
            set_cur: function (id) {
                this.cur_changed = true;
                this.cur = id;
            },
            update_cur_setpoint: function () {
                var that = this;
                json_request('/oven-control/get-setpoint/', function (data, status) {
                    that.cur_setpoint = data;
                    if (!that.cur_changed || !that.cur) {
                        that.cur = data.id;
                    }
                }, "Get current set point.");
            },
            update_cur_errors: function () {
                if (!$scope.user.username)
                    return;
                var that = this;
                json_request('/oven-control/get-errors/', function (data, status) {
                    that.cur_error = data;
                }, "Get current error.");
            },
            _init: function () {
                this.ids = [];
                this.all = {};
                this.cur = '';
                this.status = 0;
                this.cur_setpoint = {};
                this.cur_changed = false;
                this.update_cur_setpoint();
                this.editing_setpoint = false;
                this.edited_setpoint = {};
                this.cur_error = {};
                this.update_cur_errors();
            },
            edit_setpoint: function () {
                if (this.editing_setpoint) {
                    var that = this;
                    var url = ('/oven-control/set-temps/?' +
                               $.param(this.edited_setpoint));
                    json_request(url, function (data, status) {
                        add_message('Successfully changed setpoint', 'success');
                        that.update_cur_setpoint();
                        that.editing_setpoint = false;
                    }, 'Change Setpoint');
                } else {
                    this.edited_setpoint = {}
                    for (var id in this.cur_setpoint.temps) {
                        if (!this.cur_setpoint.temps.hasOwnProperty(id))
                            continue;
                        // value from this.cur_setpoint.temps may be strings
                        this.edited_setpoint[id] = parseFloat(
                            this.cur_setpoint.temps[id]);
                    }
                    this.editing_setpoint = true;
                }
            },
            cancel_edit_setpoint: function () {
                this.editing_setpoint = false;
                this.edited_setpoint = {};
            },
            do_apply: function () {
                if (!this.all[this.cur])
                    return;
                this.status = 1;
                var that = this;
                var cur = this.all[this.cur].name;
                this.cur_changed = false;
                var url = '/oven-control/set-profile/' + this.cur + '/';
                json_request(url, function (data, status) {
                    that.status = 2;
                    add_message('Successfully set profile to "' +
                                cur + '".', 'success');
                    that.update_cur_setpoint();
                }, 'Set profile to "' + cur + '"', function (data, status) {
                    that.status = 3;
                });
            },
            show_profile_dialog: function (values, cb) {
                var d = $dialog.dialog({
                    resolve: {
                        value: function () {
                            return values;
                        }
                    }
                });
                d.open('/static/html/profile_edit.html',
                       'ProfileEditCtrl').then(cb);
            },
            add_profile: function () {
                this.show_profile_dialog({
                    order: 0.0,
                    ctrls: $scope.TControls,
                    temps: {}
                }, function (res) {
                    if (!res)
                        return;
                    var url = '/oven-control/add-profile/' + res.name;
                    if (!(res.order === undefined))
                        url += '/' + res.order;
                    url += '/?' + $.param(res.temps);
                    json_request(url, function (data, status) {
                        add_message('Successfully added profile "' +
                                    data.name + '".', 'success');
                        get_profiles();
                    }, 'Add Profile');
                });
            },
            edit_profile: function (id) {
                var url = '/oven-control/get-profile-setting/' + id + '/';
                var that = this;
                json_request(url, function (data, status) {
                    data.ctrls = $scope.TControls;
                    that.show_profile_dialog(data, function (res) {
                        if (!res)
                            return;
                        var url = '/oven-control/edit-profile/' + id + '/' + res.name;
                        if (!(res.order === undefined))
                            url += '/' + res.order;
                        url += '/?' + $.param(res.temps);
                        json_request(url, function (data, status) {
                            add_message('Successfully changed profile "' +
                                        data.name + '".', 'success');
                            get_profiles();
                        }, 'Edit profile');
                    });
                }, "Get profile setting.");
            },
            remove_profile: function (id) {
                var that = this;
                var profile = this.all[id];
                var msgbox = $dialog.messageBox(
                    'Delete Profile',
                    'Do you REALLY want to delete profile' + profile.name + '?',
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
                    var url = ('/oven-control/del-profile/' + profile.id + '/');
                    json_request(url, function (data, status) {
                        add_message('Successfully deleted profile "' +
                                    profile.name + '".', 'success');
                        get_profiles();
                    }, 'Delete profile');
                });
            },
        }

        $scope.TProfile = new TempProfileMgr();
        $scope.log_collapsed = false;

        function showControllerDialog(values, cb) {
            var d = $dialog.dialog({
                resolve: {
                    value: function () {
                        return values;
                    }
                }
            });
            d.open('/static/html/controller_edit.html',
                   'CtrlEditCtrl').then(cb);
        }

        $scope.setController = function (id) {
            var url = '/oven-control/get-ctrl-setting/' + id + '/';
            json_request(url, function (data, status) {
                showControllerDialog(data, function (res) {
                    if (!res)
                        return;
                    var url = ('/oven-control/set-controller/' + id + '/?' +
                               $.param(res));
                    json_request(url, function (data, status) {
                        add_message('Successfully changed controller "' +
                                    data.name + '".', 'success');
                        get_ovens();
                        update_temps();
                    }, 'Change controller Settings');
                });
            }, "Get controller setting.");
        }

        $scope.addController = function () {
            showControllerDialog({
                port: 1000,
                number: 1,
                order: 0.0,
                default_temp: 200.0
            }, function (res) {
                if (!res)
                    return;
                var url = '/oven-control/add-controller/?' + $.param(res);
                json_request(url, function (data, status) {
                    add_message('Successfully added controller "' +
                                data.name + '".', 'success');
                    get_ovens();
                    update_temps();
                }, 'Add Controller');
            });
        };

        $scope.removeController = function (ctrl) {
            var msgbox = $dialog.messageBox(
                'Delete Controller',
                'Do you REALLY want to delete controller' + ctrl.name + '?', [{
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
                var url = ('/oven-control/del-controller/' + ctrl.id + '/');
                json_request(url, function (data, status) {
                    add_message('Successfully deleted controller "' +
                                ctrl.name + '".', 'success');
                    get_ovens();
                    update_temps();
                }, 'Delete controller');
            });
        };

        $scope.timestamp_to_string = function (t) {
            var d = new Date(t * 1000);
            return d.toLocaleString();
        };
        var log_classes = {
            'INFO': 'info',
            'ERROR': 'error',
            'FATAL': 'error',
            'CRITICAL': 'error',
            'WARNING': 'warning',
        };
        $scope.log_type_to_class = function (t) {
            return log_classes[t] || '';
        };
        $scope.disp_obj = function (o) {
            if (!o)
                return '';
            return JSON.stringify(o, null, ' ');
        };


        function LogManager() {
            this._init.apply(this, arguments);
        }

        LogManager.prototype = {
            update_logs: function (from, to) {
                var that = this;
                this._cur_id++;
                var cur_id = this._cur_id;
                var _url = this._url + '?' + $.param({
                    from: from,
                    to: to
                });
                json_request(_url, function (data, status) {
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

        $scope.TActionLog = new LogManager('/json-view/get-logs/', "Action");
        $scope.ControllerLog = new LogManager('/oven-control/get-logs/',
                                              "Controller");

        $('.becv-date-time-picker').datetimepicker();
        var auth_log_from_picker = $('#action-log-from').data('datetimepicker');
        var auth_log_to_picker = $('#action-log-to').data('datetimepicker');
        auth_log_from_picker.setLocalDate(null);
        auth_log_to_picker.setLocalDate(null);
        $scope.update_auth_logs = function () {
            var _from = +(auth_log_from_picker.getLocalDate() ||
                          new Date()) / 1000;
            var _to = +(auth_log_to_picker.getLocalDate() ||
                        new Date()) / 1000;
            $scope.TActionLog.update_logs(_from, _to);
        };

        var ctrl_log_from_picker = $('#ctrl-log-from').data('datetimepicker');
        var ctrl_log_to_picker = $('#ctrl-log-to').data('datetimepicker');
        ctrl_log_from_picker.setLocalDate(null);
        ctrl_log_to_picker.setLocalDate(null);
        $scope.update_ctrl_logs = function () {
            var _from = +(ctrl_log_from_picker.getLocalDate() ||
                          new Date()) / 1000;
            var _to = +(ctrl_log_to_picker.getLocalDate() ||
                        new Date()) / 1000;
            $scope.ControllerLog.update_logs(_from, _to);
        };

        $scope.addr_to_str = function (addr) {
            if (!$.isArray(addr))
                return addr;
            return addr.join(':');
        };

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
            show_device_dialog: function (values, cb) {
                values.server_ids = this.server_ids;
                values.servers = this.servers;
                var d = $dialog.dialog({
                    resolve: {
                        value: function () {
                            return values;
                        }
                    }
                });
                d.open('/static/html/room_device_edit.html',
                       'RoomDeviceEditCtrl').then(function (res) {
                           if (res) {
                               for (var key in ['server_ids', 'servers']) {
                                   delete res[key];
                               }
                           }
                           cb(res);
                       });
            },
            add_device: function () {
                var that = this;
                this.show_device_dialog({
                    order: 0.0,
                    unit: "\xB0C",
                    server: this.cur_server
                }, function (res) {
                    if (!res)
                        return;
                    var url = '/room-temp/add-device/?' + $.param(res);
                    json_request(url, function (data, status) {
                        add_message('Successfully added device "' +
                                    data.name + '".', 'success');
                        that.update_devices();
                    }, 'Add Server');
                });
            },
            edit_device: function (id) {
                var url = '/room-temp/get-device-setting/' + id + '/';
                var that = this;
                json_request(url, function (data, status) {
                    that.show_device_dialog(data, function (res) {
                        if (!res)
                            return;
                        if ('id' in res)
                            delete res.id;
                        var url = '/room-temp/edit-device/' + id;
                        url += '/?' + $.param(res);
                        json_request(url, function (data, status) {
                            add_message('Successfully edited device "' +
                                        data.name + '".', 'success');
                            that.update_devices();
                        }, 'Edit device');
                    });
                }, "Get device setting.");
            },
            remove_device: function (id) {
                var that = this;
                var server = this.all_devices[id];
                var msgbox = $dialog.messageBox(
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
                    var url = ('/room-temp/del-device/' + id + '/');
                    json_request(url, function (data, status) {
                        add_message('Successfully deleted device "' +
                                    server.name + '".', 'success');
                        that.update_devices();
                    }, 'Delete device');
                });
            },
            update_devices: function () {
                var that = this;
                json_request('/room-temp/get-devices/', function (data, status) {
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
                json_request('/room-temp/get-servers/', function (data, status) {
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
            show_server_dialog: function (values, cb) {
                var d = $dialog.dialog({
                    resolve: {
                        value: function () {
                            return values;
                        }
                    }
                });
                d.open('/static/html/room_server_edit.html',
                       'RoomServerEditCtrl').then(cb);
            },
            add_server: function () {
                var that = this;
                this.show_server_dialog({
                    order: 0.0,
                    port: 23,
                }, function (res) {
                    if (!res)
                        return;
                    var url = '/room-temp/add-server/?' + $.param(res);
                    json_request(url, function (data, status) {
                        add_message('Successfully added server "' +
                                    data.name + '".', 'success');
                        that.update_servers();
                        that.update_devices();
                    }, 'Add Server');
                });
            },
            edit_server: function (id) {
                var url = '/room-temp/get-server-setting/' + id + '/';
                var that = this;
                json_request(url, function (data, status) {
                    that.show_server_dialog(data, function (res) {
                        if (!res)
                            return;
                        if ('id' in res)
                            delete res.id;
                        var url = '/room-temp/edit-server/' + id;
                        url += '/?' + $.param(res);
                        json_request(url, function (data, status) {
                            add_message('Successfully edited server "' +
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
                var msgbox = $dialog.messageBox(
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
                    var url = ('/room-temp/del-server/' + id + '/');
                    json_request(url, function (data, status) {
                        add_message('Successfully deleted server "' +
                                    server.name + '".', 'success');
                        that.update_servers();
                        that.update_devices();
                    }, 'Delete server');
                });
            },
        };

        $scope.room_temp_mgr = new RoomTempMgr();
        // end of init()
    }
}]);
