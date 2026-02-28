from __future__ import annotations

import os
import sys

from streamlit.web import cli as stcli


def main() -> None:
    script_path = os.path.join(os.path.dirname(__file__), "ui_dashboard.py")
    sys.argv = ["streamlit", "run", script_path]
    stcli.main()


if __name__ == "__main__":
    main()
