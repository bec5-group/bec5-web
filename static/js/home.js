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

function HomePageCtrl($scope, $http) {
    var tabs = {
        'oven-temp': true,
        'oven-control': true
    };
    if (window.location.hash)
        $scope.active_tab = window.location.hash.substring(1);
    if (!($scope.active_tab in tabs))
        $scope.active_tab = 'oven-temp';

    $http.get('/action/get-ovens/').success(function (data, status) {
        $scope.TControls = data;
    }).error(function (data, status) {
        // TODO
    });

    $http.get('/action/get-profiles/').success(function (data, status) {
        $scope.TProfile.set_profiles(data);
    }).error(function (data, status) {
        // TODO
    });

    $scope.TControls = [];
    $scope.auto_temp = false;

    $scope.TValues = {};

    function update_temps() {
        $http.get('/action/get-temps/').success(function (data, status) {
            $scope.TValues = data;
        }).error(function (data, status) {
            // TODO
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
            this.busy = false;
        },
        do_apply: function () {
            if (!this.cur)
                return;
            this.busy = true;
            var that = this;
            $http.get('/action/set-profile/' + this.cur + '/')
                .success(function (data, status) {
                    that.busy = false;
                    // TODO
                    console.log("apply", data ? 'success' : 'failed');
                }).error(function (data, status) {
                    that.busy = false;
                    // TODO
                });
        }
    }

    $scope.TProfile = new TempProfileMgr();
}
