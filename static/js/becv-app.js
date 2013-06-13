var becv_app = angular.module(
    'becv', ['ui.bootstrap', 'ui-gravatar', 'md5'],
    ['$interpolateProvider', '$dialogProvider', function($interpolateProvider, $dialogProvider) {
        $interpolateProvider.startSymbol('{[');
        $interpolateProvider.endSymbol(']}');
        $dialogProvider.options({
            backdropFade: true,
            dialogFade: true
        });
    }]
);
