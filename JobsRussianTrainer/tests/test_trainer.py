"""覆盖快速点击取消、停止、重复与行序列等实际交互风险。"""

import unittest
import time
from unittest.mock import patch

from PySide6.QtCore import QObject, Signal
from PySide6.QtTest import QTest
from PySide6.QtTextToSpeech import QTextToSpeech
from PySide6.QtWidgets import QApplication

from russian_trainer.data import CONSONANTS, VOWELS, note, uncommon
from russian_trainer.speech import Speaker
from russian_trainer.app import TrainerWindow

APP = QApplication.instance() or QApplication([])


def wait_until(predicate, timeout=1.5):
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        QTest.qWait(20)
    return bool(predicate())


class FakeEngine(QObject):
    stateChanged = Signal(object)

    def __init__(self):
        super().__init__()
        self.spoken = []

    def say(self, text):
        self.spoken.append(text)

    def stop(self):
        self.stateChanged.emit(QTextToSpeech.State.Ready)

    def errorString(self):
        return "test error"


class PlaybackTests(unittest.TestCase):
    def setUp(self):
        self.engine = FakeEngine()
        self.speaker = Speaker(self.engine)

    def tearDown(self):
        self.speaker.stop()

    def test_latest_click_cancels_waiting_syllables(self):
        self.speaker.play(["ба", "бо"], 3)
        self.speaker.play(["ми"])
        self.assertTrue(wait_until(lambda: self.engine.spoken))
        self.assertEqual(self.engine.spoken, ["ми"])
        self.assertEqual(list(self.speaker.pending), [])

    def test_stop_prevents_pending_timer(self):
        self.speaker.play(["ба"])
        self.speaker.stop()
        QTest.qWait(200)
        self.assertEqual(self.engine.spoken, [])

    def test_repeat_and_row_order(self):
        done = []
        self.speaker.finished.connect(lambda: done.append(True))
        self.speaker.play(["ба", "бо"], 2)
        self.assertTrue(wait_until(lambda: self.engine.spoken))
        for _ in range(4):
            self.engine.stateChanged.emit(QTextToSpeech.State.Ready)
            # 不等待真实练习间隔，直接触发同一计时器槽。
            self.speaker.timer.stop()
            self.speaker._next()
        self.assertEqual(self.engine.spoken, ["ба", "ба", "бо", "бо"])
        self.assertEqual(done, [True])

    def test_error_clears_queue(self):
        errors = []
        self.speaker.failed.connect(errors.append)
        self.speaker.play(["ба", "бо"])
        self.engine.stateChanged.emit(QTextToSpeech.State.Error)
        self.assertEqual(errors, ["test error"])
        self.assertFalse(self.speaker.pending)
        self.assertFalse(self.speaker.timer.isActive())

    def test_missing_voice_is_visible(self):
        speaker = Speaker(None)
        errors = []
        speaker.failed.connect(errors.append)
        speaker.play(["ба"])
        self.assertEqual(len(errors), 1)


class TableTests(unittest.TestCase):
    def test_all_cells_accessible_and_bound_to_correct_text(self):
        with patch("russian_trainer.app.russian_engine", return_value=(None, [])):
            window = TrainerWindow()
        self.assertEqual((window.table.rowCount(), window.table.columnCount()), (21, 10))
        with patch.object(window.speaker, "play") as play:
            for row, consonant in enumerate(CONSONANTS):
                for col, vowel in enumerate(VOWELS):
                    self.assertIsNotNone(window.table.item(row, col))
                    window.table.setCurrentCell(row, col)
                    window.table.cellClicked.emit(row, col)
                    play.assert_called_with([consonant + vowel], 1)
                    self.assertEqual(window.syllable.text(), consonant + vowel)
        window.hide()
        window.deleteLater()

    def test_language_exceptions(self):
        self.assertNotIn("ь", CONSONANTS)
        self.assertNotIn("ъ", CONSONANTS)
        self.assertIn("接近 ы", note("ж", "и"))
        self.assertTrue(uncommon("ш", "я"))
        self.assertFalse(uncommon("м", "а"))


if __name__ == "__main__":
    unittest.main()
