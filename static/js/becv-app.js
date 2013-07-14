var becv_app = angular.module(
    'becv', ['ui.bootstrap', 'ui-gravatar', 'md5', 'logging', 'request',
             'room_temp', 'log_mgr', 'popup_form'],
    ['$interpolateProvider', '$dialogProvider', function(interpolate, dlg) {
        interpolate.startSymbol('{[');
        interpolate.endSymbol(']}');
        dlg.options({
            backdropFade: true,
            dialogFade: true
        });
    }]
);
