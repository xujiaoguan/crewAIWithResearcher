import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.custom_tool import saveText2Pdf


if __name__ == "__main__":
    # crewai_tools 的 @tool 会把函数包装成 Tool 对象，直接用 .run 调用
    print(saveText2Pdf.run("中文测试：你好\n第二行 English test", filename="report.pdf"))

