# -*- coding: utf-8 -*-
#
# This file is part of WEKO3.
# Copyright (C) 2017 National Institute of Informatics.
#
# WEKO3 is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# WEKO3 is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WEKO3; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.


"""Extensions for weko-groups."""

from .views import blueprint


class WekoGroups(object):
    """Weko-Groups extension."""

    def __init__(self, app=None):
        """
        Extension initialization.

        :param app: The flask application, default None.
        """
        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Flask application initialization.

        :param app: The flask application.
        """
        self.init_config(app)
        app.register_blueprint(blueprint)
        app.extensions['weko-groups'] = self

    def init_config(self, app):
        """
        Initialize configuration.

        :param app: The flask application.
        """
        app.config.setdefault(
            "GROUPS_BASE_TEMPLATE",
            app.config.get("SETTINGS_TEMPLATE",
                           "weko_groups/base.html"))
