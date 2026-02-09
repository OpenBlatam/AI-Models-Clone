from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
UNSUPPORTED_FILE_TYPE_CONTENT = ""  # keep empty for now
DRIVE_FOLDER_TYPE = "application/vnd.google-apps.folder"
DRIVE_SHORTCUT_TYPE = "application/vnd.google-apps.shortcut"
DRIVE_FILE_TYPE = "application/vnd.google-apps.file"
