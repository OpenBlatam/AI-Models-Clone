"""
Data processing utilities
"""

from utils.categories import register_utility

try:
    from utils.data_utils import DataUtils
    from utils.data_pipeline import DataPipeline
    from utils.data_augmentation import DataAugmentation
    from utils.collection_helpers import CollectionHelpers
    from utils.aggregators import Aggregators
    from utils.filters import Filters
    from utils.sorters import Sorters
    from utils.comparators import Comparators
    
    def register_utilities():
        register_utility("data", "data_utils", DataUtils)
        register_utility("data", "pipeline", DataPipeline)
        register_utility("data", "augmentation", DataAugmentation)
        register_utility("data", "collection", CollectionHelpers)
        register_utility("data", "aggregators", Aggregators)
        register_utility("data", "filters", Filters)
        register_utility("data", "sorters", Sorters)
        register_utility("data", "comparators", Comparators)
except ImportError:
    pass



