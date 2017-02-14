#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#
# Copyright (C) 2015 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#   Alvaro del Castillo San Felix <acs@bitergia.com>
#

import json
import logging

from dateutil import parser

from .enrich import Enrich, metadata

class ConfluenceEnrich(Enrich):

    def get_field_author(self):
        return 'by'

    def get_elastic_mappings(self):

        mapping = """
        {
            "properties": {
                "title_analyzed": {
                  "type": "string",
                  "index":"analyzed"
                  }
           }
        } """

        return {"items":mapping}

    def get_identities(self, item):
        """ Return the identities from an item """
        identities = []

        field = self.get_field_author()
        identities.append(self.get_sh_identity(item, field))

        return identities

    def get_users_data(self, item):
        """ If user fields are inside the global item dict """
        if 'data' in item:
            users_data = item['data']['version']
        else:
            # the item is directly the data (kitsune answer)
            users_data = item
        return users_data

    def get_sh_identity(self, item, identity_field=None):
        identity = {}

        user = item  # by default a specific user dict is expected
        if 'data' in item and type(item) == dict:
            user = item['data']['version'][identity_field]

        identity['username'] = None
        identity['email'] = None
        identity['name'] = None
        if 'username' in user:
            identity['username'] = user['username']
        if 'displayName' in user:
            identity['name'] = user['displayName']

        return identity

    @metadata
    def get_rich_item(self, item):
        eitem = {}

        for f in self.RAW_FIELDS_COPY:
            if f in item:
                eitem[f] = item[f]
            else:
                eitem[f] = None
        # The real data
        page = item['data']

        # data fields to copy
        copy_fields = ["type", "id", "status", "title"]
        for f in copy_fields:
            if f in page:
                eitem[f] = page[f]
            else:
                eitem[f] = None
        # Fields which names are translated
        map_fields = {"title": "title_analyzed"}
        for fn in map_fields:
            eitem[map_fields[fn]] = page[fn]

        version = page['version']

        if 'username' in version['by']:
            eitem['author_name'] = version['by']['username']
        else:
            eitem['author_name'] = version['by']['displayName']

        eitem['message'] = None
        if 'message' in version:
            eitem['message'] = version['message']
        eitem['version'] = version['number']
        eitem['date'] = version['when']
        eitem['url'] =  page['_links']['base'] + page['_links']['webui']

        # Specific enrichment
        if page['type'] == 'page':
            if page['version']['number'] == 1:
                eitem['type'] = 'new_page'
        eitem['is_'+eitem['type']] = 1

        if self.sortinghat:
            eitem.update(self.get_item_sh(item))

        return eitem