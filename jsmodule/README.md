# jsmodule app

This app handles script dependency as well as app specific script.

## Description

Django provide a way for apps to ship static files and views, however,
the url of them will depend on the project global setting. For html files,
it is easy to get real url using static file related tags. For javascript files,
however, using django template can easily mess up the script and also make
caching harder. This app solves the problem by provides api's (url's) to get
server url info as well as a client side js module library to manage them.
