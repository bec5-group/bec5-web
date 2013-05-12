becv_app
    .directive('redirectCnt', function () {
        return {
            link: function ($scope, $ele, $attrs) {
                var url = $attrs.titleBtn;
                var timeout = parseInt($attrs.timeout);
                if (!url)
                    url = "/";
                if (url.search('#') < 0)
                    url += location.hash;
                if (!timeout || timeout <= 0)
                    timeout = 5;

                function check_timeout() {
                    $ele.text(timeout);
                    if (timeout) {
                        timeout--;
                    } else {
                        clearInterval(interval_id);
                        window.location = url;
                    }
                }

                check_timeout();
                var interval_id = setInterval(check_timeout, 1000);
            }
        };
    })
    .directive('hrefHash', function () {
        return {
            link: function ($scope, $ele, $attrs) {
                var attr = $attrs.hrefHash;
                if (!attr)
                    attr = "href";
                var url = $attrs[attr];
                if (!url)
                    url = "";
                url += location.hash;
                $ele.attr(attr, url);
            }
        };
    });
