/**
 *   Copyright (C) 2013~2013 by Yichao Yu
 *   yyc1992@gmail.com
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 **/
var ScriptUtils = (function () {
    var to_string = ({}).toString;
    var has_own_property = ({}).hasOwnProperty;
    var doc = document;
    var head = doc.head;
    var Utils = {
        for_each: function (obj, cb, that) {
            if (that)
                cb = Utils.bind(that, cb);
            for (var i in obj) {
                if (!has_own_property.call(obj, i))
                    continue;
                cb(i, obj[i]);
            }
        },
        bind: function (that, cb) {
            return function () {
                return cb.apply(that, arguments);
            };
        },
        get_type: function (v) {
            return to_string.call(v).slice(8, -1);
        },
        is_string: function (s) {
            return Utils.get_type(s) == "String";
        },
        merge_obj: function (orig, obj) {
            orig = orig || {};
            Utils.for_each(obj, function (i, value) {
                orig[i] = value;
            });
            return orig;
        },
        def_class: function (parent, proto) {
            return Utils.merge_obj(Object.create(parent.prototype), proto);
        },
        create_ele: function (name, attrs) {
            var ele = doc.createElement(name);
            if (attrs) {
                Utils.merge_obj(ele, attrs);
            }
            return ele;
        },
        prepend_head: function (ele) {
            head.insertBefore(ele, head.firstChild);
        },
        prepare_script: function (url) {
            // This is the simplest hack I have found to let the browser
            // preload js files without executing them.
            // The <img> tags cause chromium to complain about wrong mime-type
            // but it looks working otherwise.
            Utils.prepend_head(Utils.create_ele('img', {src: url}));
        },
        load_script: function (url, fn) {
            // Borrowed from $script.get
            var loaded = false;
            function cb() {
                if (loaded)
                    return;
                if ((ele.readyState && !(/^c|loade/.test(ele.readyState))))
                    return;
                ele.onload = ele.onreadystatechange = null;
                loaded = true;
                if (fn) {
                    fn();
                }
            }
            var ele = Utils.create_ele('script', {
                onload: cb,
                onerror: cb,
                onreadystatechange: cb,
                async: 1,
                src: url
            });
            Utils.prepend_head(ele);
        }
    };
    return Utils;
})();

var ScriptLoader = (function () {
    var Utils = ScriptUtils;
    function Script() {
        this._init.apply(this, arguments);
    }
    Script.prototype = {
        _init: function (info) {
            this.loaded = false;
            this.loading = false;
            this._update(info);
            this.__prepared = false;
        },
        _update: function (info) {
            if (Utils.is_string(info)) {
                this.url = info;
                return;
            }
            Utils.for_each(info, function (i, value) {
                this[i] = value;
            }, this);
        },
        prepare: function () {
            if (this.__prepared || this.no_cache)
                return;
            Utils.prepare_script(this.url);
            this.__prepared = true;
        },
        load: function (cb) {
            if (this.loaded || this.loading)
                return;
            this.loading = true;
            Utils.load_script(this.url, Utils.bind(this, function () {
                this.loaded = true;
                this.loading = false;
                if (cb) {
                    cb();
                }
            }));
        }
    };

    function ScriptManager() {
        this._init.apply(this, arguments);
    }
    ScriptManager.prototype = {
        _init: function () {
            this.__scripts_info = {};
            this.__deps_pending = {};
            this.__checking = {};
            this.__hooks = {};
            this.__context = {};
        },
        set_contexts: function (ctx) {
            Utils.for_each(ctx, function (name, value) {
                this.set_context(name, value);
            }, this);
        },
        set_context: function (name, value) {
            this.__context[name] = value;
        },
        get_context: function (name) {
            return this.__context[name];
        },
        _set_static_prefix: function (prefix) {
            if (prefix.substr(-1) == '/')
                prefix = prefix.slice(0, -1);
            this.__static_prefix = prefix;
        },
        static_url: function (url) {
            return this.__static_prefix + '/' + url;
        },
        get_info: function (name) {
            if (this.__scripts_info.hasOwnProperty(name)) {
                return this.__scripts_info[name];
            }
        },
        add_pending: function (name) {
            this.__deps_pending[name] = name;
        },
        del_pending: function (name) {
            delete this.__deps_pending[name];
        },
        __check_finished: function (name) {
            var info = this.get_info(name);
            if (!info || !info.loaded)
                return false;
            try {
                Utils.for_each(info.sync_deps, function (i, dep_name) {
                    if (!this.__check_finished(dep_name)) {
                        throw dep_name;
                    }
                }, this);
                Utils.for_each(info.deps, function (i, dep_name) {
                    if (!this.__check_finished(dep_name)) {
                        throw dep_name;
                    }
                }, this);
            } catch (e) {
                return false;
            }
            return true;
        },
        __check_hooks: function () {
            Utils.for_each(this.__hooks, function (name, hooks) {
                if (this.__check_finished(name)) {
                    Utils.for_each(hooks, function (i, hook) {
                        try {
                            hook(name);
                        } catch (e) {
                            console.error(e);
                        }
                    });
                    delete this.__hooks[name];
                }
            }, this);
        },
        __try_load: function (name) {
            var info = this.get_info(name);
            if (!info) {
                this.add_pending(name);
                return -1;
            }
            if (info.loaded)
                return 1;
            if (info.loading)
                return 0;
            // Dependency loop
            if (this.__checking.hasOwnProperty(name))
                return 1;
            info.prepare();
            try {
                this.__checking[name] = name;
                Utils.for_each(info.deps, function (i, dep_name) {
                    this.__try_load(dep_name);
                }, this);
                var sync_deps_loaded = true;
                var sync_deps_found = true;
                Utils.for_each(info.sync_deps, function (i, dep_name) {
                    switch (this.__try_load(dep_name)) {
                    case -1:
                        sync_deps_found = false;
                        return;
                    case 0:
                        sync_deps_loaded = false;
                        return;
                    }
                }, this);
                if (!sync_deps_found)
                    throw name;
                if (sync_deps_loaded) {
                    info.load(Utils.bind(this, function () {
                        this.__check_deps();
                        this.__check_hooks();
                    }));
                    this.del_pending(name);
                } else {
                    this.add_pending(name);
                }
            } catch (e) {
                return -1;
            } finally {
                delete this.__checking[name];
            }
            return 0;
        },
        __check_deps: function () {
            Utils.for_each(this.__deps_pending, function (name) {
                this.__try_load(name);
            }, this);
        },
        register: function (infos) {
            Utils.for_each(infos, function (name, info) {
                if (this.get_info(name))
                    throw 'Script "' + name + '" already registerred.';
                this.__scripts_info[name] = new Script(info);
            }, this);
            this.__check_deps();
        },
        load: function (names) {
            if (Utils.is_string(names))
                names = [names];
            var _names = {};
            Utils.for_each(names, function (i, name) {
                this.__try_load(name);
                _names[name] = name;
            }, this);
            return {
                then: Utils.bind(this, function (cb) {
                    Utils.for_each(_names, function (name) {
                        var hook = this.__hooks[name] || [];
                        hook.push(cb);
                        this.__hooks[name] = hook;
                    }, this);
                    this.__check_hooks();
                }),
            };
        },
    };

    return new ScriptManager();
})();
