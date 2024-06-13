import re


# 标记分析器
# 文档标记，由软件自身创建的适用于漫画对话管理的文本文档的标记，仅会存在一个：<MangaTextManager>内容物</MangaTextManager>
# 页面标记，用于标记每页文本内容的标记：<PageXXX>内容物</PageXXX>
# 文本组标记，用于标记每句文本内容的标记：<DialogXXX Speaker = "">内容物</DialogXXX Speaker = "">
class MarkupParser:
    def __init__(self):
        # 正则表达式，查找所有文档标记
        # 捕获为内容物
        self.document_pattern = re.compile(
            r"<MangaTextManager>(.*?)</MangaTextManager>",
            re.DOTALL,
        )
        # 正则表达式，查找所有页面标记
        # 捕获第一个组为页码，第二个组为内容物
        self.page_pattern = re.compile(r"<Page(\d+)>(.*?)</Page\1>", re.DOTALL)
        # 正则表达式，查找所有文本组标记
        # 捕获第一个组为页码，第二个组为讲述者，第三个组为内容物
        self.dialog_pattern = re.compile(
            r'<Dialog Speaker="([^""]*)">(.*?)</Dialog>', re.DOTALL
        )

    # 分析文档标记
    def parse_doucument(self, text):
        # 获取匹配
        match = self.document_pattern.search(text)
        if match:
            # 若匹配成功，则获取项目名称与内容物，并传递到分析页面标记中
            content = match.group(1)
            return self.parse_pages(content)
        else:
            return

    # 分析页面标记
    def parse_pages(self, text):
        # 页面列表，用于暂时存储
        pages = []
        # 针对每一个匹配进行操作
        for match in self.page_pattern.finditer(text):
            # 获取页码，即第一个组的值
            page_number = int(match.group(1))
            # 获取内容，第二个组的值
            content = match.group(2)
            # 将获取到的内容传递给文本组分析函数，获取到文本组
            dialogs = self.parse_dialogs(content)
            # 将页码和文本组组合为元组并添加到列表中
            pages.append((page_number, dialogs))
        # 返回页面列表
        return pages

    # 分析文本组标记
    def parse_dialogs(self, text):
        # 文本组列表，用于暂时存储
        dialogs = []
        # 针对每一个匹配进行操作
        for match in self.dialog_pattern.finditer(text):
            # 获取讲述人
            speaker = match.group(1).strip()
            # 获取具体文本，以换行符为分隔符拆分为列表
            content = match.group(2).strip().split("\n")
            # 正常情况下一个文本组应该包括两个文本，分别是原文本与翻译文本
            if len(content) == 2:
                original_text, translated_text = content
            # 若非正常状况，则只获取原文本，不做错误捕获处理
            else:
                original_text, translated_text = content[0], ""
            # 将获取的信息整合为元组添加到文本组列表中，包括文本组序号、讲述人、原文、译文
            dialogs.append(
                (
                    speaker,
                    original_text.strip(),
                    translated_text.strip(),
                )
            )
        return dialogs

    # 生成文档
    def generate_document(self, pages):
        # 生成文档文本
        content = "\n".join(
            [self.generate_page(page_number, dialogs) for page_number, dialogs in pages]
        )
        # 返回格式化后的文档文本
        return f"<MangaTextManager>\n{content}\n</MangaTextManager>"

    # 生成页面
    def generate_page(self, page_number, dialogs):
        # 生成页面文本
        content = "\n".join(
            [
                self.generate_dialog(speaker, original_text, translated_text)
                for speaker, original_text, translated_text in dialogs
            ]
        )
        # 返回格式化后的页面文本
        return f"\t<Page{page_number:03}>\n{content}\n\t</Page{page_number:03}>"

    # 生成对话组
    def generate_dialog(self, speaker, original_text, translated_text):
        # 返回格式化后的对话组文本
        return f'\t\t<Dialog Speaker="{speaker}">\n\t\t\t{original_text}\t\t\t\n\t\t\t{translated_text}\t\t\t\n\t\t</Dialog>'
