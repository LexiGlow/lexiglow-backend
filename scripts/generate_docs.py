#!/usr/bin/env python3
"""
Documentation Generation Script for LexiGlow.

This script generates API documentation in both HTML and Markdown formats
using pdoc3 for the app/ and tests/ modules.

Usage:
    python scripts/generate_docs.py [--html-dir PATH] [--markdown-dir PATH] [--clean]

Options:
    --html-dir PATH      Directory for HTML documentation output (default: docs/html/)
    --markdown-dir PATH  Directory for Markdown documentation output
                            (default: docs/markdown/)
    --clean              Clean output directories before generating documentation
"""

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path

import markdown

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


def find_readme_and_init_pairs(base_path: Path) -> list[tuple[Path, Path]]:
    """
    Finds pairs of README.md and __init__.py files within a given base path.

    Args:
        base_path: The base directory to search within (e.g., BASE_DIR / "app").

    Returns:
        A list of tuples, where each tuple contains (readme_path, init_path).
    """
    pairs = []
    for root, _, files in base_path.walk():
        if "README.md" in files and "__init__.py" in files:
            readme_path = Path(root) / "README.md"
            init_path = Path(root) / "__init__.py"
            pairs.append((readme_path, init_path))
    return pairs


def inject_readme_into_init(readme_path: Path, init_path: Path) -> Path:
    """
    Injects the content of a README.md file into the module docstring
        of an __init__.py file.
    Creates a temporary backup of the original __init__.py.

    Args:
        readme_path: Path to the README.md file.
        init_path: Path to the __init__.py file.

    Returns:
        Path to the temporary backup file.
    """
    logger.info(f"Injecting {readme_path.name} into {init_path.name}")

    # Create a temporary backup of the original __init__.py
    temp_init_path = init_path.with_suffix(".py.bak")
    shutil.copyfile(init_path, temp_init_path)

    readme_content = readme_path.read_text(encoding="utf-8")
    init_content = init_path.read_text(encoding="utf-8")

    # Check if there's an existing module docstring
    if init_content.strip().startswith('"""') or init_content.strip().startswith("'''"):
        # Find the end of the existing docstring
        if init_content.strip().startswith('"""'):
            docstring_marker = '"""'
        else:
            docstring_marker = "'''"

        parts = init_content.split(docstring_marker, 2)
        if len(parts) == 3:
            # Append to existing docstring
            new_init_content = (
                f"{docstring_marker}{parts[1]}\n\n"
                f"--- Content from {readme_path.name} ---\n"
                f"{readme_content}\n"
                f"{docstring_marker}{parts[2]}"
            )
        else:
            # Should not happen if it starts with a docstring, but handle defensively
            new_init_content = (
                f"{docstring_marker}\n"
                f"--- Content from {readme_path.name} ---\n"
                f"{readme_content}\n"
                f"{docstring_marker}\n{init_content}"
            )
    else:
        # No existing docstring, add one at the beginning
        new_init_content = (
            f'"""\n'
            f"--- Content from {readme_path.name} ---\n"
            f"{readme_content}\n"
            f'"""\n{init_content}'
        )

    init_path.write_text(new_init_content, encoding="utf-8")
    logger.info(f"Successfully injected {readme_path.name} into {init_path.name}")
    return temp_init_path


def restore_init_files(modified_files: list[tuple[Path, Path]]) -> None:
    """
    Restores __init__.py files from their temporary backups.

    Args:
        modified_files: A list of tuples (original_init_path, temp_backup_path).
    """
    for original_path, temp_path in modified_files:
        if temp_path.exists():
            logger.info(f"Restoring {original_path.name} from backup.")
            shutil.move(temp_path, original_path)
        else:
            logger.warning(
                f"Backup file not found for {original_path.name}. "
                "Manual intervention might be needed if the file was modified."
            )


def generate_custom_index_html(output_dir: Path) -> None:
    """
    Generates a custom index.html file for GitHub Pages.

    Args:
        output_dir: The directory where the index.html will be created.
    """
    logger.info(f"Generating custom index.html in {output_dir}")

    main_readme_path = BASE_DIR / "README.md"
    main_readme_content = main_readme_path.read_text(encoding="utf-8")

    # Convert main README.md content to HTML
    main_readme_html = markdown.markdown(main_readme_content)

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LexiGlow Backend Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, 
            Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
            line-height: 1.6;
            color: #24292e;
            margin: 0;
            display: flex; /* Use flexbox for layout */
            min-height: 100vh; /* Full viewport height */
        }}
        #sidebar {{
            width: 250px; /* Fixed width for sidebar */
            background-color: #f6f8fa;
            padding: 30px 15px;
            border-right: 1px solid #e1e4e8;
            overflow-y: auto; /* Scrollable sidebar */
            flex-shrink: 0; /* Prevent sidebar from shrinking */
        }}
        #main-content {{
            flex-grow: 1; /* Main content takes remaining space */
            max-width: 900px; /* Max width for readability */
            margin: 0 auto; /* Center main content */
            padding: 30px;
            box-sizing: border-box; /* Include padding in width */
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #000;
            margin-top: 1em;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }}
        h1 {{ font-size: 2em; }}
        h2 {{ font-size: 1.5em; }}
        h3 {{ font-size: 1.25em; }}
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        code {{
            font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, 
            Courier, monospace;
            background-color: rgba(27,31,35,.05);
            border-radius: 3px;
            padding: .2em .4em;
        }}
        pre {{
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 16px;
            overflow: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        .documentation-links {{
            margin-top: 30px;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }}
        .documentation-links h2 {{
            margin-bottom: 15px;
        }}
        .documentation-links ul {{
            list-style: none;
            padding: 0;
        }}
        .documentation-links li {{
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div id="sidebar">
        <h2>LexiGlow Backend Docs</h2>
        <div class="documentation-links">
            <h3>Generated API Documentation</h3>
            <ul>
                <li><a href="app/index.html">Application Modules (app/)</a></li>
                <li><a href="tests/index.html">Test Modules (tests/)</a></li>
            </ul>
        </div>
    </div>
    <div id="main-content">
        <h1>LexiGlow Backend Documentation</h1>
        {main_readme_html}
    </div>
</body>
</html>
    """
    (output_dir / "index.html").write_text(html_content, encoding="utf-8")
    logger.info("✅ Custom index.html generated successfully!")


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
        # --skip-errors allows documentation generation even if
        # some modules fail to import
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
        # --skip-errors allows documentation generation even if
        # some modules fail to import
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
        help=(
            "Directory for Markdown documentation output (default: "
            f"{DEFAULT_MARKDOWN_DIR})"
        ),
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

    modified_init_files = []
    try:
        # Pre-process: Inject README.md content into __init__.py docstrings
        for module_name in MODULES_TO_DOCUMENT:
            module_path = BASE_DIR / module_name
            readme_init_pairs = find_readme_and_init_pairs(module_path)
            for readme_path, init_path in readme_init_pairs:
                temp_backup_path = inject_readme_into_init(readme_path, init_path)
                modified_init_files.append((init_path, temp_backup_path))

        # Generate HTML documentation
        generate_html_documentation(MODULES_TO_DOCUMENT, html_dir, args.clean)

        # Generate Markdown documentation
        generate_markdown_documentation(MODULES_TO_DOCUMENT, markdown_dir, args.clean)

        # Generate custom index.html
        generate_custom_index_html(html_dir)

        logger.info("✅ Documentation generation completed successfully!")
        logger.info(f"HTML documentation: {html_dir}")
        logger.info(f"Markdown documentation: {markdown_dir}")

    except Exception as e:
        logger.error(f"Failed to generate documentation: {e}")
        sys.exit(1)
    finally:
        # Post-process: Restore original __init__.py files
        restore_init_files(modified_init_files)


if __name__ == "__main__":
    main()
