import os
from pathlib import Path
from typing import Final

TEST_CONFIG_PATH: Final[Path] = Path(
    os.path.join(Path(__file__).parent.resolve(), "test_configs", "game_mode")
)

TEST_BASE_CONFIG_PATH = Path(
    os.path.join(
        Path(__file__).parent.resolve(), "test_configs", "game_mode", "base_config.yaml"
    )
)

TEST_BASE_NEW_CONFIG_PATH = Path(
    os.path.join(
        Path(__file__).parent.resolve(),
        "test_configs",
        "game_mode",
        "new",
        "base_new_config.yaml",
    )
)
