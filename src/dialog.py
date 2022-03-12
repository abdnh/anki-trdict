import urllib
import urllib.request
from typing import List

from aqt.qt import *
from aqt.utils import showWarning
from anki.notes import Note
from aqt.operations import QueryOp

from .form import Ui_Dialog
from .consts import *

from tdk import TDK, NetworkError, NoAudioError, WordNotFoundError

PROGRESS_LABEL = "Updated {count} out of {total} note(s)"


class TRDictDialog(QDialog):
    def __init__(self, mw, parent, notes: List[Note]):
        super().__init__(parent)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.mw = mw
        self.notes = notes
        self.combos = [
            self.form.wordFieldComboBox,
            self.form.definitionFieldComboBox,
            self.form.sentenceFieldComboBox,
            self.form.audioFieldComboBox,
        ]
        self.setWindowTitle(ADDON_NAME_LONG)
        self.form.icon.setPixmap(QPixmap(os.path.join(ADDON_DIR, "icon.png")))
        self._fill_fields()
        qconnect(self.form.addButton.clicked, self.on_add)

    def _fill_fields(self):
        mids = set(note.mid for note in self.notes)
        if len(mids) > 1:
            showWarning(
                "Please select notes from only one notetype.",
                parent=self,
                title=ADDON_NAME,
            )
            self.done(0)
            return
        self.field_names = ["None"] + self.notes[0].keys()
        for i, combo in enumerate(self.combos):
            combo.addItems(self.field_names)
            selected = 0
            if len(self.field_names) - 1 > i:
                selected = i + 1
            combo.setCurrentIndex(selected)
            qconnect(
                combo.currentIndexChanged,
                lambda field_index, combo_index=i: self.on_selected_field_changed(
                    combo_index, field_index
                ),
            )

    def on_selected_field_changed(self, combo_index, field_index):
        if field_index == 0:
            return
        for i, combo in enumerate(self.combos):
            if i != combo_index and combo.currentIndex() == field_index:
                combo.setCurrentIndex(0)

    def on_add(self):
        if self.form.wordFieldComboBox.currentIndex == 0:
            self.done(0)
            return

        if self.form.wordFieldComboBox.currentIndex() == 0:
            showWarning("No word field selected.", parent=self, title="TRDict")
            return
        word_field = self.form.wordFieldComboBox.currentText()
        definition_field_i = self.form.definitionFieldComboBox.currentIndex()
        sentence_field_i = self.form.sentenceFieldComboBox.currentIndex()
        audio_field_i = self.form.audioFieldComboBox.currentIndex()

        def on_success(ret):
            if len(self.updated_notes) > 0:
                self.done(1)
            else:
                self.done(0)

        # FIXME: when our dialog is triggered from the editor and finished running,
        # the main window gets brought to the front instead of self.parent
        op = QueryOp(
            parent=self.parentWidget(),
            op=lambda col: self._fill_notes(
                word_field, definition_field_i, sentence_field_i, audio_field_i
            ),
            success=on_success,
        )
        # with_progress() was broken until Anki 2.1.50 (https://addon-docs.ankiweb.net/background-ops.html#read-onlynon-undoable-operations),
        # so this doesn't work on the latest stable release
        op.with_progress(
            PROGRESS_LABEL.format(count=0, total=len(self.notes))
        ).run_in_background()

    def _fill_notes(
        self, word_field, definition_field_i, sentence_field_i, audio_field_i
    ):
        self.errors = []
        self.updated_notes = []
        for note in self.notes:
            word = note[word_field]
            tdk = TDK(word)
            try:
                need_updating = False
                if definition_field_i:
                    definitions = self._get_definitions(tdk)
                    note[self.field_names[definition_field_i]] = definitions
                    need_updating = True
                if sentence_field_i:
                    sentences = self._get_sentences(tdk)
                    note[self.field_names[sentence_field_i]] = sentences
                    need_updating = True
                if audio_field_i:
                    audio = self._get_audio_files(tdk)
                    note[self.field_names[audio_field_i]] = audio
                    need_updating = True
            except NetworkError as ex:
                showWarning(str(ex), parent=self, title="TRDict")
                break
            except (WordNotFoundError, NoAudioError) as ex:
                self.errors.append(str(ex))
            finally:
                if need_updating:
                    self.updated_notes.append(note)
                    self.mw.taskman.run_on_main(
                        lambda: self.mw.progress.update(
                            label=PROGRESS_LABEL.format(
                                count=len(self.updated_notes), total=len(self.notes)
                            ),
                            value=len(self.updated_notes),
                            max=len(self.notes),
                        )
                    )

    def _get_definitions(self, tdk: TDK) -> str:
        field_contents = []
        for i, definition in enumerate(tdk.meanings, start=1):
            field_contents.append(f"{i:2}. {definition}")
        return "<br>".join(field_contents)

    def _get_sentences(self, tdk: TDK) -> str:
        field_contents = []
        for i, example in enumerate(tdk.examples, start=1):
            field_contents.append(f"{i:2}. {example}")
        return "<br>".join(field_contents)

    def _get_audio_files(self, tdk: TDK) -> str:
        field_contents = ""
        audio_links = tdk.audio_links
        for i, link in enumerate(audio_links):
            name = f"{tdk.word}_{i+1}{link[link.rfind('.'):]}"
            try:
                req = urllib.request.Request(
                    link, None, headers={"User-Agent": USER_AGENT}
                )
                with urllib.request.urlopen(req) as res:
                    name = self.mw.col.media.write_data(name, res.read())
                    field_contents += f"[sound:{name}]"
            except Exception:
                raise Exception("failed to download audio")
        return field_contents
