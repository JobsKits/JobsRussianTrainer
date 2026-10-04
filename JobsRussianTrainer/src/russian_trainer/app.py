"""Jobs · 多语种拼读表。"""

import sys
import random
import re

from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor, QFont, QKeySequence, QShortcut, QPalette
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QSlider, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox,
)

from russian_trainer.data import (
    COURSES, HANGUL_CODAS, SOFT_VOWELS, VOWELS, CONSONANTS,
    RUSSIAN_COURSE, uncommon,
)
from russian_trainer.speech import Speaker, language_engine, russian_engine

STYLE = """
QWidget { color: #243651; }
QDialog { background: #f4f6fa; }
QTableCornerButton::section { background: #eaf0fa; border: none;
 border-right: 1px solid #dbe4f3; border-bottom: 1px solid #dbe4f3; }
QToolTip { background: white; color: #243651; border: 1px solid #d5deeb; }
QMainWindow, QWidget#root { background: #f4f6fa; color: #182944; }
QLabel { color: #243651; }
QLabel#title { font-size: 28px; font-weight: 700; }
QLabel#subtitle { color: #6b7890; font-size: 13px; }
QLabel#phonetic { color: #6b7890; font-size: 10px; }
QLabel#syllable { color: #215bce; font-size: 52px; font-weight: 700; }
QWidget#card { background: white; border-radius: 14px; }
QPushButton { background: white; color: #254164; border: 1px solid #d5deeb;
 border-radius: 7px; padding: 8px 14px; font-size: 13px; }
QPushButton:hover { background: #eaf1ff; border-color: #98b6ee; }
QPushButton:pressed { background: #cedeff; }
QPushButton#primary { background: #285fcb; color: white; border: none; }
QComboBox { background: white; color: #243651; border: 1px solid #d5deeb;
 border-radius: 6px; padding: 6px 10px; min-height: 22px; }
QComboBox QAbstractItemView { background: white; color: #243651; selection-background-color: #dce8ff; }
QTableWidget { background: white; color: #243651; border: 1px solid #dce4f0;
 gridline-color: #e7edf5; selection-background-color: #285fcb; selection-color: white; }
QHeaderView::section { background: #eaf0fa; color: #294e85;
 border: none; border-right: 1px solid #dbe4f3; border-bottom: 1px solid #dbe4f3;
 padding: 8px; font-size: 19px; font-weight: 600; }
QSlider::groove:horizontal { height: 5px; background: #d7e1f1; border-radius: 2px; }
QSlider::handle:horizontal { width: 15px; margin: -5px 0; background: #285fcb; border-radius: 7px; }
"""


DARK_COLORS = {
    "#f4f6fa": "#171e29", "#182944": "#e5edf8", "#243651": "#e5edf8",
    "#6b7890": "#a5b5cc", "#215bce": "#80b0ff", "white": "#263244",
    "#254164": "#dce8fa", "#d5deeb": "#46566e", "#eaf1ff": "#344761",
    "#98b6ee": "#80b0ff", "#cedeff": "#415d82", "#dce8ff": "#415d82",
    "#dce4f0": "#46566e", "#e7edf5": "#38485e", "#eaf0fa": "#2e3e55",
    "#294e85": "#b4d1ff", "#dbe4f3": "#46566e", "#d7e1f1": "#46566e",
}


class TrainerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Jobs", "RussianTrainer")
        self.course = RUSSIAN_COURSE
        saved_course = self.settings.value("language", "ru")
        if saved_course in COURSES:
            self.course = COURSES[saved_course]
        self.current_coda = ""
        self.current_text = self.course.syllable(self.course.consonants[0], self.course.vowels[0]) or ""
        self.setWindowTitle(f"Jobs · {self.course.title}")
        self.resize(1120, 860)
        self.setMinimumSize(820, 600)
        engine_factory = russian_engine if self.course.key == "ru" else language_engine
        if self.course.key == "ru":
            self.engine, self.voices = engine_factory(self)
        else:
            self.engine, self.voices = engine_factory(self, self.course.locale)
        self.speaker = Speaker(self.engine, self, self.course.locale)
        self.root = QWidget(objectName="root")
        self.setCentralWidget(self.root)
        layout = QVBoxLayout(self.root)
        layout.setContentsMargins(26, 20, 26, 18)
        layout.setSpacing(12)
        titlebar = QHBoxLayout()
        self.title_label = QLabel(self.course.title, objectName="title")
        titlebar.addWidget(self.title_label)
        self.course_combo = QComboBox()
        for course in COURSES.values():
            self.course_combo.addItem(course.title, course.key)
        self.course_combo.setCurrentIndex(max(0, self.course_combo.findData(self.course.key)))
        self.course_combo.currentIndexChanged.connect(self.change_course)
        titlebar.addWidget(self.course_combo)
        titlebar.addStretch()
        self.theme_combo = QComboBox()
        self.theme_combo.setAccessibleName("界面主题")
        for label, mode in [("白天", "light"), ("黑夜", "dark"), ("跟随系统", "system")]:
            self.theme_combo.addItem(label, mode)
        saved_theme = self.settings.value("appearance/theme", "system")
        self.theme_combo.setCurrentIndex(max(0, self.theme_combo.findData(saved_theme)))
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        titlebar.addWidget(self.theme_combo)
        self.help_button = QPushButton("语音帮助")
        self.help_button.clicked.connect(self.show_help)
        titlebar.addWidget(self.help_button)
        layout.addLayout(titlebar)
        self.subtitle = QLabel(objectName="subtitle")
        layout.addWidget(self.subtitle)

        self.card = QWidget(objectName="card")
        card_layout = QHBoxLayout(self.card)
        card_layout.setContentsMargins(22, 12, 22, 12)
        self.syllable = QLabel("ба", objectName="syllable")
        self.syllable.setMinimumWidth(105)
        card_layout.addWidget(self.syllable)
        details = QVBoxLayout()
        self.formula = QLabel("б + а")
        self.formula.setFont(QFont("", 15, QFont.Weight.Bold))
        self.transcription = QLabel()
        self.transcription.setFont(QFont("", 13))
        self.hint = QLabel(self.course.notice)
        self.hint.setWordWrap(True)
        details.addWidget(self.formula)
        details.addWidget(self.transcription)
        details.addWidget(self.hint)
        card_layout.addLayout(details, 1)
        layout.addWidget(self.card)

        controls = QHBoxLayout()
        self.voice_label = QLabel(f"{self.course.title}声音")
        controls.addWidget(self.voice_label)
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(
            [voice.name() for voice in self.voices]
            or [f"未安装{self.course.title}声音"]
        )
        self.voice_combo.setEnabled(bool(self.voices))
        saved_voice = self.settings.value(self._setting_key("voice"), "")
        index = self.voice_combo.findText(saved_voice)
        if index >= 0:
            self.voice_combo.setCurrentIndex(index)
        self.voice_combo.currentIndexChanged.connect(self.change_voice)
        controls.addWidget(self.voice_combo)
        controls.addSpacing(14)
        self.coda_label = QLabel("收音")
        controls.addWidget(self.coda_label)
        self.coda_combo = QComboBox()
        for coda in HANGUL_CODAS:
            self.coda_combo.addItem("无收音" if not coda else coda, coda)
        self.coda_combo.setVisible(bool(self.course.codas))
        self.coda_label.setVisible(bool(self.course.codas))
        self.coda_combo.currentIndexChanged.connect(self.change_coda)
        controls.addWidget(self.coda_combo)
        controls.addSpacing(14)
        controls.addWidget(QLabel("语速"))
        self.rate_combo = QComboBox()
        for title, rate in [("慢速", -0.4), ("稍慢", -0.2), ("正常", 0.0)]:
            self.rate_combo.addItem(title, rate)
        self.rate_combo.setCurrentIndex(max(0, min(2, self.settings.value(self._setting_key("rate"), 1, type=int))))
        self.rate_combo.currentIndexChanged.connect(self.change_rate)
        controls.addWidget(self.rate_combo)
        controls.addWidget(QLabel("重复"))
        self.repeat_combo = QComboBox()
        self.repeat_combo.addItems(["1 次", "2 次", "3 次"])
        self.repeat_combo.setCurrentIndex(max(0, min(2, self.settings.value(self._setting_key("repeat"), 0, type=int))))
        controls.addWidget(self.repeat_combo)
        controls.addSpacing(14)
        controls.addWidget(QLabel("音量"))
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(max(0, min(100, self.settings.value(self._setting_key("volume"), 85, type=int))))
        self.volume.setMaximumWidth(110)
        self.volume.valueChanged.connect(self.change_volume)
        controls.addWidget(self.volume)
        controls.addStretch()
        layout.addLayout(controls)

        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setMinimumSectionSize(48)
        self.table.horizontalHeader().setMinimumHeight(64)
        self.table.verticalHeader().setDefaultSectionSize(64)
        for header in (self.table.horizontalHeader(), self.table.verticalHeader()):
            header.setSectionsClickable(True)
            header.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
            header.setFont(QFont("", 26, QFont.Weight.Bold))
        self.table.horizontalHeader().sectionClicked.connect(lambda col: self.play_letter(self.course.vowels[col]))
        self.table.verticalHeader().sectionClicked.connect(lambda row: self.play_letter(self.course.consonants[row]))
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFont(QFont("", 12))
        self.table.cellClicked.connect(self.play_cell)
        self.table.currentCellChanged.connect(self.selection_changed)
        layout.addWidget(self.table, 1)
        self.legend = QLabel(objectName="subtitle")
        layout.addWidget(self.legend)

        actions = QHBoxLayout()
        for text, callback, primary in [
            ("再听一次  Space", self.replay, True),
            ("整行连读", self.play_row, False),
            ("随机练习", self.play_random, False),
            ("停止  Esc", self.stop, False),
        ]:
            button = QPushButton(text)
            if primary:
                button.setObjectName("primary")
            button.clicked.connect(callback)
            actions.addWidget(button)
        actions.addStretch()
        layout.addLayout(actions)
        self.status = QLabel("准备好了 · 点击任一格子开始" if self.engine else f"未检测到{self.course.title}声音 · 请先查看「语音帮助」")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.shortcuts = []
        for key, callback in [("Space", self.replay), ("Return", self.replay), ("Escape", self.stop)]:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(callback)
            self.shortcuts.append(shortcut)
        self._connect_speaker()
        self._update_course_labels()
        self._rebuild_table()
        self.table.setCurrentCell(0, 0)
        self.change_voice()
        self.change_rate()
        self.change_volume()
        self._changing_theme = False
        QApplication.instance().styleHints().colorSchemeChanged.connect(self.system_theme_changed)
        self.change_theme()

    def _setting_key(self, name):
        return name if self.course.key == "ru" else f"{self.course.key}/{name}"

    def _connect_speaker(self):
        self.speaker.started.connect(self.on_started)
        self.speaker.finished.connect(lambda: self.status.setText("播放完成 · 可以跟读，或按空格重听"))
        self.speaker.failed.connect(self.on_error)

    def _save_course_settings(self):
        self.settings.setValue(self._setting_key("voice"), self.voice_combo.currentText())
        self.settings.setValue(self._setting_key("rate"), self.rate_combo.currentIndex())
        self.settings.setValue(self._setting_key("repeat"), self.repeat_combo.currentIndex())
        self.settings.setValue(self._setting_key("volume"), self.volume.value())

    def _update_course_labels(self):
        self.setWindowTitle(f"Jobs · {self.course.title}")
        self.title_label.setText(self.course.title)
        self.voice_label.setText(f"{self.course.title}声音")
        self.subtitle.setText(
            f"{self.course.locale}  /  点上方元音、左侧辅音 / 声母或中间组合即可朗读"
        )

    def _rebuild_table(self):
        self.table.setRowCount(len(self.course.consonants))
        self.table.setColumnCount(len(self.course.vowels))
        self.table.setHorizontalHeaderLabels([
            self.course.display_vowel(v) for v in self.course.vowels
        ])
        self.table.setVerticalHeaderLabels(self.course.consonants)
        for column, vowel in enumerate(self.course.vowels):
            self.table.horizontalHeaderItem(column).setToolTip(
                f"点击试听元音 {self.course.display_vowel(vowel)} · {self.course.pronunciation_hint_for_vowel(vowel)}"
            )
        for row, consonant in enumerate(self.course.consonants):
            self.table.verticalHeaderItem(row).setToolTip(f"点击朗读辅音字母或声母 {consonant}")
            for column, vowel in enumerate(self.course.vowels):
                syllable = self.course.syllable(consonant, vowel, self.current_coda)
                rare = self.course.is_rare(consonant) or (
                    self.course.key == "ru" and uncommon(consonant, vowel)
                )
                label = syllable or "—"
                display = label + (" ·" if rare and syllable else "")
                annotation = (
                    self.course.pronunciation_hint(consonant, vowel, self.current_coda)
                    if syllable else ""
                )
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setToolTip(self.course.hint(consonant, vowel, self.current_coda))
                if syllable is None:
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, column, item)
                self._set_table_cell(row, column, display, annotation)
        self._paint_table(self._is_dark_theme())

    def _set_table_cell(self, row, column, title, annotation):
        container = QWidget()
        container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(1, 0, 1, 0)
        layout.setSpacing(0)
        glyph = QLabel(title)
        glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        glyph.setFont(QFont("", 25, QFont.Weight.Bold))
        layout.addWidget(glyph)
        if annotation:
            note = QLabel(annotation, objectName="phonetic")
            note.setAlignment(Qt.AlignmentFlag.AlignCenter)
            note.setWordWrap(True)
            layout.addWidget(note)
        self.table.setCellWidget(row, column, container)

    def _is_dark_theme(self):
        mode = self.theme_combo.currentData()
        scheme = QApplication.instance().styleHints().colorScheme()
        return mode == "dark" or (mode == "system" and scheme == Qt.ColorScheme.Dark)

    def _paint_table(self, dark):
        for row, consonant in enumerate(self.course.consonants):
            for column, vowel in enumerate(self.course.vowels):
                item = self.table.item(row, column)
                if item is None:
                    continue
                rare = self.course.is_rare(consonant) or (
                    self.course.key == "ru" and uncommon(consonant, vowel)
                )
                soft = self.course.key == "ru" and vowel in SOFT_VOWELS
                color = (
                    "#493c27" if rare else "#283e59" if soft else "#263244"
                ) if dark else (
                    "#fff4df" if rare else "#eef5ff" if soft else "#ffffff"
                )
                item.setBackground(QColor(color))
        if self.course.key == "ru":
            self.legend.setText(
                ("深灰：通常配硬音　深蓝：通常配软音　棕黄 ·：少见组合" if dark else
                 "白色：通常配硬音　浅蓝：通常配软音　浅黄 ·：少见组合") +
                "　｜　ъ、ь 是符号，不列作辅音"
            )
        elif self.course.is_hangul:
            self.legend.setText("ㅇ 作声母时不发音　｜　收音依拼写显示，实际读音随词中位置变化")
        else:
            self.legend.setText("· 外来词或少见字母组合　｜　拼写规则和地区读音见上方说明")
        self.table.viewport().update()

    def change_course(self, index):
        if index < 0:
            return
        key = self.course_combo.itemData(index)
        course = COURSES.get(key)
        if course is None or course.key == self.course.key:
            return
        self._save_course_settings()
        self.speaker.stop()
        self.speaker.deleteLater()
        if self.engine:
            self.engine.stop()
            self.engine.deleteLater()
        self.course = course
        self.current_coda = ""
        self.current_text = course.syllable(course.consonants[0], course.vowels[0]) or ""
        self.settings.setValue("language", course.key)
        self.engine, self.voices = language_engine(self, course.locale)
        self.speaker = Speaker(self.engine, self, course.locale)
        self._connect_speaker()
        self.voice_combo.blockSignals(True)
        self.voice_combo.clear()
        self.voice_combo.addItems([voice.name() for voice in self.voices] or [f"未安装{course.title}声音"])
        saved_voice = self.settings.value(self._setting_key("voice"), "")
        voice_index = self.voice_combo.findText(saved_voice)
        if voice_index >= 0:
            self.voice_combo.setCurrentIndex(voice_index)
        self.voice_combo.setEnabled(bool(self.voices))
        self.voice_combo.blockSignals(False)
        self.rate_combo.setCurrentIndex(max(0, min(2, self.settings.value(self._setting_key("rate"), 1, type=int))))
        self.repeat_combo.setCurrentIndex(max(0, min(2, self.settings.value(self._setting_key("repeat"), 0, type=int))))
        self.volume.setValue(max(0, min(100, self.settings.value(self._setting_key("volume"), 85, type=int))))
        self.coda_combo.blockSignals(True)
        self.coda_combo.setCurrentIndex(0)
        self.coda_combo.setVisible(bool(course.codas))
        self.coda_label.setVisible(bool(course.codas))
        self.coda_combo.blockSignals(False)
        self._update_course_labels()
        self.status.setText(
            "准备好了 · 点击任一格子开始"
            if self.engine
            else f"未检测到{self.course.title}声音 · 请先查看「语音帮助」"
        )
        self._rebuild_table()
        self.table.setCurrentCell(0, 0)
        self.change_voice()
        self.change_rate()
        self.change_volume()
        self._paint_table(self._is_dark_theme())

    def change_coda(self, index):
        if index < 0 or not self.course.is_hangul:
            return
        self.current_coda = self.coda_combo.itemData(index)
        self._rebuild_table()
        row = max(0, self.table.currentRow())
        column = max(0, self.table.currentColumn())
        self.table.setCurrentCell(row, column)

    def change_theme(self, *_):
        mode = self.theme_combo.currentData()
        self.settings.setValue("appearance/theme", mode)
        self.settings.sync()
        hints = QApplication.instance().styleHints()
        self._changing_theme = True
        try:
            if mode == "system":
                hints.unsetColorScheme()
            else:
                hints.setColorScheme(Qt.ColorScheme.Dark if mode == "dark" else Qt.ColorScheme.Light)
        finally:
            self._changing_theme = False
        self.system_theme_changed(hints.colorScheme())

    def system_theme_changed(self, scheme):
        if self._changing_theme:
            return
        mode = self.theme_combo.currentData()
        dark = mode == "dark" or (mode == "system" and scheme == Qt.ColorScheme.Dark)
        app = QApplication.instance()
        palette = QPalette()
        for role, color in {
            QPalette.ColorRole.Window: "#171e29" if dark else "#f4f6fa",
            QPalette.ColorRole.WindowText: "#e5edf8" if dark else "#243651",
            QPalette.ColorRole.Base: "#263244" if dark else "#ffffff",
            QPalette.ColorRole.Text: "#e5edf8" if dark else "#243651",
            QPalette.ColorRole.Button: "#2e3e55" if dark else "#eaf0fa",
            QPalette.ColorRole.ButtonText: "#e5edf8" if dark else "#243651",
            QPalette.ColorRole.Highlight: "#285fcb",
            QPalette.ColorRole.HighlightedText: "#ffffff",
            QPalette.ColorRole.ToolTipBase: "#263244" if dark else "#ffffff",
            QPalette.ColorRole.ToolTipText: "#e5edf8" if dark else "#243651",
        }.items():
            palette.setColor(QPalette.ColorGroup.All, role, QColor(color))
        app.setPalette(palette)
        style = STYLE
        if dark:
            style = re.sub(r"#[0-9a-fA-F]{6}|\bwhite\b",
                           lambda match: DARK_COLORS.get(match.group(), match.group()), style)
            # 高亮与主按钮仍使用白字，避免跟随普通表面的颜色替换。
            style += "QPushButton#primary { color: #ffffff; } QTableWidget { selection-color: #ffffff; }"
        app.setStyleSheet(style)
        self._paint_table(dark)

    def selection_changed(self, row, col, *_):
        if row < 0 or col < 0:
            return
        if row >= len(self.course.consonants) or col >= len(self.course.vowels):
            return
        consonant = self.course.consonants[row]
        vowel = self.course.vowels[col]
        syllable = self.course.syllable(consonant, vowel, self.current_coda)
        self.current_text = syllable or ""
        self.syllable.setText(syllable or "—")
        coda_text = f" + {self.current_coda}" if self.current_coda else ""
        self.formula.setText(f"{consonant} + {self.course.display_vowel(vowel)}{coda_text}")
        self.transcription.setText(self.course.pronunciation_hint(consonant, vowel, self.current_coda))
        self.hint.setText(self.course.hint(consonant, vowel, self.current_coda))

    def play_cell(self, row, col):
        self.selection_changed(row, col)
        if self.current_text:
            self.speaker.play([self.current_text], self.repeat_combo.currentIndex() + 1)

    def show_letter(self, letter):
        self.current_text = letter
        self.table.clearSelection()
        self.syllable.setText(letter)
        kind = "元音" if letter in self.course.vowels else "辅音字母 / 声母"
        display = self.course.display_vowel(letter) if letter in self.course.vowels else letter
        self.formula.setText(f"{kind} · {display}")
        if letter in self.course.vowels:
            self.transcription.setText(self.course.pronunciation_hint_for_vowel(letter))
        elif letter in self.course.consonants:
            self.transcription.setText(self.course.pronunciation_hint_for_consonant(letter))
        else:
            self.transcription.clear()
        self.hint.setText(
            "单个字母试听 · 系统可能读出字母名称；辅音字母名称不等于纯辅音音素。"
        )

    def play_letter(self, letter):
        self.show_letter(letter)
        speech_text = (
            self.course.syllable("ء", letter) or letter
            if self.course.key == "ar" and letter in self.course.vowels
            else letter
        )
        self.speaker.play([speech_text], self.repeat_combo.currentIndex() + 1)

    def replay(self):
        if self.current_text:
            self.speaker.play([self.current_text], self.repeat_combo.currentIndex() + 1)

    def play_row(self):
        row = max(0, self.table.currentRow())
        consonant = self.course.consonants[row]
        syllables = [
            syllable
            for vowel in self.course.vowels
            if (syllable := self.course.syllable(consonant, vowel, self.current_coda))
        ]
        self.speaker.play(syllables, self.repeat_combo.currentIndex() + 1)

    def play_random(self):
        choices = [
            (row, column)
            for row, consonant in enumerate(self.course.consonants)
            for column, vowel in enumerate(self.course.vowels)
            if self.course.syllable(consonant, vowel, self.current_coda)
            and not self.course.is_rare(consonant)
            and not (self.course.key == "ru" and uncommon(consonant, vowel))
        ]
        if not choices:
            return
        row, col = random.choice(choices)
        self.table.setCurrentCell(row, col)
        self.play_cell(row, col)

    def stop(self):
        self.speaker.stop()
        self.status.setText("已停止 · 点击格子重新播放")

    def on_started(self, syllable):
        if syllable in self.course.vowels or syllable in self.course.consonants:
            self.show_letter(syllable)
        else:
            for row, consonant in enumerate(self.course.consonants):
                for column, vowel in enumerate(self.course.vowels):
                    if self.course.syllable(consonant, vowel, self.current_coda) == syllable:
                        self.table.setCurrentCell(row, column)
                        self.table.item(row, column).setSelected(True)
                        self.selection_changed(row, column)
                        self.table.scrollToItem(self.table.item(row, column))
                        break
        self.status.setText(f"正在朗读：{syllable} · 跟着声音练习")

    def on_error(self, message):
        self.status.setText("发音失败：" + message)

    def change_voice(self, *_):
        index = self.voice_combo.currentIndex()
        if self.engine and 0 <= index < len(self.voices):
            self.speaker.stop()
            self.engine.setVoice(self.voices[index])

    def change_rate(self, *_):
        if self.engine:
            self.engine.setRate(self.rate_combo.currentData())

    def change_volume(self, *_):
        if self.engine:
            self.engine.setVolume(self.volume.value() / 100)

    def show_help(self):
        QMessageBox.information(
            self,
            f"{self.course.title}声音与学习说明",
            f"本应用离线调用系统{self.course.title}语音，不上传内容。\n\n"
            "点击顶部元音或左侧辅音 / 声母，可单独朗读；也可点击表格组合。"
            "单个字母可能按字母名称朗读，不等同于纯辅音音素。\n\n"
            f"{self.course.notice}\n\n"
            "如果声音不可用，请到系统语音设置安装对应语言声音后重新打开应用。"
            "系统 TTS 不是经教师逐项审校的音素录音；实际单词还可能受拼写位置、重音、"
            "连音、音变或地区发音影响。\n\n"
            "空格 / 回车：重听；方向键：选格；Esc：停止。快速点新格会取消之前的朗读。",
        )

    def closeEvent(self, event):
        self.speaker.stop()
        self._save_course_settings()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JobsRussianTrainer")
    app.setOrganizationName("Jobs")
    app.setStyle("Fusion")
    window = TrainerWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
