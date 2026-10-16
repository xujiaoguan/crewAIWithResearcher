from crewai_tools import tool
import os
import re

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas


@tool("saveText2Pdf")
def saveText2Pdf(text: str, filename: str = "report.pdf") -> str:
	"""
	使用这个工具来保存任务输出为PDF文件，支持中文。
	:param text: 要保存的文本内容
	:param filename: 保存的PDF文件名
	:return: 保存状态消息
	"""
	# 输出目录
	out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
	out_dir = os.path.abspath(out_dir)
	os.makedirs(out_dir, exist_ok=True)

	# 统一输出文件名：确保是 .pdf，且不允许路径穿越
	safe_name = os.path.basename(filename or "report.pdf")
	if not safe_name.lower().endswith(".pdf"):
		safe_name = re.sub(r"\.[^.\s]+$", "", safe_name) + ".pdf"
	if safe_name.strip() in (".pdf", ""):
		safe_name = "report.pdf"

	pdf_path = os.path.join(out_dir, safe_name)

	# 注册中文字体（CID 字体，不需要额外 ttf 文件；生成的是“可选中复制”的文字）
	try:
		pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
	except Exception:
		# 多次注册/某些环境下可能报错，忽略即可
		pass

	c = canvas.Canvas(pdf_path, pagesize=A4)
	width, height = A4

	left = 48
	right = 48
	top = 56
	bottom = 56
	max_width = width - left - right

	# 标题（与本科毕业论文体例专题报告一致；正文仍来自模型输出）
	c.setFont("STSong-Light", 16)
	c.drawString(left, height - top, "本科生毕业论文体例专题报告")
	c.setFont("STSong-Light", 10)
	c.drawString(left, height - top - 18, "（Markdown 排版稿的 PDF 导出，表格与公式以纯文本呈现）")

	# 正文：简单自动换行（按字符估算宽度，兼容中英文混排）
	c.setFont("STSong-Light", 11)
	y = height - top - 44
	line_height = 16

	def split_lines(s: str):
		s = (s or "").replace("\r\n", "\n").replace("\r", "\n")
		for para in s.split("\n"):
			if para.strip() == "":
				yield ""
				continue
			buf = ""
			for ch in para:
				# 估算宽度：英文更窄、中文更宽
				est = 6 if ord(ch) < 128 else 11
				cur = sum((6 if ord(cc) < 128 else 11) for cc in buf)
				if cur + est > max_width and buf:
					yield buf
					buf = ch
				else:
					buf += ch
			if buf:
				yield buf

	for line in split_lines(text):
		if y <= bottom:
			c.showPage()
			c.setFont("STSong-Light", 11)
			y = height - top
		c.drawString(left, y, line)
		y -= line_height

	c.save()
	return f"PDF 已生成：{pdf_path}"

