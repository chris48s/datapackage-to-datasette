import json
import logging
from os import path

import datapackage
from datapackage.package import _slugify_resource_name
from deepmerge import always_merger
from sqlalchemy import create_engine

logging.basicConfig(format="%(levelname)s: %(message)s")


class DataImportError(Exception):
    pass


def datapackage_descriptor_to_metadata_object(descriptor):
    obj = {}
    if descriptor.get("title", None):
        obj["title"] = descriptor["title"]
    if descriptor.get("description", None):
        obj["description"] = descriptor["description"]
    if descriptor.get("licenses", []):
        if descriptor["licenses"][0].get("name", None):
            obj["license"] = descriptor["licenses"][0]["name"]
        if descriptor["licenses"][0].get("path", None):
            obj["license_url"] = descriptor["licenses"][0]["path"]
        num_licenses = len(descriptor["licenses"])
        if num_licenses > 1:
            logging.warning(
                f"{num_licenses} licenses found, but datasette metadata only "
                "allows one license to be specified. Only the first will be used."
            )
    if descriptor.get("homepage", None):
        obj["source_url"] = descriptor["homepage"]
    return obj


def get_metadata_object(dbname, dp):
    metadata = {
        "databases": {dbname: datapackage_descriptor_to_metadata_object(dp.descriptor)}
    }

    metadata["databases"][dbname]["tables"] = {}
    for resource in dp.resources:
        if resource.tabular:
            md = datapackage_descriptor_to_metadata_object(resource.descriptor)
            if md:
                table_name = _slugify_resource_name(resource.name)
                metadata["databases"][dbname]["tables"][table_name] = md
    if not metadata["databases"][dbname]["tables"]:
        del metadata["databases"][dbname]["tables"]

    return metadata


def validate_write_mode(write_mode):
    allowed_values = (None, "replace", "merge")
    if write_mode not in allowed_values:
        raise ValueError(f"write_mode must be one of {str(allowed_values)}")


def write_file(metadata, filename, write_mode):
    if not path.exists(filename):
        with open(filename, "w") as _:
            pass

    with open(filename, "r+") as f:
        if write_mode == "merge":
            existing = json.load(f)
            f.seek(0)
        else:
            existing = {}
        json.dump(always_merger.merge(existing, metadata), f, indent=2)


def datapackage_to_datasette(dbname, data_package, metadata_filename, write_mode=None):
    validate_write_mode(write_mode)

    if path.exists(metadata_filename) and not write_mode:
        raise DataImportError(
            f"File {metadata_filename} already exists. "
            "Use write_mode to replace or merge the existing file."
        )

    dp = datapackage.Package(data_package)
    engine = create_engine(f"sqlite:///{dbname}")
    dp.save(storage="sql", engine=engine)

    metadata = get_metadata_object(dbname, dp)

    write_file(metadata, metadata_filename, write_mode)
