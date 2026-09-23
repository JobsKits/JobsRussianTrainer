#!/bin/zsh
# 脚本自述：生成俄语拼读表 .app / .dmg；仅准备工程 .venv 和 dist。
# 运行提示：展示说明后回车继续，Ctrl+C 取消；缺依赖时联网安装。
# shell: zsh

# 展示固定说明并确认运行。
show_script_intro_and_wait() {
    print 'Jobs 俄语拼读表 · macOS 打包'
    print '用途：在本机生成包含 Python 和 Qt 的 .app / .dmg。'
    print '影响：工程 .venv / build / dist；缺依赖时联网安装，不升级健康环境。'
    print '日志：系统临时目录 JobsRussianTrainer-build.log；Ctrl+C 可取消。'
    [[ -t 0 ]] || { print '请在终端中运行。'; exit 1; }
    read -r '?按回车继续：' _
}
# 初始化路径及失败时保留终端。
initialize() {
    setopt NO_NOMATCH
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"
    LOG_FILE="${TMPDIR:-/tmp}/JobsRussianTrainer-build.log"
}
# 检查可实际运行的 Python，缺失时给出安装提示。
check_environment() {
    command -v python3 >/dev/null || { print '请安装 Python 3.11–3.14。'; read -r '?回车退出：' _; exit 1; }
    python3 -c 'import sys, venv; assert (3,11) <= sys.version_info[:2] < (3,15)' || { print 'Python 不可用或版本不匹配。'; read -r '?回车退出：' _; exit 1; }
}
# 调用共享构建器并保留失败输出。
run_business() {
    python3 "$SCRIPT_DIR/JobsRussianTrainer/scripts/manage.py" build --yes
    local result=$?
    if [[ "$result" -eq 0 ]]; then
        print '\033[1;32m✔ 构建完成，请查看工程 dist 目录。\033[0m'
    else
        print "\033[1;31m✖ 构建失败，日志：$LOG_FILE\033[0m"
    fi
    read -r '?按回车退出：' _
    exit "$result"
}
# 编排说明、环境检查与构建。
main() {
    show_script_intro_and_wait # 确认后才允许准备环境。
    initialize # 初始化路径和运行选项。
    check_environment # 验证构建运行时。
    run_business # 生成本机安装包。
}

main "$@"
