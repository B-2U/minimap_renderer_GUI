import sys
import os
from pathlib import Path
import webbrowser
import time

import flet as ft  # type: ignore
import requests  # type: ignore
from renderer.render import Renderer  # type: ignore
from replay_parser import ReplayParser  # type: ignore
from renderer.utils import LOGGER  # type: ignore

from app.utils import *

python = sys.executable


def main(page: ft.Page):
    # rendering
    def on_dialog_result(e: ft.FilePickerResultEvent):
        if not e.files:
            return

        any_success = False
        files = [file.path for file in e.files]
        body.controls.pop(0)
        body.update()
        progs = []
        for file in files:
            path = Path(file)
            prog = ft.Column(
                [ft.Text(f"{path.stem}.mp4", style=ft.TextThemeStyle.BODY_LARGE)]
            )
            body.controls.append(prog)
            progs.append(prog)

            body.update()
        for index, file in enumerate(files):
            try:
                progs[index].controls.append(ft.ProgressBar())
                body.update()

                path = Path(file)
                video_path = output_path.joinpath(f"{path.stem}.mp4")
                with open(path, "rb") as f:
                    LOGGER.info("Parsing the replay file...")
                    replay_info = ReplayParser(
                        f, strict=True, raw_data_output=False
                    ).get_info()
                    LOGGER.info("Rendering the replay file...")
                    renderer = Renderer(
                        replay_info["hidden"]["replay_data"],
                        logs=True,
                        use_tqdm=True,
                        enable_chat=setting_chat.value,
                        anon=setting_anon.value,
                    )
                    renderer.start(str(video_path))
                    LOGGER.info(f"The video file is at: {str(video_path)}")

                    progs[index].controls.pop(1)
                    progs[index].controls[0] = ft.Text(
                        f"✅ {path.stem}.mp4 ", style=ft.TextThemeStyle.BODY_LARGE
                    )

                any_success = True

            except:
                progs[index].controls.pop(1)
                body.controls[index] = ft.Text(
                    f"❌ {path.stem}.mp4", style=ft.TextThemeStyle.BODY_LARGE
                )

            body.update()

        body.controls = [upload_container]
        time.sleep(2)
        body.update()
        if any_success:
            os.startfile(output_path)

    def set_output_folder(e: ft.FilePickerResultEvent):
        if not e.path:
            return
        else:
            page.client_storage.set("output_path", str(e.path))
            output_path_title.value = f"{str(e.path)}\\"
            output_path_title.update()

    def update_renderer(e):
        body.controls = [
            ft.Column(
                [
                    ft.Text(
                        "Updating modules, it might take a few minutes... ",
                        style=ft.TextThemeStyle.BODY_LARGE,
                    ),
                    ft.ProgressBar(),
                ]
            )
        ]
        body.update()
        run_pip_from_git(
            "https://github.com/WoWs-Builder-Team/minimap_renderer.git",
            "minimap_renderer",
            "--force-reinstall --no-deps",
        )
        body.controls = [upload_container]
        page.snack_bar = ft.SnackBar(
            ft.Text(
                f"Updated succesfully!, Current supported version: {get_installed_version()}"
            ),
            action="Alright!",
            bgcolor="green",
        )
        page.snack_bar.open = True
        version_text.value = f"Installed version: {get_installed_version()}"
        page.update()

    # check local files
    def get_installed_version() -> str:
        path = Path(os.getcwd()).joinpath(
            "renderer_venv/Lib/site-packages/renderer/versions/"
        )
        versions = [p for p in path.iterdir() if p.is_dir() and p.name != "__pycache__"]
        version = versions[-1].name.replace("_", ".")
        return version

    # check repo
    def get_repo_version() -> str:
        api_url = "https://api.github.com/repos/WoWs-Builder-Team/minimap_renderer/contents/src/replay_unpack/clients/wows/versions"

        versions = [
            p
            for p in requests.get(api_url).json()
            if p["type"] == "dir" and p["name"] != "__pycache__"
        ]
        version = versions[-1]["name"].replace("_", ".")
        return version

    def page_resize(e):
        body.height = page.window_height - 120
        body.update()

    version_text = ft.Text(
        f"Installed version: {get_installed_version()}",
        style=ft.TextThemeStyle.BODY_SMALL,
    )

    # reading settings
    if page.client_storage.contains_key("output_path"):
        output_path = Path(page.client_storage.get("output_path"))

    else:
        output_path = Path(os.getcwd()).joinpath("output_videos")
        output_path.mkdir(parents=True, exist_ok=True)

    # components
    github_btn = ft.ElevatedButton(
        "Github",
        icon=ft.icons.HOME_ROUNDED,
        on_click=lambda _: webbrowser.open(
            "https://github.com/WoWs-Builder-Team/minimap_renderer", new=0
        ),
        style=ft.ButtonStyle(
            # color = {
            #     ft.MaterialState.HOVERED: "green",
            #     ft.MaterialState.DEFAULT: "blue",
            # },
            shape=ft.buttons.RoundedRectangleBorder(radius=2),
        ),
    )

    body = ft.ResponsiveRow(
        [],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        height=600,
    )

    upload_container = ft.Container(
        ft.Text("Select replays", style=ft.TextThemeStyle.DISPLAY_MEDIUM),
        alignment=ft.alignment.center,
        border=ft.border.all(5, "#C0C0C0"),
        on_click=lambda _: file_picker.pick_files(
            allowed_extensions=["wowsreplay"], allow_multiple=True
        ),
    )

    body.controls.append(upload_container)

    # menu
    setting_chat = ft.Checkbox(
        label="Enable chat",
        value=True,
        fill_color="#C0C0C0",
        tooltip="render chat history or not",
    )
    setting_anon = ft.Checkbox(
        label="anonymous mode",
        value=False,
        fill_color="#C0C0C0",
        tooltip="players' ign will be replaced by tags",
    )
    setting = ft.PopupMenuButton(
        icon=ft.icons.SETTINGS,
        items=[
            ft.PopupMenuItem(
                text="render setting",
                content=ft.Column(
                    [
                        ft.Text("Render setting", style=ft.TextThemeStyle.BODY_LARGE),
                        setting_chat,
                        setting_anon,
                    ]
                ),
            ),
            ft.PopupMenuItem(),  # divider
            # ft.PopupMenuItem(text="D:\Codes\minimap_renderer\Codes\minimap_renderer", on_click = lambda _: output_folder_picker.get_directory_path()), # divider
            ft.PopupMenuItem(
                text="output setting",
                content=ft.Column(
                    [
                        ft.Text(
                            "Output setting",
                            tooltip="current output folder",
                            style=ft.TextThemeStyle.BODY_LARGE,
                        ),
                        output_path_title := ft.Text(
                            f"{output_path}\\", style=ft.TextThemeStyle.BODY_SMALL
                        ),
                        ft.ElevatedButton(
                            "change folder",
                            tooltip="change output folder",
                            on_click=lambda _: output_folder_picker.get_directory_path(),
                            style=ft.ButtonStyle(
                                shape=ft.buttons.RoundedRectangleBorder(radius=2),
                            ),
                        ),
                    ]
                ),
            ),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(
                content=ft.Column(
                    [
                        ft.Text("Update", style=ft.TextThemeStyle.BODY_LARGE),
                        ft.ElevatedButton(
                            "update modules",
                            tooltip="click it if WOWS updated recently and this tool failed to run",
                            on_click=update_renderer,
                            style=ft.ButtonStyle(
                                shape=ft.buttons.RoundedRectangleBorder(radius=2),
                            ),
                        ),
                        version_text,
                        ft.Text(
                            f"Latest version: {get_repo_version()}",
                            style=ft.TextThemeStyle.BODY_SMALL,
                        ),
                    ]
                )
            ),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(
                content=ft.Text(
                    "GUI made by B2U#0900", style=ft.TextThemeStyle.BODY_SMALL
                ),
            ),
        ],
    )

    # app bar
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.MAP),
        leading_width=40,
        title=ft.Text("Minimap renderer V1.1"),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[github_btn, setting],
    )

    # filer pickers
    file_picker = ft.FilePicker(on_result=on_dialog_result)
    output_folder_picker = ft.FilePicker(on_result=set_output_folder)
    page.overlay.append(file_picker)
    page.overlay.append(output_folder_picker)

    # page
    page.add(body)
    page.on_resize = page_resize
    page.update()
