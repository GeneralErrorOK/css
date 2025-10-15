# Cybernet Scoring System
A terminal-ui based scoring dashboard for use @ Cybernet.

## Requirements
- Linux, macOS (with anything but Terminal.app), Windows (with Windows Terminal)
- Python 3.13 or higher
- UV (preferably globally installed)

## Configuration
All settings, including their explanations, are in `config/settings.py`. For
adjusting colors, refer to `style/css.tcss`.

## How to use it
Make sure your settings are correct. Then, from the root directory of the project, just run:

``uv run textual run cybernet-scoring-system.py``

If for some reason `uv` has not pulled the dependencies yet: `uv sync` should fix it.

Make sure you have the development server (`cybernet-scoring-server`) running when using DEV_SERVER_MODE.