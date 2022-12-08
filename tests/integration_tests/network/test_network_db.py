"""Test the main :class:`` class."""
import os
from unittest.mock import patch

import pytest

from tests.mock_and_patch.yawning_titan_db_patch import yawning_titan_db_init_patch
from yawning_titan.db.doc_metadata import DocMetadataSchema
from yawning_titan.db.yawning_titan_db import YawningTitanDB
from yawning_titan.exceptions import YawningTitanDBError
from yawning_titan.network.network_db import NetworkDB


@pytest.mark.integration_test
def test_db_file_exists():
    """Test the creation of the network db."""
    with patch.object(YawningTitanDB, "__init__", yawning_titan_db_init_patch):
        db = NetworkDB()
        assert os.path.isfile(db._db._path)
        db._db.close_and_delete_temp_db()


@pytest.mark.integration_test
def test_delete_default_network_delete_fails():
    """Test attempted deletion of locked network fails."""
    with patch.object(YawningTitanDB, "__init__", yawning_titan_db_init_patch):
        db = NetworkDB()
        config = db.search(DocMetadataSchema.LOCKED == True)[0]

        with pytest.raises(YawningTitanDBError):
            db.remove(config)

        db._db.close_and_delete_temp_db()


@pytest.mark.integration_test
def test_reset_default_networks():
    """Test attempted deletion of locked network fails."""
    with patch.object(YawningTitanDB, "__init__", yawning_titan_db_init_patch):
        db = NetworkDB()
        configs = db.all()

        config = configs[0]

        # Update the object locally
        config.entry_nodes = ["1"]

        # Hack an update to the locked network in the db
        db._db.db.update(
            config.to_dict(json_serializable=True),
            DocMetadataSchema.UUID == config.doc_metadata.uuid,
        )

        # Perform the default networks reset
        db.reset_default_networks_in_db()

        expected = [config.to_dict(json_serializable=True) for config in configs]
        actual = [config.to_dict(json_serializable=True) for config in db.all()]
        assert expected == actual

        db._db.close_and_delete_temp_db()
