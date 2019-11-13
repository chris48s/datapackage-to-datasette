import json
import sqlite3
import tempfile
from unittest import TestCase

import datapackage

from datapackage_to_datasette.utils import (
    DataImportError,
    datapackage_to_datasette,
    get_metadata_object,
)


class GetMetadataObjectTests(TestCase):
    def setUp(self):
        self.database_tmp_file = tempfile.NamedTemporaryFile(suffix=".db")

    def tearDown(self):
        self.database_tmp_file.close()

    def test_minimal_attributes(self):
        dp = datapackage.Package("tests/fixtures/periodic-table/datapackage.json")
        self.assertDictEqual(
            {"databases": {self.database_tmp_file.name: {"title": "Periodic Table"}}},
            get_metadata_object(self.database_tmp_file.name, dp),
        )

    def test_all_attributes(self):
        dp = datapackage.Package("tests/fixtures/contrived-example/datapackage.json")

        expected = {
            "databases": {
                self.database_tmp_file.name: {
                    "source_url": "http://foo.bar/baz",
                    "title": "A datapackage designed to artificially create a range of conditions",
                    "tables": {
                        "units": {
                            "title": "Standard Units",
                            "description": "Standard Units for the Frictionless Data specification",
                            "license": "CC-BY-3.0",
                            "license_url": "https://creativecommons.org/licenses/by/3.0/",
                        },
                        "unit_prefixes": {
                            "license": "CC-BY-4.0",
                            "license_url": "https://creativecommons.org/licenses/by/4.0/",
                        },
                    },
                }
            }
        }

        self.assertDictEqual(
            expected, get_metadata_object(self.database_tmp_file.name, dp)
        )


class DatapackageToDatasetteTests(TestCase):
    def setUp(self):
        self.database_tmp_file = tempfile.NamedTemporaryFile(suffix=".db")
        self.metadata_tmp_file = tempfile.NamedTemporaryFile("r+")

    def tearDown(self):
        self.database_tmp_file.close()
        self.metadata_tmp_file.close()

    def test_dont_replace_existing_metadata(self):
        with self.assertRaises(DataImportError):
            datapackage_to_datasette(
                self.database_tmp_file.name,
                "tests/fixtures/units-and-prefixes/datapackage.json",
                self.metadata_tmp_file.name,
            )

    def test_merge_existing_metadata(self):
        existing_metadata = {
            "title": "Custom title for your index page",
            "description": "Some description text can go here",
            "license": "ODbL",
            "license_url": "https://opendatacommons.org/licenses/odbl/",
            "source": "Original Data Source",
            "source_url": "http://example.com/",
            "databases": {
                "database1": {
                    "tables": {
                        "example_table": {"sortable_columns": ["height", "weight"]}
                    }
                }
            },
        }

        json.dump(existing_metadata, self.metadata_tmp_file, indent=2)
        self.metadata_tmp_file.seek(0)

        datapackage_to_datasette(
            self.database_tmp_file.name,
            "tests/fixtures/units-and-prefixes/datapackage.json",
            self.metadata_tmp_file.name,
            write_mode="merge",
        )

        conn = sqlite3.connect(self.database_tmp_file.name)
        self.assertEqual(174, conn.execute("SELECT COUNT(*) FROM units;").fetchone()[0])
        self.assertEqual(
            20, conn.execute("SELECT COUNT(*) FROM unit_prefixes;").fetchone()[0]
        )

        expected = {
            "title": "Custom title for your index page",
            "description": "Some description text can go here",
            "license": "ODbL",
            "license_url": "https://opendatacommons.org/licenses/odbl/",
            "source": "Original Data Source",
            "source_url": "http://example.com/",
            "databases": {
                "database1": {
                    "tables": {
                        "example_table": {"sortable_columns": ["height", "weight"]}
                    }
                },
                self.database_tmp_file.name: {
                    "title": "Units and Unit Prefixes",
                    "license": "CC-BY-4.0",
                    "license_url": "https://creativecommons.org/licenses/by/4.0/",
                    "tables": {
                        "units": {
                            "title": "Standard Units",
                            "description": "Standard Units for the Frictionless Data specification",
                        },
                        "unit_prefixes": {
                            "title": "Unit Prefixes",
                            "description": "Standard Unit Prefixes for the Frictionless Data specification",
                        },
                    },
                },
            },
        }

        self.assertDictEqual(expected, json.load(self.metadata_tmp_file))

    def test_replace_existing_metadata(self):
        datapackage_to_datasette(
            self.database_tmp_file.name,
            "tests/fixtures/units-and-prefixes/datapackage.json",
            self.metadata_tmp_file.name,
            write_mode="replace",
        )

        conn = sqlite3.connect(self.database_tmp_file.name)
        self.assertEqual(174, conn.execute("SELECT COUNT(*) FROM units;").fetchone()[0])
        self.assertEqual(
            20, conn.execute("SELECT COUNT(*) FROM unit_prefixes;").fetchone()[0]
        )

        expected = {
            "databases": {
                self.database_tmp_file.name: {
                    "title": "Units and Unit Prefixes",
                    "license": "CC-BY-4.0",
                    "license_url": "https://creativecommons.org/licenses/by/4.0/",
                    "tables": {
                        "units": {
                            "title": "Standard Units",
                            "description": "Standard Units for the Frictionless Data specification",
                        },
                        "unit_prefixes": {
                            "title": "Unit Prefixes",
                            "description": "Standard Unit Prefixes for the Frictionless Data specification",
                        },
                    },
                }
            }
        }

        self.assertDictEqual(expected, json.load(self.metadata_tmp_file))
