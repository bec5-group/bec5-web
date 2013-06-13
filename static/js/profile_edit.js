becv_app.controller('ProfileEditCtrl', ['$scope', 'value', 'dialog', function ($scope, value, dialog) {
    $scope.value = value;
    $scope.show_advanced = false;
    $scope.close = function () {
        return dialog.close();
    };
    $scope.submit = function (res) {
        var val = $scope.value;
        if (!val.name)
            return;
        dialog.close(res);
    };
}]);
