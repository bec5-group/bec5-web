becv_app.controller('CtrlEditCtrl', ['$scope', 'value', 'dialog', function ($scope, value, dialog) {
    $scope.value = value;
    $scope.show_advanced = false;
    $scope.submit = function (res) {
        var val = $scope.value;
        if (!val.name || !val.addr)
            return;
        dialog.close(res);
    }
}]);
