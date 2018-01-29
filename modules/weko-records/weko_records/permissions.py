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

"""Permissions for item types."""

import pkg_resources
from flask_principal import ActionNeed

action_item_type_access = ActionNeed('item-type-access')
"""Define the action needed by the default permission factory."""


def permission_factory():
    """Default factory for creating a permission for an admin.

    It tries to load a :class:`invenio_access.permissions.DynamicPermission`
    instance if `invenio_access` is installed.
    Otherwise, it loads a :class:`flask_principal.Permission` instance.

    :param admin_view: Instance of administration view which is currently being
        protected.
    :returns: Permission instance.
    """
    try:
        pkg_resources.get_distribution('invenio-access')
        from invenio_access.permissions import DynamicPermission as Permission
    except pkg_resources.DistributionNotFound:
        from flask_principal import Permission

    return Permission(action_item_type_access)
