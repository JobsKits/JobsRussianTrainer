"""直接运行成品的窗口、语音插件与播放队列冒烟检查。"""
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from russian_trainer.app import TrainerWindow, STYLE


def smoke_test():
    app = QApplication([])
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    window = TrainerWindow()
    window.show()
    started = []
    expected = ["ба", "ми", "шу"]
    window.speaker.started.connect(started.append)
    window.speaker.failed.connect(lambda message: (print(message, flush=True), app.exit(1)))

    def finished():
        success = started == expected and window.isVisible() and window.engine is not None
        print("PACKAGED SMOKE:", "PASS" if success else "FAIL", started, flush=True)
        app.exit(0 if success else 1)

    window.speaker.finished.connect(finished)
    QTimer.singleShot(300, lambda: window.speaker.play(expected))
    QTimer.singleShot(20000, lambda: app.exit(2))
    return app.exec()
