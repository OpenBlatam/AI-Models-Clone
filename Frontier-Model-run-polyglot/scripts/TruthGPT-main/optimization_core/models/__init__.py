
try:
    from ..modules.models import *
    from ..modules.models import (
        create_model,
        ModelManager,
        ModelBuilder
    )
except (ImportError, ValueError):
    from modules.models import *
    from modules.models import (
        create_model,
        ModelManager,
        ModelBuilder
    )
