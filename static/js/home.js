becv_app
    .constant("titleBtnConfig", {
        activeClass: "active"
    })
    .directive('titleBtn', ['titleBtnConfig', function (titleBtnConfig) {
        var activeClass = titleBtnConfig.activeClass || 'active';
        return {
            require: 'ngModel',
            link: function ($scope, $ele, $attrs, ngModelCtrl) {
                var name = $scope.$eval($attrs.titleBtn);

                $scope.$watch(function () {
                    return ngModelCtrl.$modelValue;
                }, function (modelValue) {
                    if (angular.equals(modelValue, name)){
                        $ele.addClass(activeClass);
                    } else {
                        $ele.removeClass(activeClass);
                    }
                });

                $ele.bind("click", function () {
                    if (!$ele.hasClass(activeClass)) {
                        $scope.$apply(function () {
                            ngModelCtrl.$setViewValue(name);
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

function HomePageCtrl($scope, $http) {
    var tabs = {
        'oven-temp': true,
        'oven-control': true
    };
    if (window.location.hash)
        $scope.active_tab = window.location.hash.substring(1);
    if (!($scope.active_tab in tabs))
        $scope.active_tab = 'oven-temp';

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
        if (!type)
            type = "";
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

    $http.get('/action/get-ovens/', {
        cache: false,
        timeout: 10000
    }).success(function (data, status) {
        $scope.TControls = data;
    }).error(function (data, status) {
        add_message("Error " + status + ", when getting oven list.", 'error');
    });

    $http.get('/action/get-profiles/', {
        cache: false,
        timeout: 10000
    }).success(function (data, status) {
        $scope.TProfile.set_profiles(data);
    }).error(function (data, status) {
        add_message("Error " + status + ", when getting profile list.",
                    'error');
    });

    $scope.TControls = [];
    $scope.auto_temp = false;

    $scope.TValues = {};

    function update_temps() {
        $http.get('/action/get-temps/', {
            cache: false,
            timeout: 10000,
        }).success(function (data, status) {
            $scope.TValues = data;
        }).error(function (data, status) {
            add_message("Error " + status + ", when getting temperatures.",
                        'error');
        });
    }
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
        _init: function () {
            this.ids = [];
            this.all = {};
            this.cur = '';
            this.status = 0;
        },
        do_apply: function () {
            if (!this.cur)
                return;
            this.status = 1;
            var that = this;
            var cur = this.all[this.cur].name;
            $http.get('/action/set-profile/' + this.cur + '/', {
                cache: false,
                timeout: 10000
            }).success(function (data, status) {
                that.status = 2;
                add_message('Successfully set profile to "' + cur + '".',
                            'success');
            }).error(function (data, status) {
                that.status = 3;
                add_message("Error " + status +
                            ', when setting profile to "' + cur + '".',
                            'error');
            });
        }
    }

    $scope.TProfile = new TempProfileMgr();
}
