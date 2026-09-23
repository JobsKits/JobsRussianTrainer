"""系统俄语语音与可取消的串行播放。"""

import sys
from collections import deque

from PySide6.QtCore import QObject, QLocale, QTimer, Signal
from PySide6.QtTextToSpeech import QTextToSpeech


def russian_engine(parent: QObject):
    """选择真实系统引擎，禁止退回英语或 mock 静默成功。"""
    available = QTextToSpeech.availableEngines()
    preferred = ["darwin", "macos"] if sys.platform == "darwin" else ["winrt", "sapi"]
    for name in preferred:
        if name not in available:
            continue
        engine = QTextToSpeech(name, parent)
        engine.setLocale(QLocale("ru_RU"))
        voices = [v for v in engine.availableVoices() if v.locale().language() == QLocale.Language.Russian]
        if voices and engine.state() != QTextToSpeech.State.Error:
            engine.setVoice(voices[0])
            return engine, voices
        engine.deleteLater()
    return None, []


class Speaker(QObject):
    started = Signal(str)
    finished = Signal()
    failed = Signal(str)

    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.pending = deque()
        self.active = False
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._next)
        self.watchdog = QTimer(self)
        self.watchdog.setSingleShot(True)
        self.watchdog.setInterval(15000)
        self.watchdog.timeout.connect(lambda: self._error("语音响应超时，请检查系统语音包和声音输出。"))
        if engine:
            engine.stateChanged.connect(self._state_changed)

    def play(self, syllables, repeats=1):
        self.stop()
        if not self.engine:
            self.failed.emit("未找到俄语语音，请点击「语音帮助」，安装后重新打开应用。")
            return
        self.pending.extend(s for s in syllables for _ in range(repeats))
        # 等 stop 的平台回调完成，再启动最新请求，快速点击不会叠音。
        self.timer.start(80)

    def stop(self):
        self.timer.stop()
        self.watchdog.stop()
        self.pending.clear()
        self.active = False
        if self.engine:
            self.engine.stop()

    def _next(self):
        if not self.pending:
            self.finished.emit()
            return
        syllable = self.pending.popleft()
        self.started.emit(syllable)
        self.active = True
        self.watchdog.start()
        self.engine.say(syllable)

    def _state_changed(self, state):
        if state == QTextToSpeech.State.Error:
            self._error(self.engine.errorString() or "系统语音引擎错误。")
        elif state == QTextToSpeech.State.Ready and self.active:
            self.active = False
            self.watchdog.stop()
            self.timer.start(450)

    def _error(self, message):
        self.stop()
        self.failed.emit(message)
