"""构建/运行入口：依赖仅安装到工程专属虚拟环境。"""

import argparse
import json
import logging
import os
from artifact_shortcuts import clear_shortcuts, publish_shortcuts
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import venv
from datetime import datetime

PROJECT = Path(__file__).resolve().parents[1]
OUTER = PROJECT.parent
LOG = Path(tempfile.gettempdir()) / "JobsRussianTrainer-build.log"


def run(command, **kwargs):
    logging.info("执行：%s", command)
    with LOG.open("a", encoding="utf-8") as stream:
        subprocess.run(command, check=True, cwd=PROJECT, stdout=stream, stderr=subprocess.STDOUT, **kwargs)


def confirm_required_install(message):
    """缺失必需依赖时回车安装，任何非空输入取消整个流程。"""
    try:
        answer = input(message + "：直接回车安装，输入任意字符后回车取消：")
    except EOFError:
        raise SystemExit("没有交互输入，已取消依赖安装。")
    if answer != "":
        raise SystemExit("已取消依赖安装，停止当前流程。")


def environment(build):
    folder = PROJECT / ".venv"
    executable = folder / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not executable.exists():
        venv.EnvBuilder(with_pip=True).create(folder)
    check = "import PySide6.QtWidgets, PySide6.QtTextToSpeech" + (", PyInstaller" if build else "")
    if subprocess.run([str(executable), "-c", check], capture_output=True).returncode:
        confirm_required_install("需要联网补齐工程依赖")
        run([str(executable), "-m", "pip", "install", str(PROJECT) + ("[build]" if build else "")])
        run([str(executable), "-c", check])
    return executable


def build_app(executable):
    stamp = datetime.now().strftime("%Y.%m.%d %H-%M-%S")
    dist_root = OUTER / "dist"
    if dist_root.is_symlink():
        raise SystemExit("拒绝清理符号链接 dist，请检查输出目录。")
    clear_shortcuts(OUTER)
    if dist_root.exists():
        shutil.rmtree(dist_root)
    output = dist_root / stamp
    output.mkdir(parents=True)
    command = [str(executable), "-m", "PyInstaller", "--noconfirm", "--windowed",
               "--name", "JobsRussianTrainer", "--paths", str(PROJECT / "src"),
               "--distpath", str(output), "--workpath", str(PROJECT / "build" / stamp),
               "--specpath", str(PROJECT / "build"),
               "--hidden-import", "PySide6.QtTextToSpeech"]
    if sys.platform == "darwin":
        command += ["--osx-bundle-identifier", "com.jobs.russiantrainer"]
    else:
        command += ["--onefile"]
    # Homebrew / 自编译 Qt 不一定采用 wheel 目录；按真实构建环境补齐插件。
    probe = subprocess.check_output([
        str(executable), "-c",
        "import json; from PySide6.QtCore import QLibraryInfo; "
        "print(json.dumps(QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)))",
    ], text=True)
    plugins = Path(json.loads(probe))
    plugin_target = "PySide6/plugins" if os.name == "nt" else "PySide6/Qt/plugins"
    suffix = ".dll" if os.name == "nt" else ".dylib"
    for category in ("platforms", "texttospeech", "multimedia", "styles"):
        for plugin in sorted((plugins / category).glob("*" + suffix)):
            if "mock" not in plugin.name:
                command += ["--add-binary", f"{plugin}:{plugin_target}/{category}"]
    run(command + [str(PROJECT / "scripts" / "entry.py")])
    if sys.platform == "darwin":
        image = output / "JobsRussianTrainer.dmg"
        run(["/usr/bin/hdiutil", "create", "-volname", "JobsRussianTrainer",
             "-srcfolder", str(output / "JobsRussianTrainer.app"), "-format", "UDZO", str(image)])
    logging.info("构建完成：%s", output)
    artifact = output / "JobsRussianTrainer.app" if sys.platform == "darwin" else output / "JobsRussianTrainer.exe"
    if not artifact.exists():
        raise SystemExit("构建产物不存在：" + str(artifact))
    packages = sorted(output.glob("*.dmg" if sys.platform == "darwin" else "*.zip"))
    publish_shortcuts(OUTER, [artifact, *packages])
    if sys.platform == "darwin":
        subprocess.run(["open", str(output)], check=True)
        subprocess.run(["open", str(output / "JobsRussianTrainer.app")], check=True)
    else:
        subprocess.run(["explorer.exe", str(output)], check=False)
        subprocess.Popen([str(output / "JobsRussianTrainer.exe")], cwd=output)



def main():
    parser = argparse.ArgumentParser(description="Jobs 俄语拼读表：只在工程 .venv 安装依赖；生成前清理旧 dist；成功后打开产物目录并运行软件。")
    parser.add_argument("action", choices=["run", "build"])
    parser.add_argument("--yes", action="store_true", help="外层入口已展示自述并得到确认")
    args = parser.parse_args()
    if not args.yes:
        print(f"将准备工程 .venv，缺依赖时联网安装，然后{args.action}。日志：{LOG}。Ctrl+C 取消。")
        input("按回车继续：")
    if sys.platform not in ("darwin", "win32"):
        parser.error("此工程支持在 macOS 或 Windows 本机运行和构建。")
    if not (3, 11) <= sys.version_info[:2] < (3, 15):
        parser.error("请安装 Python 3.11–3.14。")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(LOG, encoding="utf-8"), logging.StreamHandler()])
    try:
        executable = environment(args.action == "build")
        if args.action == "build":
            build_app(executable)
        else:
            env = dict(os.environ, PYTHONPATH=str(PROJECT / "src"))
            run([str(executable), "-m", "russian_trainer.app"], env=env)
    except (OSError, subprocess.CalledProcessError):
        logging.exception("操作失败，请检查日志：%s", LOG)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
