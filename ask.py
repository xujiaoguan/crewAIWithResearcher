import argparse
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from crew import CrewtestprojectCrew

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))


def build_model(model_type: str):
    if model_type == "oneapi":
        oneapi_key = os.getenv("ONEAPI_CHAT_API_KEY", "")
        if not oneapi_key:
            raise SystemExit("缺少环境变量 ONEAPI_CHAT_API_KEY（用于 OneAPI 调用）。请先设置后再运行。")
        return ChatOpenAI(
            base_url=os.getenv("ONEAPI_API_BASE", "http://localhost:3000/v1"),
            # langchain_openai 期望的 key 参数名
            openai_api_key=oneapi_key,
            model=os.getenv("ONEAPI_CHAT_MODEL", "qwen-max-latest"),
        )
    if model_type == "ollama":
        ollama_key = os.getenv("OLLAMA_CHAT_API_KEY", "ollama")
        if not ollama_key:
            raise SystemExit("缺少环境变量 OLLAMA_CHAT_API_KEY（用于 Ollama 调用）。请先设置后再运行。")
        return ChatOpenAI(
            base_url=os.getenv("OLLAMA_API_BASE", "http://localhost:11434/v1"),
            openai_api_key=ollama_key,
            model=os.getenv("OLLAMA_CHAT_MODEL", "llama3.1:latest"),
        )
    # openai
    openai_key = os.getenv("OPENAI_CHAT_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    if not openai_key:
        raise SystemExit("缺少环境变量 OPENAI_API_KEY（或 OPENAI_CHAT_API_KEY）。请先设置后再运行。")
    return ChatOpenAI(
        base_url=os.getenv("OPENAI_API_BASE", ""),
        openai_api_key=openai_key,
        model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
    )


def main():
    parser = argparse.ArgumentParser(description="交互式提问并生成 PDF 报告到 output/report.pdf")
    parser.add_argument("--model-type", default=os.getenv("MODEL_TYPE", "oneapi"), choices=["oneapi", "ollama", "openai"])
    parser.add_argument("--topic", default="", help="直接指定问题/主题；不填则进入交互输入")
    args = parser.parse_args()

    topic = (args.topic or "").strip()
    if not topic:
        try:
            topic = input("请输入你的问题/主题 > ").strip()
        except (EOFError, KeyboardInterrupt):
            topic = ""

    if not topic:
        raise SystemExit("未输入问题，已退出。")

    model = build_model(args.model_type)
    result = CrewtestprojectCrew(model).crew().kickoff(inputs={"topic": topic})
    print(str(result))
    print(
        "已生成文件：output/research_notes.md（调研笔记）、output/report.md（论文体例 Markdown）"
        " 与 output/report.pdf（PDF 导出）。"
        " 若需可核验的参考文献 URL，请在环境中设置 SERPER_API_KEY（https://serper.dev）。"
    )


if __name__ == "__main__":
    main()

