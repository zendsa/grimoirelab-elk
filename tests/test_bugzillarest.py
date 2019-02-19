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
#     Alvaro del Castillo <acs@bitergia.com>
#     Valerio Cosentino <valcos@bitergia.com>
#

import json
import logging
import unittest

from base import TestBaseBackend
from grimoire_elk.raw.bugzillarest import BugzillaRESTOcean

from grimoire_elk.enriched.bugzillarest import BugzillaRESTEnrich


class TestBugzillaRest(TestBaseBackend):
    """Test BugzillaRest backend"""

    connector = "bugzillarest"
    ocean_index = "test_" + connector
    enrich_index = "test_" + connector + "_enrich"

    def test_has_identites(self):
        """Test value of has_identities method"""

        enrich_backend = self.connectors[self.connector][2]()
        self.assertTrue(enrich_backend.has_identities())

    def test_items_to_raw(self):
        """Test whether JSON items are properly inserted into ES"""

        result = self._test_items_to_raw()
        self.assertEqual(result['items'], 7)
        self.assertEqual(result['raw'], 7)

    def test_raw_to_enrich(self):
        """Test whether the raw index is properly enriched"""

        result = self._test_raw_to_enrich()
        self.assertEqual(result['raw'], 7)
        self.assertEqual(result['enrich'], 7)

    def test_raw_to_enrich_sorting_hat(self):
        """Test enrich with SortingHat"""

        result = self._test_raw_to_enrich(sortinghat=True)
        self.assertEqual(result['raw'], 7)
        self.assertEqual(result['enrich'], 7)

    def test_raw_to_enrich_projects(self):
        """Test enrich with Projects"""

        result = self._test_raw_to_enrich(projects=True)
        self.assertEqual(result['raw'], 7)
        self.assertEqual(result['enrich'], 7)

    def test_refresh_identities(self):
        """Test refresh identities"""

        result = self._test_refresh_identities()
        # ... ?

    def test_refresh_project(self):
        """Test refresh project field for all sources"""

        result = self._test_refresh_project()
        # ... ?

    def test_get_project(self):
        """ Test the project mapping """

        # Test Mozilla projects mapping that it a bit tricky
        # The component and product fields used for the mapping
        # must contain both with " " converted to "+"
        rawitems = open("data/bugzillarest-item-bulgarian.json").read()
        rawitem = json.loads(rawitems)['hits']['hits'][0]["_source"]

        # Create the enricher
        enricher = BugzillaRESTEnrich(json_projects_map="data/bugzillarest-projects.json")
        # Enrich the item
        eitem = enricher.get_rich_item(rawitem)
        # Check the project
        self.assertEqual(eitem['project'], "Localization")

    def test_arthur_params(self):
        """Test the extraction of arthur params from an URL"""

        with open("data/projects-release.json") as projects_filename:
            url = json.load(projects_filename)['grimoire']['bugzillarest'][0]
            arthur_params = {'uri': 'https://bugzilla.mozilla.org', 'url': 'https://bugzilla.mozilla.org'}
            self.assertDictEqual(arthur_params, BugzillaRESTOcean.get_arthur_params_from_url(url))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    unittest.main(warnings='ignore')
