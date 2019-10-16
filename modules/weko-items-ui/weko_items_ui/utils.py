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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WEKO3; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.

"""Module of weko-items-ui utils.."""

from elasticsearch.exceptions import NotFoundError
from flask import current_app, session
from flask_babelex import gettext as _
from flask_login import current_user
from invenio_db import db
from invenio_records.api import RecordBase
from invenio_search import RecordsSearch
from jsonschema import ValidationError
from sqlalchemy import MetaData, Table
from weko_records.api import ItemTypes
from weko_search_ui.query import item_search_factory
from weko_user_profiles import UserProfile
from weko_workflow.models import Action as _Action


def get_list_username():
    """Get list username.

    Query database to get all available username
    return: list of username
    """
    current_user_id = current_user.get_id()
    user_index = 1
    result = list()
    while True:
        try:
            if (int(current_user_id) == user_index):
                pass
            else:
                user_info = UserProfile.get_by_userid(user_index)
                result.append(user_info.get_username)
            user_index = user_index + 1
        except Exception:
            break

    return result


def get_list_email():
    """Get list email.

    Query database to get all available email
    return: list of email
    """
    current_user_id = current_user.get_id()
    result = list()
    try:
        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        table_name = 'accounts_user'

        user_table = Table(table_name, metadata)
        record = db.session.query(user_table)

        data = record.all()

        for item in data:
            if (int(current_user_id) == item[0]):
                pass
            else:
                result.append(item[1])
    except Exception as e:
        result = str(e)

    return result


def get_user_info_by_username(username):
    """Get user information by username.

    Query database to get user id by using username
    Get email from database using user id
    Pack response data: user id, user name, email

    parameter:
        username: The username
    return: response pack
    """
    result = dict()
    try:
        user = UserProfile.get_by_username(username)
        user_id = user.user_id

        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        table_name = 'accounts_user'

        user_table = Table(table_name, metadata)
        record = db.session.query(user_table)

        data = record.all()

        for item in data:
            if item[0] == user_id:
                result['username'] = username
                result['user_id'] = user_id
                result['email'] = item[1]
                return result
        return None
    except Exception as e:
        result['error'] = str(e)


def validate_user(username, email):
    """Validate user information.

    Get user id from database using username
    Get user id from database using email
    Compare 2 user id to validate user information
    Pack responde data:
        results: user information (username, user id, email)
        validation: username is match with email or not
        error: null if no error occurs

    param:
        username: The username
        email: The email
    return: response data
    """
    result = {
        'results': '',
        'validation': False,
        'error': ''
    }
    try:
        user = UserProfile.get_by_username(username)
        user_id = 0

        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        table_name = 'accounts_user'

        user_table = Table(table_name, metadata)
        record = db.session.query(user_table)

        data = record.all()

        for item in data:
            if item[1] == email:
                user_id = item[0]
                break

        if user.user_id == user_id:
            user_info = dict()
            user_info['username'] = username
            user_info['user_id'] = user_id
            user_info['email'] = email
            result['results'] = user_info
            result['validation'] = True
        return result
    except Exception as e:
        result['error'] = str(e)

    return result


def get_user_info_by_email(email):
    """
    Get user information by email.

    Query database to get user id by using email
    Get username from database using user id
    Pack response data: user id, user name, email

    parameter:
        email: The email
    return: response
    """
    result = dict()
    try:
        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        table_name = 'accounts_user'

        user_table = Table(table_name, metadata)
        record = db.session.query(user_table)

        data = record.all()
        for item in data:
            if item[1] == email:
                user = UserProfile.get_by_userid(item[0])
                if user is None:
                    result['username'] = ""
                else:
                    result['username'] = user.get_username
                result['user_id'] = item[0]
                result['email'] = email
                return result
        return None
    except Exception as e:
        result['error'] = str(e)


def get_user_information(user_id):
    """
    Get user information user_id.

    Query database to get email by using user_id
    Get username from database using user id
    Pack response data: user id, user name, email

    parameter:
        user_id: The user_id
    return: response
    """
    result = {
        'username': '',
        'email': ''
    }
    user_info = UserProfile.get_by_userid(user_id)
    if user_info is not None:
        result['username'] = user_info.get_username

    metadata = MetaData()
    metadata.reflect(bind=db.engine)
    table_name = 'accounts_user'

    user_table = Table(table_name, metadata)
    record = db.session.query(user_table)

    data = record.all()

    for item in data:
        if item[0] == user_id:
            result['email'] = item[1]
            return result

    return result


def get_user_permission(user_id):
    """
    Get user permission user_id.

    Compare current id with id of current user
    parameter:
        user_id: The user_id
    return: true if current id is the same with id of current user.
    If not return false
    """
    current_id = current_user.get_id()
    if current_id is None:
        return False
    if str(user_id) == current_id:
        return True
    return False


def get_current_user():
    """
    Get user id of user currently login.

    parameter:
    return: current_id
    """
    current_id = current_user.get_id()
    return current_id


def get_actionid(endpoint):
    """
    Get action_id by action_endpoint.

    parameter:
    return: action_id
    """
    with db.session.no_autoflush:
        action = _Action.query.filter_by(
            action_endpoint=endpoint).one_or_none()
        if action:
            return action.id
        else:
            return None


def parse_ranking_results(results, display_rank, list_name='all',
                          title_key='title', count_key=None, pid_key=None,
                          search_key=None, date_key=None):
    """Parse the raw stats results to be usable by the view."""
    ranking_list = []
    if pid_key:
        url = '../records/{0}'
        key = pid_key
    elif search_key:
        url = '../search?page=1&size=20&search_type=1&q={0}'
        key = search_key
    else:
        url = None

    if date_key == 'create_date':
        data_list = parse_ranking_new_items(results)
        results = dict()
        results['all'] = data_list
    if results and list_name in results:
        rank = 1
        count = 0
        date = ''
        for item in results[list_name]:
            t = {}
            if count_key:
                if not count == int(item[count_key]):
                    rank = len(ranking_list) + 1
                    count = int(item[count_key])
                t['rank'] = rank
                t['count'] = count
            elif date_key:
                new_date = item[date_key]
                if new_date == date:
                    t['date'] = ''
                else:
                    t['date'] = new_date
                    date = new_date
            title = item[title_key]
            if title_key == 'user_id':
                user_info = UserProfile.get_by_userid(title)
                if user_info:
                    title = user_info.username
                else:
                    title = 'None'
            t['title'] = title
            t['url'] = url.format(item[key]) if url and key in item else None
            ranking_list.append(t)
            if len(ranking_list) == display_rank:
                break
    return ranking_list


def parse_ranking_new_items(result_data):
    """Parse ranking new items.

    :param result_data: result data
    """
    data_list = list()
    if not result_data or not result_data.get('hits') \
            or not result_data.get('hits').get('hits'):
        return data_list
    for item_data in result_data.get('hits').get('hits'):
        item_created = item_data.get('_source')
        data = dict()
        data['create_date'] = item_created.get('publish_date', '')
        data['pid_value'] = item_created.get('control_number')
        meta_data = item_created.get('_item_metadata')
        item_title = ''
        if isinstance(meta_data, dict):
            item_title = meta_data.get('item_title')
        data['record_name'] = item_title
        data_list.append(data)
    return data_list


def validate_form_input_data(result: dict, item_id: str, data: dict):
    """Validate input data.

    :param result: result dictionary.
    :param item_id: item type identifier.
    :param data: form input data
    """
    item_type = ItemTypes.get_by_id(item_id)
    json_schema = item_type.schema.copy()

    data['$schema'] = json_schema.copy()
    validation_data = RecordBase(data)
    try:
        validation_data.validate()
    except ValidationError as error:
        result["is_valid"] = False
        if 'required' == error.validator:
            result['error'] = _('Please input all required item.')
        elif 'pattern' == error.validator:
            result['error'] = _('Please input the correct data.')
        else:
            result['error'] = _(error.message)


def update_json_schema_by_activity_id(json, activity_id):
    """Update json schema by activity id.

    :param json: The json schema
    :param activity_id: Activity ID
    :return: json schema
    """
    if not session.get('update_json_schema') or not session[
            'update_json_schema'].get(activity_id):
        return None
    error_list = session['update_json_schema'][activity_id]

    if error_list:
        for item in error_list['required']:
            sub_item = item.split('.')
            if len(sub_item) == 1:
                json['required'] = sub_item
            else:
                if json['properties'][sub_item[0]].get('items'):
                    if not json['properties'][sub_item[0]]['items'].get(
                            'required'):
                        json['properties'][sub_item[0]]['items']['required'] \
                            = []
                    json['properties'][sub_item[0]]['items'][
                        'required'].append(sub_item[1])
                else:
                    json['properties'][sub_item[0]]['required'].append(
                        sub_item[1])
        for item in error_list['pattern']:
            sub_item = item.split('.')
            if len(sub_item) == 2:
                creators = json['properties'][sub_item[0]].get('items')
                if not creators:
                    break
                for creator in creators.get('properties'):
                    if creators['properties'][creator].get('items'):
                        givename = creators['properties'][creator]['items']
                        if givename['properties'].get(sub_item[1]):
                            if not givename.get('required'):
                                givename['required'] = []
                            givename['required'].append(sub_item[1])
    return json


def get_new_items_by_date(start_date: str, end_date: str) -> dict:
    """Get ranking new item by date.

    :param start_date:
    :param end_date:
    :return:
    """
    record_search = RecordsSearch(
        index=current_app.config['SEARCH_UI_SEARCH_INDEX'])
    result = dict()

    try:
        search_instance, qs_kwargs = item_search_factory(None, record_search,
                                                         start_date, end_date)
        search_result = search_instance.execute()
        result = search_result.to_dict()
    except NotFoundError as e:
        current_app.logger.debug("Indexes do not exist yet: ", str(e))

    return result
