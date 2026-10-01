"""独立应用的打包入口。"""
import sys
from russian_trainer.app import main

if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        from russian_trainer.diagnostics import smoke_test
        raise SystemExit(smoke_test())
    else:
        raise SystemExit(main())
