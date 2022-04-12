import json
from typing import Any

from aqt import mw
from aqt.qt import QKeySequence, QShortcut

from aqt.reviewer import Reviewer
from aqt.webview import WebContent
from aqt.gui_hooks import (
    webview_will_set_content,
    card_will_show,
    webview_did_receive_js_message,
)

from anki.cards import Card

import tdk

base_path = f"/_addons/{mw.addonManager.addonFromModule(__name__)}/web"
mw.addonManager.setWebExports(__name__, r"web(vendor)*/.*\.(js|css)")
config = mw.addonManager.getConfig(__name__)
tooltip_enabled_notetypes = config["tooltip_enabled_notetypes"]


def should_enable_tooltip(notetype: str) -> bool:
    if tooltip_enabled_notetypes == "all":
        return True
    return notetype in tooltip_enabled_notetypes


def append_webcontent(webcontent: WebContent, context: Any):

    # TODO: allow in previewer and card layouts too
    if isinstance(context, Reviewer):
        webcontent.js.append(f"{base_path}/vendor/popper.min.js")
        webcontent.js.append(f"{base_path}/vendor/tippy.umd.min.js")
        webcontent.js.append(f"{base_path}/tooltips.js")

        webcontent.css.append(f"{base_path}/vendor/tippy.css")
        webcontent.css.append(f"{base_path}/vendor/animations.css")
        webcontent.css.append(f"{base_path}/vendor/light.css")
        webcontent.css.append(f"{base_path}/vendor/material.css")


def init_tooltips(text: str, card: Card, kind: str):
    notetype = card.note_type()["name"]
    js = ""
    if should_enable_tooltip(notetype):
        js = "<script>enableTooltips()</script>"
    else:
        js = "<script>disableTooltips()</script>"
    return text + js


def formatted_dict_entry(entry: tdk.TDKEntry) -> str:
    formatted = "<dl>"
    formatted += f"<dt>{entry.word}"
    formatted += "</dt><dd>"

    formatted += "<ol>"
    for k, def_entry in enumerate(entry.definitions):
        formatted += "<li>"
        if def_entry.properties:
            formatted += '<span class="trdict-prop">'
            for j, prop in enumerate(def_entry.properties):
                formatted += prop
                if j < len(def_entry.properties) - 1:
                    formatted += ", "
            formatted += "</span> "

        formatted += f"{def_entry.definition}</li>"

        for example in def_entry.examples:
            formatted += '"' + f'<span class="trdict-example">{example}</span>' + '"'
        formatted += "</li>"
    formatted += "</ol></dl>"

    return formatted


CSS = """
dd, dl, li {
    margin-left: 0px;
    padding-left: 0px;
}

dt {
    color: blue;
}

.trdict-prop {
    color: orange;
    font-style: italic;
}

#trdict-entry-list {
    list-style-type: upper-roman;
}

ol, ul, dd, dt {
    text-align: left;
}

ol, ul {
    padding-left: 20px;
}

.trdict-example {
    font-style: italic;
}

"""


def formatted_dict_entries(word: str) -> str:
    try:
        entries = tdk.TDK(word).entries
        formatted = '<ul id="trdict-entry-list">'
        for entry in entries:
            formatted += f"<li>{formatted_dict_entry(entry)}</li>"
        formatted += "</ul>"
        return formatted + f"<style>{CSS}</style>"
    except Exception as exc:
        return f'<div style="color: red">{exc}</div>'


def handle_popup_request(
    handled: tuple[bool, Any], message: str, context: Any
) -> tuple[bool, Any]:
    print(f"message: {message}")
    parts = message.split(":")
    cmd = parts[0]
    if cmd != "trdict" or len(parts) == 1:
        return handled
    subcmd, word = parts[1:3]
    if subcmd == "popup":
        contents = formatted_dict_entries(word)
        contents = json.dumps(contents)
        context.web.eval(f"globalThis.tippyInstance.setContent({contents});")
    return (True, None)


def show_tooltip():
    if mw.state != "review":
        return
    mw.reviewer.web.eval("showTooltipForSelection();")


def init_webview():
    webview_will_set_content.append(append_webcontent)
    card_will_show.append(init_tooltips)
    webview_did_receive_js_message.append(handle_popup_request)
    QShortcut(
        QKeySequence(config["tooltip_shortcut"]),
        mw,
        activated=show_tooltip,
    )
