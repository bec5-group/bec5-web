becv_app
    .constant("titleBtnConfig", {
        activeClass: "active"
    })
    .directive('titleBtn', ['titleBtnConfig', '$parse', function (titleBtnConfig,
                                                                  $parse) {
        var activeClass = titleBtnConfig.activeClass || 'active';
        return {
            link: function ($scope, $ele, $attrs) {
                var name = $scope.$eval($attrs.titleBtn);
                var model_name = $attrs.titleBtnModel;
                var on_click = $scope.$eval($attrs.titleBtnClicked);

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

becv_app.controller('HomePageCtrl', ['$scope', '$http', '$dialog', function ($scope, $http, $dialog) {
    $scope.init = function (permissions, user) {
        $scope.user = user;
        $scope.redirect_to_login = function (name) {
            window.location = '/accounts/login/?next=/#' + name
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
            active: 'oven-temp'
        }
        if (window.location.hash) {
            var hash_tab = window.location.hash.substring(1);
            var all_tabs = $scope.home_tabs.all;
            for (var i in all_tabs) {
                if (all_tabs[i].id == hash_tab) {
                    if (!$scope.permissions[hash_tab]) {
                        $scope.redirect_to_login(hash_tab);
                    } else {
                        $scope.home_tabs.active = hash_tab;
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
            if ($scope.messages.length >= 5) {
                $scope.messages.length = 4;
            }
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
            return false;
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
            json_request('/action/get-ovens/', function (data, status) {
                $scope.TControls = data;
            }, "Get ovens list");
        }

        function get_profiles() {
            json_request('/action/get-profiles/', function (data, status) {
                $scope.TProfile.set_profiles(data);
            }, "Get profile list");
        }

        function update_temps() {
            json_request('/action/get-temps/', function (data, status) {
                $scope.TValues = data;
            }, "Get temperatures");
        }
        get_ovens();
        get_profiles();
        update_temps();

        setInterval(function () {
            if ($scope.auto_temp) {
                update_temps();
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
                json_request('/action/get-setpoint/', function (data, status) {
                    that.cur_setpoint = data;
                    if (!that.cur_changed || !that.cur) {
                        that.cur = data.id;
                    }
                }, "Get current set point.");
            },
            _init: function () {
                this.ids = [];
                this.all = {};
                this.cur = '';
                this.status = 0;
                this.cur_setpoint = {};
                this.cur_changed = false;
                this.update_cur_setpoint();
            },
            do_apply: function () {
                if (!this.all[this.cur])
                    return;
                this.status = 1;
                var that = this;
                var cur = this.all[this.cur].name;
                this.cur_changed = false;
                var url = '/action/set-profile/' + this.cur + '/'
                json_request(url, function (data, status) {
                    that.status = 2;
                    add_message('Successfully set profile to "' +
                                cur + '".', 'success');
                    that.update_cur_setpoint();
                }, 'Set profile to "' + cur + '"', function (data, status) {
                    that.status = 3;
                });
            }
        }

        $scope.TProfile = new TempProfileMgr();
        $scope.log_collapsed = false;

        $scope.editingOvenTemps = false;
        $scope.editOvenTemps = function () {
            $scope.editingOvenTemps = !$scope.editingOvenTemps;
        }

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
            var url = '/action/get-ctrl-setting/' + id + '/'
            json_request(url, function (data, status) {
                showControllerDialog(data, function (res) {
                    if (!res)
                        return;
                    var url = ('/action/set-controller/' + id + '/?' +
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
                var url = '/action/add-controller/?' + $.param(res);
                json_request(url, function (data, status) {
                    add_message('Successfully added controller "' +
                                data.name + '".', 'success');
                    get_ovens();
                    update_temps();
                }, 'Add Controller');
            });
        }

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
                var url = ('/action/del-controller/' + ctrl.id + '/');
                json_request(url, function (data, status) {
                    add_message('Successfully deleted controller "' +
                                ctrl.name + '".', 'success');
                    get_ovens();
                    update_temps();
                }, 'Delete controller');
            });
        }
    }
}]);
