# Jobs 多语种拼读表

![Jobs出品，必属精品](https://picsum.photos/1500/400)

[toc]

---

[▶ 观看俄语拼读表演示视频](./showMeNow.mp4)

https://github.com/user-attachments/assets/1ed73e9d-b8b2-499f-978c-f9d476dc0b0d

## 🔥 <font id=前言>前言</font>

使用 [**Python**](https://www.python.org/) 和 [**PySide6**](https://doc.qt.io/qtforpython-6/) 编写的离线桌面拼读工具，支持俄语、阿拉伯语、法语、西班牙语、朝鲜语和德语。课程数据、注音矩阵和系统语音会随顶部语种选择切换。

## 一、使用方法 <a href="#前言" style="font-size:17px; color:green;"><b>🔼</b></a> <a href="#🔚" style="font-size:17px; color:green;"><b>🔽</b></a>

- 点击格子：朗读当前语种的拼读组合；快速点击新格会取消上一项。
- 点击顶部元音或左侧辅音 / 声母：单独朗读对应字母；同样支持语速、重复与音量设置。系统可能使用字母名称朗读，辅音字母名称不等同于纯辅音音素。
- 俄语：10 个元音、21 个辅音，共 210 个组合；少见拼写组合会标记。
- 阿拉伯语：28 个辅音音值与三个短元音符号 `َ / ِ / ُ`；以 hamza 显示初始辅音，格子附简化拉丁注音和 IPA。日常文本常省略短元音；本表不含长元音和词中变化。
- 法语：6 个元音字母和常见辅音组合；格子附宽式 IPA，提供 `ch / gn / ph`，并处理 `q` 只能组成 `que / qui` 的基础规则。
- 西班牙语：5 个元音、22 个辅音字母及 `ch / ll`；格子附宽式 IPA，`q` 只显示 `que / qui`，提示 `c / g / h` 规则、`b / v` 同音及地区读音差异。
- 朝鲜语：19 个声母、21 个元音组合成音节块；格子附韩国修订罗马字和 IPA；可选择无收音或 27 种收音。
- 德语：8 个基础元音、外来词元音 `y`、20 个辅音及常见拼写组合；字母和组合用大字显示，IPA 注音以小字分层展示。`q` 行补写 `u`，长短元音与 `ch / c / s / v` 的读音受上下文影响。
- 空格 / 回车：重听当前字母或组合。方向键：移动选择。Esc：停止。
- 语速支持慢速、稍慢、正常；重复支持 1–3 次；支持音量、整行连读和随机练习。
- 点击组合后显示所选拼读和课程规则说明；各语种的语音、音量、语速及重复次数在关闭窗口时保存到系统用户设置。
- 所有拼读表格都显示与原文字并列的转写或宽式 IPA；这些标注是入门提示，系统 TTS 不是人工音素录音。
- 俄语矩阵以颜色区分硬 / 软音和少见组合；随机练习避开少见组合。韩语 `ㅇ` 作声母时不发音，收音在实际词语中可能发生连音与音变。
- 拼写组合可试听，但不代表所有排列都是常用音节。系统 TTS 可能读出字母名称；本工具不提供经教师逐项审校的音素录音，不替代教材。

## 二、运行与系统声音 <a href="#前言" style="font-size:17px; color:green;"><b>🔼</b></a> <a href="#🔚" style="font-size:17px; color:green;"><b>🔽</b></a>

仓库现有 Apple Silicon Mac `.app` / `.dmg` 是旧构建产物，不包含新增的阿拉伯语、法语、西班牙语、朝鲜语和德语入口；运行新增课程请按上文源码入口启动，或在目标平台重新打包。Windows 使用源码工程在本机打包。

成品应用无需安装 Python 或 Qt，但依赖操作系统中对应语种的语音包。没有目标语言声音时明确提示，不会用其它语种代替。

macOS：系统设置 → 辅助功能 → 朗读相关设置 → 系统声音，添加当前练习语种的声音；不同系统版本名称可能不同。

Windows：设置 → 时间和语言 → 语言和区域，添加当前练习语种并安装语音组件。完成后重新打开应用。优先采用系统 WinRT 引擎，必要时尝试 SAPI。

源码运行（在本 README 所在目录打开终端）：

```sh
python3 ./JobsRussianTrainer/scripts/manage.py run
```

Windows 将 `python3` 改为 `py -3`。构建／开发环境需要 Python 3.11–3.14。管理入口先展示说明并确认，仅在依赖缺失时安装到工程 `.venv`，不会修改全局 Python。

## 三、打包 <a href="#前言" style="font-size:17px; color:green;"><b>🔼</b></a> <a href="#🔚" style="font-size:17px; color:green;"><b>🔽</b></a>

| 入口 | 平台与用途 | 产物 |
| --- | --- | --- |
| `./【MacOS】📦生成dmg.command` | macOS 本机构建，双击后回车确认 | `./dist/YYYY.MM.DD HH-mm-ss/JobsRussianTrainer.app` 和 `.dmg` |
| `./【Windows】📦生成exe.bat` | Windows 本机构建，确认后检查 Python | `./dist/YYYY.MM.DD HH-mm-ss/JobsRussianTrainer.exe` |

使用 [**PyInstaller**](https://pyinstaller.org/) 包含 Python 运行时和 Qt 依赖。macOS 和 Windows 必须分别在对应系统上构建；Apple Silicon 与 Intel 默认跟随构建机架构。构建前清理旧 dist，时间戳目录仅保存本次产物。外层脚本只检查环境和调用内层构建器。

首次构建需要网络安装缺失依赖；正常使用发音不需要网络。日志追加保存在系统临时目录的 `JobsRussianTrainer-build.log`。Mac 入口只修改本项目环境与产物；不使用 sudo，不修改系统语音设置。应用未进行开发者证书签名或公证，公开分发前需自行配置。

## 四、工程结构 <a href="#前言" style="font-size:17px; color:green;"><b>🔼</b></a> <a href="#🔚" style="font-size:17px; color:green;"><b>🔽</b></a>

```text
JobsRussianTrainer.py/
├── README.md
├── 【MacOS】📦生成dmg.command
├── 【Windows】📦生成exe.bat
└── JobsRussianTrainer/
    ├── pyproject.toml
    ├── src/russian_trainer/
    │   ├── app.py             # 窗口和交互
    │   ├── data.py            # 六种语言课程、拉丁转写与 IPA 映射
    │   └── speech.py          # 多语种系统语音与串行播放
    ├── scripts/
    │   ├── entry.py           # 打包入口
    │   └── manage.py          # 虚拟环境、运行及构建
    └── tests/
```

## 五、验证与参考 <a href="#前言" style="font-size:17px; color:green;"><b>🔼</b></a> <a href="#🔚" style="font-size:17px; color:green;"><b>🔽</b></a>

```sh
cd ./JobsRussianTrainer
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 -m compileall -q src scripts tests
```

2026-10-04 德语及拼读字形层级通过 `python3 -m compileall -q src scripts`；2026-10-05 德语 `qu` 注音拼写修正通过课程文件 `compileall`。未运行 UI 或设备语音验证，旧成品未重新打包。

Windows 测试先执行 `set PYTHONPATH=src`，再使用 `py -3 -m unittest discover -s tests -v`。Windows 产物需在 Windows 上实际构建并验证声音，不能以 macOS 检查代替。

既有验证基线：Python 3.14.7、PySide6 6.11.2、PyInstaller 6.22.3、macOS arm64。系统语音是否提供阿拉伯语及其它课程声音，需在目标设备检查并试听；打包器与平台脚本沿用原工程配置。

参考：[康奈尔大学俄语字母与发音](https://russian.cornell.edu/russian.web/courses/305/letters_sounds_1.htm)、[沙迦大学阿拉伯语罗马转写工具](https://romanization.sharjah.ac.ae/firstpageView/)、[国际音标表](https://www.internationalphoneticassociation.org/content/ipa-chart)、[法国教育部法语音素表](https://www.education.gouv.fr/media/199500/download)、[西班牙皇家学院字母与拼写说明](https://www.rae.es/diccionario-estudiante/docs/ortografia.pdf)、[韩国国立国语院修订罗马字](https://www.korean.go.kr/front_eng/roman/roman_01.do)、[Qt 系统语音引擎](https://doc.qt.io/qt-6.5/qttexttospeech-engines.html)。

## 六、常见问题 <a href="#前言" style="font-size:17px; color:green;"><b>🔼</b></a> <a href="#🔚" style="font-size:17px; color:green;"><b>🔽</b></a>

**点击没有声音？** 先检查系统输出设备、系统与应用音量；查看窗口底部错误，再检查当前课程对应的语音包。安装后重新打开应用。

**某一格听起来不自然？** 浅黄格只是非典型组合试听；系统语音对孤立字母组合的处理并不等于经过审校的音节录音。结合教材或教师读音校正。

**能直接在 Mac 上生成 Windows EXE 吗？** 不能。把整个源码工程复制到 Windows，排除 `.venv`、`build`、`dist` 后运行 Windows 打包入口。

打包前会清理该应用工程的旧 `dist` 产物，清理失败则停止；成功后自动打开当前平台产物的磁盘位置并运行本次生成的 APP / EXE，结尾无需回车。失败时不启动软件；运行前的防误触确认保留。

必需依赖缺失时，直接回车联网安装；输入任意字符后回车取消整个流程。安装失败或复检仍不可用时停止，不继续清理旧产物或打包。健康依赖直接复用；可选升级和词库更新仍为回车跳过、任意字符执行。

第一层交付目录与平台打包脚本同层保存 `dist/`，以及最新 APP / DMG 的相对符号链接（Mac）或 EXE / 分发包的 `.lnk`（Windows）。双击快捷方式即可接触成品，真实文件保留在 `dist/`；成功构建自动更新入口，清理旧产物时移除对应旧入口。尚无成品时不生成无效快捷方式。

构建产物使用本机本地构建时间，格式为 `YYYY.MM.DD HH-mm-ss`（年月日时分秒），例如 `2020.06.04 12-23-21`。每次构建的 APP、DMG、EXE、ZIP 和配套文件统一保存到交付层 `./dist/YYYY.MM.DD HH-mm-ss/`，同次构建只取一次时间；第一层快捷方式指向本次时间目录，成功后打开该目录并启动其中的软件。旧产物沿用原有清理规则；历史产物缺少可靠构建时间时，不补写推测时间。

<a id="🔚" href="#前言" style="font-size:17px; color:green; font-weight:bold;">我是有底线的➤点我回到首页</a>
