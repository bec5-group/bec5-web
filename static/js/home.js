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

function HomePageCtrl($scope) {
    $scope.active_tab = 'oven-temp';
    if (window.location.hash)
        $scope.active_tab = window.location.hash.substring(1);

    $scope.TControls = [{
        id: 'bottom',
        name: 'Bottom'
    }, {
        id: 'middle',
        name: 'Middle'
    }, {
        id: 'out',
        name: 'Out'
    }];

    $scope.TValues = {
        out: 500,
        middle: 480,
        bottom: 460
    };

    function TempProfileMgr() {
        this._init.apply(this, arguments);
    }

    TempProfileMgr.prototype = {
        _init: function () {
            this.ids = ['off', 'stand_by', 'on'];
            this.all = {
                off: {
                    name: 'Off',
                    temps: {
                        out: 240,
                        middle: 220,
                        bottom: 200
                    }
                },
                stand_by: {
                    name: 'Stand By',
                    temps: {
                        out: 525,
                        middle: 480,
                        bottom: 460
                    }
                },
                on: {
                    name: 'On',
                    temps: {
                        out: 525,
                        middle: 500,
                        bottom: 480
                    }
                }
            };
            this.cur = '';
            this.busy = false;
        },
        do_apply: function () {
            if (!this.cur)
                return;
            this.busy = !this.busy;
            console.log("Apply", this.cur);
        }
    }

    $scope.TProfile = new TempProfileMgr();
}
