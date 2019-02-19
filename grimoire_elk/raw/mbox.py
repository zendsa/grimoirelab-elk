# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2019 Bitergia
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

import logging

from .elastic import ElasticOcean
from ..elastic_mapping import Mapping as BaseMapping


logger = logging.getLogger(__name__)


class Mapping(BaseMapping):

    @staticmethod
    def get_elastic_mappings(es_major):
        """Get Elasticsearch mapping.

        Non dynamic discovery of type for:
            * data.body (inmense field)

        :param es_major: major version of Elasticsearch, as string
        :returns:        dictionary with a key, 'items', with the mapping
        """

        mapping = '''
         {
            "dynamic":true,
                "properties": {
                    "data": {
                        "properties": {
                            "body": {
                                "dynamic":false,
                                "properties": {}
                            }
                        }
                    }
                }
        }
        '''

        return {"items": mapping}


class MBoxOcean(ElasticOcean):
    """MBox Ocean feeder"""

    mapping = Mapping

    @classmethod
    def get_perceval_params_from_url(cls, url):
        # In the url the uri and the data dir are included
        params = url.split()

        return params

    @classmethod
    def get_arthur_params_from_url(cls, url):
        # In the url the dirpath and the repository are included

        params = url.split()
        """ Get the arthur params given a URL for the data source """
        params = {"dirpath": params[1], "uri": params[0]}

        return params

    def _fix_item(self, item):
        # Remove all custom fields to avoid the 1000 fields limit in ES

        fields = list(item["data"].keys())
        for field in fields:
            if field.lower().startswith("x-"):
                item["data"].pop(field)
