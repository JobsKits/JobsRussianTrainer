"""Jobs · 俄语拼读表。"""

import sys
import random

from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor, QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QSlider, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox,
)

from russian_trainer.data import VOWELS, CONSONANTS, SOFT_VOWELS, uncommon, note
from russian_trainer.speech import Speaker, russian_engine

STYLE = """
QMainWindow, QWidget#root { background: #f4f6fa; color: #182944; }
QLabel { color: #243651; }
QLabel#title { font-size: 28px; font-weight: 700; }
QLabel#subtitle { color: #6b7890; font-size: 13px; }
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


class TrainerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Jobs", "RussianTrainer")
        self.setWindowTitle("Jobs · 俄语拼读表")
        self.resize(1120, 860)
        self.setMinimumSize(820, 600)
        self.engine, self.voices = russian_engine(self)
        self.speaker = Speaker(self.engine, self)
        self.speaker.started.connect(self.on_started)
        self.speaker.finished.connect(lambda: self.status.setText("播放完成 · 可以跟读，或按空格重听"))
        self.speaker.failed.connect(self.on_error)
        self.root = QWidget(objectName="root")
        self.setCentralWidget(self.root)
        layout = QVBoxLayout(self.root)
        layout.setContentsMargins(26, 20, 26, 18)
        layout.setSpacing(12)
        titlebar = QHBoxLayout()
        titlebar.addWidget(QLabel("俄语拼读表", objectName="title"))
        titlebar.addStretch()
        self.help_button = QPushButton("语音帮助")
        self.help_button.clicked.connect(self.show_help)
        titlebar.addWidget(self.help_button)
        layout.addLayout(titlebar)
        layout.addWidget(QLabel("РУССКИЙ  /  横向元音 × 纵向辅音 · 点一下，听一遍，再跟读", objectName="subtitle"))

        self.card = QWidget(objectName="card")
        card_layout = QHBoxLayout(self.card)
        card_layout.setContentsMargins(22, 12, 22, 12)
        self.syllable = QLabel("ба", objectName="syllable")
        self.syllable.setMinimumWidth(105)
        card_layout.addWidget(self.syllable)
        details = QVBoxLayout()
        self.formula = QLabel("б + а")
        self.formula.setFont(QFont("", 15, QFont.Weight.Bold))
        self.hint = QLabel(note("б", "а"))
        self.hint.setWordWrap(True)
        details.addWidget(self.formula)
        details.addWidget(self.hint)
        card_layout.addLayout(details, 1)
        layout.addWidget(self.card)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("俄语声音"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems([v.name() for v in self.voices] or ["未安装俄语语音"])
        self.voice_combo.setEnabled(bool(self.voices))
        saved_voice = self.settings.value("voice", "")
        index = self.voice_combo.findText(saved_voice)
        if index >= 0:
            self.voice_combo.setCurrentIndex(index)
        self.voice_combo.currentIndexChanged.connect(self.change_voice)
        controls.addWidget(self.voice_combo)
        controls.addSpacing(14)
        controls.addWidget(QLabel("语速"))
        self.rate_combo = QComboBox()
        for title, rate in [("慢速", -0.4), ("稍慢", -0.2), ("正常", 0.0)]:
            self.rate_combo.addItem(title, rate)
        self.rate_combo.setCurrentIndex(max(0, min(2, self.settings.value("rate", 1, type=int))))
        self.rate_combo.currentIndexChanged.connect(self.change_rate)
        controls.addWidget(self.rate_combo)
        controls.addWidget(QLabel("重复"))
        self.repeat_combo = QComboBox()
        self.repeat_combo.addItems(["1 次", "2 次", "3 次"])
        controls.addWidget(self.repeat_combo)
        controls.addSpacing(14)
        controls.addWidget(QLabel("音量"))
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(max(0, min(100, self.settings.value("volume", 85, type=int))))
        self.volume.setMaximumWidth(110)
        self.volume.valueChanged.connect(self.change_volume)
        controls.addWidget(self.volume)
        controls.addStretch()
        layout.addLayout(controls)

        self.table = QTableWidget(len(CONSONANTS), len(VOWELS))
        self.table.setHorizontalHeaderLabels([v.upper() + " " + v for v in VOWELS])
        self.table.setVerticalHeaderLabels([c.upper() + " " + c for c in CONSONANTS])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setMinimumSectionSize(57)
        self.table.verticalHeader().setDefaultSectionSize(43)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFont(QFont("", 18))
        for row, consonant in enumerate(CONSONANTS):
            for col, vowel in enumerate(VOWELS):
                rare = uncommon(consonant, vowel)
                item = QTableWidgetItem(consonant + vowel + (" ·" if rare else ""))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setToolTip(note(consonant, vowel))
                item.setBackground(QColor("#fff4df" if rare else "#eef5ff" if vowel in SOFT_VOWELS else "#ffffff"))
                self.table.setItem(row, col, item)
        self.table.cellClicked.connect(self.play_cell)
        self.table.currentCellChanged.connect(self.selection_changed)
        layout.addWidget(self.table, 1)
        layout.addWidget(QLabel("白色：通常配硬音　浅蓝：通常配软音　浅黄 ·：少见组合　｜　ъ、ь 是符号，不列作辅音", objectName="subtitle"))

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
        self.status = QLabel("准备好了 · 点击任一格子开始" if self.engine else "未检测到俄语声音 · 请先查看「语音帮助」")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.shortcuts = []
        for key, callback in [("Space", self.replay), ("Return", self.replay), ("Escape", self.stop)]:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(callback)
            self.shortcuts.append(shortcut)
        self.table.setCurrentCell(0, 0)
        self.change_voice()
        self.change_rate()
        self.change_volume()

    def selection_changed(self, row, col, *_):
        if row < 0 or col < 0:
            return
        c, v = CONSONANTS[row], VOWELS[col]
        self.syllable.setText(c + v)
        self.formula.setText(f"{c} + {v}")
        self.hint.setText(note(c, v))

    def play_cell(self, row, col):
        self.speaker.play([CONSONANTS[row] + VOWELS[col]], self.repeat_combo.currentIndex() + 1)

    def replay(self):
        self.play_cell(self.table.currentRow(), self.table.currentColumn())

    def play_row(self):
        consonant = CONSONANTS[self.table.currentRow()]
        self.speaker.play([consonant + v for v in VOWELS], self.repeat_combo.currentIndex() + 1)

    def play_random(self):
        choices = [(r, c) for r, consonant in enumerate(CONSONANTS)
                   for c, vowel in enumerate(VOWELS) if not uncommon(consonant, vowel)]
        row, col = random.choice(choices)
        self.table.setCurrentCell(row, col)
        self.play_cell(row, col)

    def stop(self):
        self.speaker.stop()
        self.status.setText("已停止 · 点击格子重新播放")

    def on_started(self, syllable):
        row, col = CONSONANTS.index(syllable[0]), VOWELS.index(syllable[1])
        self.table.setCurrentCell(row, col)
        self.table.scrollToItem(self.table.item(row, col))
        self.status.setText(f"正在朗读：{syllable} · 跟着声音练习")

    def on_error(self, message):
        self.status.setText("发音失败：" + message)

    def change_voice(self, *_):
        if self.engine:
            self.speaker.stop()
            self.engine.setVoice(self.voices[self.voice_combo.currentIndex()])

    def change_rate(self, *_):
        if self.engine:
            self.engine.setRate(self.rate_combo.currentData())

    def change_volume(self, *_):
        if self.engine:
            self.engine.setVolume(self.volume.value() / 100)

    def show_help(self):
        QMessageBox.information(self, "俄语声音与学习说明",
            "本应用离线调用系统俄语语音，不上传内容。\n\n"
            "macOS：系统设置 → 辅助功能 → 朗读相关设置 → 系统声音，添加俄语 Milena。\n"
            "Windows：设置 → 时间和语言 → 语言和区域，添加俄语并安装语音组件；安装后重启应用。"
            "如果声音仍未列出，请检查系统语音设置中是否存在俄语声音。\n\n"
            "每个格子都是‘辅音字母 + 元音字母’。浅黄格属于少见或非典型拼写，仍可试听。"
            "系统 TTS 不是专业音素引擎，孤立组合可能被读作字母名；音节并不等于完整词语，"
            "重音、弱化、软硬音和外来词例外需要结合教材学习。\n\n"
            "空格 / 回车：重听；方向键：选格；Esc：停止。快速点新格会取消之前的朗读。")

    def closeEvent(self, event):
        self.speaker.stop()
        self.settings.setValue("voice", self.voice_combo.currentText())
        self.settings.setValue("rate", self.rate_combo.currentIndex())
        self.settings.setValue("volume", self.volume.value())
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JobsRussianTrainer")
    app.setOrganizationName("Jobs")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    window = TrainerWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
