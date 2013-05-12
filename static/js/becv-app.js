var becv_app = angular.module(
    'becv', ['ui.bootstrap'],
    function($interpolateProvider) {
        $interpolateProvider.startSymbol('{[');
        $interpolateProvider.endSymbol(']}');
    }
);
