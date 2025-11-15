#!/usr/bin/env python3
"""
Documentation Generation Script for LexiGlow.

This script generates API documentation in both HTML and Markdown formats
using pdoc3 for the app/ and tests/ modules.

Usage:
    python scripts/generate_docs.py [--html-dir PATH] [--markdown-dir PATH] [--clean]

Options:
    --html-dir PATH      Directory for HTML documentation output (default: docs/html/)
    --markdown-dir PATH  Directory for Markdown documentation output (default: docs/markdown/)
    --clean              Clean output directories before generating documentation
"""

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent

# Default configuration
DEFAULT_HTML_DIR = BASE_DIR / "docs" / "html"
DEFAULT_MARKDOWN_DIR = BASE_DIR / "docs" / "markdown"
MODULES_TO_DOCUMENT = ["app", "tests"]


def clean_directory(directory: Path) -> None:
    """
    Remove all contents of a directory if it exists.

    Args:
        directory: Path to the directory to clean
    """
    if directory.exists():
        logger.info(f"Cleaning directory: {directory}")
        shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)


def generate_html_documentation(
    modules: list[str], output_dir: Path, clean: bool = False
) -> None:
    """
    Generate HTML documentation using pdoc3.

    Args:
        modules: List of module names to document
        output_dir: Directory where HTML documentation will be generated
        clean: Whether to clean the output directory before generating
    """
    if clean:
        clean_directory(output_dir)
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generating HTML documentation to: {output_dir}")

    try:
        # Generate HTML documentation for all modules using pdoc CLI
        module_list = " ".join(modules)
        logger.info(f"Documenting modules: {module_list}")

        # Use pdoc CLI to generate HTML documentation
        # Change to base directory to ensure module imports work correctly
        # --skip-errors allows documentation generation even if some modules fail to import
        cmd = [
            sys.executable,
            "-m",
            "pdoc",
            "--html",
            "--output-dir",
            str(output_dir),
            "--skip-errors",
        ] + modules

        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            check=True,
        )

        if result.stdout:
            logger.debug(result.stdout)
        if result.stderr:
            logger.debug(result.stderr)

        logger.info(f"✅ HTML documentation generated successfully in {output_dir}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating HTML documentation: {e}")
        if e.stdout:
            logger.error(f"stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"stderr: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Error generating HTML documentation: {e}")
        raise


def generate_markdown_documentation(
    modules: list[str], output_dir: Path, clean: bool = False
) -> None:
    """
    Generate Markdown documentation using pdoc3.

    Args:
        modules: List of module names to document
        output_dir: Directory where Markdown documentation will be generated
        clean: Whether to clean the output directory before generating
    """
    if clean:
        clean_directory(output_dir)
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generating Markdown documentation to: {output_dir}")

    try:
        # Generate Markdown documentation for all modules using pdoc CLI
        module_list = " ".join(modules)
        logger.info(f"Documenting modules: {module_list}")

        # Use pdoc CLI to generate Markdown documentation
        # Change to base directory to ensure module imports work correctly
        # --skip-errors allows documentation generation even if some modules fail to import
        cmd = [
            sys.executable,
            "-m",
            "pdoc",
            "--output-dir",
            str(output_dir),
            "--skip-errors",
        ] + modules

        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            check=True,
        )

        if result.stdout:
            logger.debug(result.stdout)
        if result.stderr:
            logger.debug(result.stderr)

        logger.info(f"✅ Markdown documentation generated successfully in {output_dir}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating Markdown documentation: {e}")
        if e.stdout:
            logger.error(f"stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"stderr: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Error generating Markdown documentation: {e}")
        raise


def main() -> None:
    """Main function to generate documentation."""
    parser = argparse.ArgumentParser(
        description="Generate API documentation for LexiGlow using pdoc3"
    )
    parser.add_argument(
        "--html-dir",
        type=str,
        default=str(DEFAULT_HTML_DIR),
        help=f"Directory for HTML documentation output (default: {DEFAULT_HTML_DIR})",
    )
    parser.add_argument(
        "--markdown-dir",
        type=str,
        default=str(DEFAULT_MARKDOWN_DIR),
        help=f"Directory for Markdown documentation output (default: {DEFAULT_MARKDOWN_DIR})",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean output directories before generating documentation",
    )

    args = parser.parse_args()

    html_dir = Path(args.html_dir).resolve()
    markdown_dir = Path(args.markdown_dir).resolve()

    logger.info("Starting documentation generation...")
    logger.info(f"Modules to document: {', '.join(MODULES_TO_DOCUMENT)}")
    logger.info(f"HTML output directory: {html_dir}")
    logger.info(f"Markdown output directory: {markdown_dir}")

    try:
        # Generate HTML documentation
        generate_html_documentation(MODULES_TO_DOCUMENT, html_dir, args.clean)

        # Generate Markdown documentation
        generate_markdown_documentation(MODULES_TO_DOCUMENT, markdown_dir, args.clean)

        logger.info("✅ Documentation generation completed successfully!")
        logger.info(f"HTML documentation: {html_dir}")
        logger.info(f"Markdown documentation: {markdown_dir}")

    except Exception as e:
        logger.error(f"Failed to generate documentation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
