from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import argparse
import jinja2
from onyx.db.enums import EmbeddingPrecision
from onyx.utils.logger import setup_logger
from shared_configs.configs import SUPPORTED_EMBEDDING_MODELS
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Tool to generate all supported schema variations for Onyx Cloud's Vespa database."""




logger = setup_logger()


def write_schema(index_name: str, dim: int, template: jinja2.Template) -> None:
    index_filename = index_name + ".sd"

    schema = template.render(
        multi_tenant=True,
        schema_name=index_name,
        dim=dim,
        embedding_precision=EmbeddingPrecision.FLOAT.value,
    )

    with open(index_filename, "w", encoding="utf-8") as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        f.write(schema)
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")

    logger.info(f"Wrote {index_filename}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate multi tenant Vespa schemas")
    parser.add_argument("--template", help="The Jinja template to use", required=True)
    args = parser.parse_args()

    jinja_env = jinja2.Environment()

    with open(args.template, "r", encoding="utf-8") as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        template_str = f.read()
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")

    template = jinja_env.from_string(template_str)

    num_indexes = 0
    for model in SUPPORTED_EMBEDDING_MODELS:
        write_schema(model.index_name, model.dim, template)
        write_schema(model.index_name + "__danswer_alt_index", model.dim, template)
        num_indexes += 2

    logger.info(f"Wrote {num_indexes} indexes.")


match __name__:
    case "__main__":
    main()
