odoo.define('show_databasename.ShowDatabaseName', function (require) {
    'use strict';

    var UserMenu = require('web.UserMenu');
    var session = require('web.session');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    // var Model = require('web.Model');
    var Widget = require('web.Widget');
    var BasicModel = require('web.BasicModel');

    // Inherit UserMenu widget by using "include".
    UserMenu.include({

        start: function () {
            var self = this;
            var session = this.getSession();
            this.$el.on('click', 'li a[data-menu]', function (ev) {
                ev.preventDefault();
                var menu = $(this).data('menu');
                self['_onMenu' + menu.charAt(0).toUpperCase() + menu.slice(1)]();
            });
            return this._super.apply(this, arguments).then(function () {
                var $avatar = self.$('.oe_topbar_avatar');
                if (!session.uid) {
                    $avatar.attr('src', $avatar.data('default-src'));
                    return $.when();
                }
                var topbar_name = _.str.sprintf("%s (%s)", session.db, session.name);
                self.$('.oe_topbar_name').text(topbar_name);
                var avatar_src = session.url('/web/image', {
                    model: 'res.users',
                    field: 'image_small',
                    id: session.uid
                });
                $avatar.attr('src', avatar_src);
            });
        }
    });

});
