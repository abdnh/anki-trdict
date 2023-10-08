import os
import sys
from typing import List

from anki.hooks import field_filter
from anki.template import TemplateRenderContext
from aqt.browser.browser import Browser
from aqt.editor import Editor
from aqt.gui_hooks import browser_menus_did_init, editor_did_init_buttons
from aqt.operations import CollectionOp
from aqt.qt import *
from aqt.utils import showText, tooltip

from .consts import *

sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

import tdk

tdk.TDK.user_agent = USER_AGENT

from .audiocache import get_audio
from .consts import *
from .gui.dialog import TRDictDialog
from .tooltips import init_webview


def on_bulk_updated_notes(browser: Browser, errors: List[str], updated_count: int):
    msg = f"Updated {updated_count} note(s) with data from the TDK dictionary."
    if errors:
        msg += " The following issues happened during the process:\n"
        msg += "\n".join(errors)
        showText(msg, parent=browser, title=consts.name)
    else:
        tooltip(msg, parent=browser)


def on_browser_action_triggered(browser: Browser) -> None:
    notes = [browser.mw.col.get_note(nid) for nid in browser.selected_notes()]
    dialog = TRDictDialog(browser.mw, browser, notes)
    if dialog.exec():
        CollectionOp(
            parent=browser,
            op=lambda col: col.update_notes(dialog.updated_notes),
        ).success(
            lambda out: on_bulk_updated_notes(
                browser, dialog.errors, len(dialog.updated_notes)
            ),
        ).run_in_background()


def on_browser_menus_did_init(browser: Browser):
    a = QAction("Bulk-define selected Turkish words", browser)
    qconnect(a.triggered, lambda: on_browser_action_triggered(browser))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)


def on_editor_button_clicked(editor: Editor) -> None:
    if editor.note:
        dialog = TRDictDialog(editor.mw, editor.parentWindow, [editor.note])
        if dialog.exec():
            editor.loadNoteKeepingFocus()


def on_editor_did_init_buttons(buttons: List[str], editor: Editor):
    button = editor.addButton(
        icon=os.path.join(consts.dir, "icon.svg"),
        cmd="trdict",
        tip=consts.name,
        func=on_editor_button_clicked,
    )
    buttons.append(button)


def trdict_filter(
    field_text: str,
    field_name: str,
    filter_name: str,
    ctx: TemplateRenderContext,
) -> str:
    if not filter_name.startswith("trdict"):
        return field_text

    # only 'trdict-audio' is supported for now
    option = filter_name.split("-")[1].lower()
    if option != "audio":
        return field_text

    try:
        files = get_audio(field_text)
    except Exception as ex:
        return f'<div style="color: red;">{str(ex)}</div>'

    sound_refs = "".join(map(lambda f: f"[sound:{f}]", files))

    return sound_refs


browser_menus_did_init.append(on_browser_menus_did_init)
editor_did_init_buttons.append(on_editor_did_init_buttons)
field_filter.append(trdict_filter)
init_webview()
