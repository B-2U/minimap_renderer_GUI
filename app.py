if __name__ == "__main__":
    from app.utils import *

    if not is_installed("renderer"):
        print("this might take a few minutes...")
        run_pip_from_git(
            "https://github.com/WoWs-Builder-Team/minimap_renderer.git",
            desc="minimap_renderer",
            args="--upgrade --force-reinstall",
        )

    if not is_installed("flet"):
        run_pip("flet", "flet")

    if not is_installed("requests"):
        run_pip("requests", "requests")

    if not is_installed("langdetect"):
        run_pip("langdetect", "langdetect")

    import flet as ft  # type: ignore
    from app.main import main

    ft.app(target=main)
