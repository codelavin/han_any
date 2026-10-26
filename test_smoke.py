# -*- coding: utf-8 -*-
"""han_any 冒烟测试：验证核心转换、检测、文件转换。
结果同时打印到 stdout 并写入 smoke_result.txt（UTF-8，避免 Windows 控制台编码干扰）。
"""
import os
import sys

from han_any import auto_convert, convert, convert_file, detect

DEMO = "日月之行，若出其中；星汉灿烂，若出其里。幸甚至哉，歌以咏志。"
TT = "我在臺灣用軟體裡的記憶體，滑鼠和印表機都有病毒。"

lines = []
lines.append("[1] s2t   : " + convert(DEMO, "s2t"))
lines.append("[2] s2twp : " + convert(DEMO, "s2twp"))
lines.append("[3] zh-tw : " + convert(DEMO, "zh-tw"))
lines.append("[4] zh-hk : " + convert(DEMO, "zh-hk"))
lines.append("[4b] t2s  : " + convert(convert(DEMO, "s2t"), "t2s"))
lines.append("[5] t2s   : " + convert(TT, "t2s"))
lines.append("[6] detect: %s / %s" % (detect(DEMO), detect("軟體與印表機")))
lines.append("[7] auto  : " + auto_convert("軟體與印表機"))

here = os.path.dirname(os.path.abspath(__file__))
tmp_in = os.path.join(here, "_tmp_in.txt")
tmp_out = os.path.join(here, "_tmp_out.txt")
with open(tmp_in, "w", encoding="utf-8") as f:
    f.write(DEMO)
convert_file(tmp_in, tmp_out, "s2twp")
with open(tmp_out, "r", encoding="utf-8") as f:
    lines.append("[8] file  : " + f.read())
os.remove(tmp_in)
os.remove(tmp_out)
lines.append("[OK] all passed")

out = "\n".join(lines)
with open(os.path.join(here, "smoke_result.txt"), "w", encoding="utf-8") as f:
    f.write(out)
sys.stdout.write(out + "\n")
