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

// name, close(), inputs, show_advanced, has_advanced, submit, popup_form
// value
angular.module('popup_form', ['ui.bootstrap'], ['$provide', function(p) {
    p.factory('popupForm', ['$dialog', function(dlg) {
        var template_url =
            ScriptLoader.static_url('popup_form/html/popup_form.html');
        function PopupForm() {
            this._init.apply(this, arguments);
        }

        function get_field(obj, name) {
            var fields = name.split('.');
            for (var i = 0;i < fields.length;i++) {
                if (!obj.hasOwnProperty(fields[i]))
                    return undefined;
                obj = obj[fields[i]];
            }
            return obj;
        }

        function set_field(obj, name, value) {
            var fields = name.split('.');
            for (var i = 0;i < fields.length - 1;i++) {
                if (!obj.hasOwnProperty(fields[i]))
                    obj[fields[i]] = {};
                obj = obj[fields[i]];
            }
            obj[fields[fields.length - 1]] = value;
        }

        PopupForm.prototype = {
            _init: function (name, inputs, value) {
                value = value || {};
                this.name = name;
                this.inputs = inputs;
                this.show_advanced = false;
                this.scope = null;
                this.has_advanced = false;
                this.value = {};
                for (var i in inputs) {
                    if (!inputs.hasOwnProperty(i))
                        continue;
                    var input = inputs[i];
                    if (input.advanced) {
                        this.has_advanced = true;
                    }
                    this.value[input.id] = get_field(value, input.id);
                }
                var that = this;
                this.dialog = dlg.dialog({
                    controller: 'PopupFormCtrl',
                    templateUrl: template_url,
                    resolve: {
                        popupForm: function () {
                            return that;
                        }
                    }
                });
            },
            open: function () {
                return this.dialog.open();
            },
            close: function (res) {
                return this.dialog.close(res);
            },
            submit: function () {
                if (!this.dialog.isOpen() || !this.scope ||
                    !this.scope.popup_form || !this.scope.popup_form.$valid) {
                    return;
                }
                var res = {};
                for (var i in this.inputs) {
                    if (!this.inputs.hasOwnProperty(i))
                        continue;
                    var input = this.inputs[i];
                    set_field(res, input.id, this.value[input.id]);
                }
                return this.close(res);
            },
            _set_scope: function (scope) {
                this.scope = scope;
            }
        };

        return PopupForm;
    }]);
}]).controller('PopupFormCtrl', ['$scope', 'popupForm', function ($s, form) {
    $s.form = form;
    form._set_scope($s);
}]);
