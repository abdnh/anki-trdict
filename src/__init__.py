from typing import List

from aqt import mw
from aqt.gui_hooks import (
    browser_menus_did_init,
    editor_did_init_buttons,
)
from anki.hooks import field_filter
from anki.template import TemplateRenderContext
from aqt.qt import *
from aqt.browser.browser import Browser
from aqt.editor import Editor
from aqt.utils import showText, tooltip, showWarning
from aqt.operations import CollectionOp

from .dialog import TRDictDialog
from .audiocache import get_audio
from .consts import *


def on_bulk_updated_notes(browser: Browser, errors: List[str], updated_count: int):
    msg = f"Updated {updated_count} note(s) with data from the TDK dictionary."
    if errors:
        msg = +" The following issues happened during the process:\n"
        msg += "\n".join(errors)
        showText(msg, parent=browser, title=ADDON_NAME)
    else:
        tooltip(msg, parent=browser)


def on_browser_action_triggered(browser: Browser) -> None:
    notes = [mw.col.get_note(nid) for nid in browser.selected_notes()]
    dialog = TRDictDialog(mw, browser, notes)
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
    a = QAction("Update Selected from Turkish Dictionary", browser)
    qconnect(a.triggered, lambda: on_browser_action_triggered(browser))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)


def on_editor_button_clicked(editor: Editor) -> None:
    if editor.note:
        dialog = TRDictDialog(editor.mw, editor.widget, [editor.note])
        if dialog.exec():
            editor.loadNoteKeepingFocus()


def on_editor_did_init_buttons(buttons: List[str], editor: Editor):
    button = editor.addButton(
        icon=os.path.join(ADDON_DIR, "icon.svg"),
        cmd="trdict",
        tip=ADDON_NAME_LONG,
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
        showWarning(str(ex), title=ADDON_NAME)
        return field_text

    sound_refs = "".join(map(lambda f: f"[sound:{f}]", files))

    return sound_refs


browser_menus_did_init.append(on_browser_menus_did_init)
editor_did_init_buttons.append(on_editor_did_init_buttons)
field_filter.append(trdict_filter)
