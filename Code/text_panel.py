from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QStackedWidget,
    QHeaderView,
    QTextEdit,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
)
from PyQt5.QtCore import Qt, QDir
import pyperclip
import os
import csv

from markup_parser import MarkupParser
from menu_box import MenuBox


class TextPanel(QWidget):
    # 构造函数
    def __init__(self):
        # 调用父类构造函数
        super().__init__()

        # 开始布局
        self.layout = QVBoxLayout(self)  # 总布局，纵向布局

        # 顶部控制栏
        self.up_control_layout = QHBoxLayout()  # 横向布局
        self.paste_translated_text_button = QPushButton("粘贴页面译文")
        self.create_page_button = QPushButton("添加新页面")  # 添加新页面按钮
        self.delete_page_button = QPushButton("删除最后一页")
        self.delete_button = QPushButton("删除文本组")  # 删除文本组按钮
        self.add_button = QPushButton("添加文本组")  # 添加文本组按钮
        self.copy_original_text_button = QPushButton("复制页面原文")  # 复制原文文本按钮
        self.copy_translated_text_button = QPushButton("复制页面译文")  # 复制译文按钮
        self.up_control_layout.addWidget(self.paste_translated_text_button)
        self.up_control_layout.addWidget(self.copy_original_text_button)
        self.up_control_layout.addWidget(self.copy_translated_text_button)
        self.up_control_layout.addWidget(self.delete_page_button)
        self.up_control_layout.addWidget(self.create_page_button)
        self.up_control_layout.addWidget(self.delete_button)
        self.up_control_layout.addWidget(self.add_button)
        # 添加布局
        self.layout.addLayout(self.up_control_layout)

        # 文本显示
        # 表格框
        self.table_panel = QTableWidget()
        self.table_panel.setColumnCount(3)
        self.table_panel.setHorizontalHeaderLabels(
            ["讲述人", "原文", "译文"]
        )  # 设置表头
        self.table_panel.setWordWrap(True)  # 设置自动换行
        self.table_panel.horizontalHeader().setSectionResizeMode(
            QHeaderView.Fixed
        )  # 设置列宽无法被用户更改
        self.table_panel.horizontalHeader().setSectionsClickable(False)
        self.table_panel.horizontalHeader().setSectionsMovable(False)
        # 文本框
        self.text_panel = QTextEdit()
        # 切换
        self.stack = QStackedWidget()
        self.stack.addWidget(self.table_panel)
        self.stack.addWidget(self.text_panel)
        self.layout.addWidget(self.stack)

        # 底部控制栏
        self.down_control_layout = QHBoxLayout()
        self.jump_page_number = QLineEdit(self)
        self.jump_page_number.setPlaceholderText("请输入页码")
        self.page_max_number = QLabel("总页数")
        self.jump_button = QPushButton("跳转")
        self.prev_button = QPushButton("上一页文本")  # 上一页文本
        self.next_button = QPushButton("下一页文本")  # 下一页文本
        self.down_control_layout.addWidget(self.jump_page_number, 5)
        self.down_control_layout.addWidget(
            self.page_max_number, 5, alignment=Qt.AlignCenter
        )
        self.down_control_layout.addWidget(self.jump_button, 10)
        self.down_control_layout.addWidget(self.prev_button, 40)
        self.down_control_layout.addWidget(self.next_button, 40)
        self.layout.addLayout(self.down_control_layout)

        # 其他数据成员
        self.current_text_path = None  # 当前文档地址
        self.text_is_mtm = False  # 当前文档是否为mtm文档
        self.parser = MarkupParser()  # 解析器
        self.menu_box = MenuBox()
        self.current_data = {}  # 当前数据
        self.current_page_number = -1  # 当前页面
        self.image_panel = None  # 隔壁的图片面板
        self.is_human_editing = True  # 是否处在人工修改阶段
        self.font_size = 10  # 字体大小
        self.default_speaker = "未知"  # 预设内容
        self.default_original_text = "原文"
        self.deafult_translated_text = "译文"

        # 关联
        self.parser.text_panel = self

        # 设置边框样式
        self.table_panel.setStyleSheet(
            "QTableWidget::item { border: 1px solid black; }"
        )

        # 绑定方法
        self.paste_translated_text_button.clicked.connect(self.paste_translated_text)
        self.copy_original_text_button.clicked.connect(self.copy_page_original_text)
        self.copy_translated_text_button.clicked.connect(self.copy_page_translated_text)
        self.jump_button.clicked.connect(self.jump_page)
        self.delete_page_button.clicked.connect(self.delete_last_page)
        self.create_page_button.clicked.connect(self.create_new_page)
        self.add_button.clicked.connect(self.add_text_group)
        self.delete_button.clicked.connect(self.delete_text_group)
        self.prev_button.clicked.connect(self.show_prev_page)
        self.next_button.clicked.connect(self.show_next_page)

        # 链接函数
        self.table_panel.itemChanged.connect(self.update_current_data)

        # 默认切换
        self.switch_text_panel()

    # 重设自身
    def reset_self(self):
        # 重设前保存
        self.save_text_file()
        self.current_text_path = None  # 当前文档地址
        self.text_is_mtm = False  # 当前文档是否为mtm文档
        self.current_data = {}  # 当前数据
        self.current_page_number = -1  # 当前页面

    # 获取默认文件位置
    def get_default_path(self):
        # 判断图片面板是否有文件目录列表
        if self.image_panel.image_path_list:
            # 若有，返回该文件列表0号位元素所在路径
            return os.path.dirname(self.image_panel.image_path_list[0])
        # 判断自身是否存在文件
        elif self.current_text_path:
            # 若有，返回自身路径
            return os.path.dirname(self.current_text_path)
        else:
            return QDir.homePath()

    # 新建文本文件
    def new_text_file(self):
        # 获取文件路径
        default_path = self.get_default_path()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "新建文本文件",
            default_path,
            "MTM Files (*.mtm);;Text Files (*.txt);;All Files(*)",
        )
        # 判断是否选中文件
        if file_path:
            # 如果有，获取路径文件，并创建页面内容列表与内容字符串
            folder_path = os.path.normpath(os.path.dirname(file_path))
            pages = []
            content = ""
            # 开始文件判断
            if self.judge_file_type(file_path):
                # 如果是MTM文件
                # 判断是否有图集
                if self.image_panel.judge_images_exist(folder_path):
                    # 如果有图集
                    # 打开图集
                    self.image_panel.open_image_folder_with_path(folder_path)

                    # 生成是否回答方法
                    def if_yes():
                        # 如果根据图片创建文档
                        pages.extend(
                            [
                                (i + 1, [("", "", "")])
                                for i in range(len(self.image_panel.image_path_list))
                            ]
                        )

                    def if_no():
                        # 如果不，创建单页文档
                        pages.extend([(1, [("", "", "")])])

                    # 询问是否要按照图集生成
                    self.menu_box.show_confirmation_dialog(
                        "询问",
                        "当前目录下存在图片文件，是否根据图片文件创建文档？",
                        if_yes,
                        if_no,
                    )
                else:
                    # 如果没有图集，则提示并生成单页数据
                    self.menu_box.show_message(
                        "提示", "当前文件夹下无图片数据，将生成单页MTM文档"
                    )
                    pages.extend[(1, [("", "", "")])]
                # 判定结束后生成内容
                content = self.parser.generate_document(pages)
            # 内容生成结束后，写入文件
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            # 打开文件
            self.open_text_file_with_path(file_path)

    # 判断文档类型
    def judge_file_type(self, file_path):
        if file_path:
            # 对文档类型进行判断
            if file_path.lower().endswith(".mtm"):
                # 如果是MTM文档，返回True
                return True
            else:
                # 如果不是，返回False
                return False

    # 打开文本文件
    def open_text_file(self):
        # 获取默认路径
        default_path = self.get_default_path()
        # 打开文件选框
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开文本文件",
            default_path,
            "MTM Files (*.mtm);;Text Files (*.txt);;All Files(*)",
        )
        # 判断有无选中
        if file_path:
            # 若有选中，打开文本文件，并进行后续操作
            self.open_text_file_with_path(file_path)
            # 获取路径
            folder_path = os.path.normpath(os.path.dirname(file_path))
            if self.image_panel.judge_images_exist(folder_path):
                # 如果有，创建是否函数，询问是否加载
                # 是
                def if_yes():
                    # 加载图集
                    self.image_panel.open_image_folder_with_path(folder_path)
                    # 若加载，简单判断页面数据与图片数据是否相符
                    if len(self.current_data) == len(self.image_panel.image_path_list):
                        # 若相符，则正常
                        return
                    else:
                        # 若不相同，则需要报信息
                        self.menu_box.show_message(
                            "提示",
                            "文档中页面数量与文件夹内图片数量不符，请注意不要开启了错误的文件",
                        )

                # 否
                def if_no():
                    # 不加载图集，并删除现有图集
                    self.image_panel.reset_self()
                    return

                # 询问是否要加载图集
                self.menu_box.show_confirmation_dialog(
                    "询问",
                    "是否加载图片文件？",
                    if_yes,
                    if_no,
                )

    # 打开文本文件，传入了路径的版本
    def open_text_file_with_path(self, file_path):
        # 打开前重设自身
        self.reset_self()
        # 检查是否有文件被选中
        if file_path:
            # 若有，加载
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
                self.load_text_data(text)
            # 设定软件内数据
            self.current_text_path = file_path

    # 加载文本数据
    def load_text_data(self, text):
        # 尝试对文本进行解析
        pages = self.parser.parse_doucument(text)
        # 检查解析结果
        if pages:
            # 若有结果，说明为mtm文本，切换UI并加载数据
            self.text_is_mtm = True
            self.switch_text_panel()
            self.current_data = {page_number: dialogs for page_number, dialogs in pages}
            # 设置页数为1
            self.current_page_number = 1
            self.jump_page_number.setText(str(self.current_page_number))
            # 设置总页数
            self.page_max_number.setText(str(len(self.current_data)))
            # 加载页面
            self.load_page(1)
        else:
            # 如果不是，以普通文本显示全部文本
            self.text_is_mtm = False
            self.switch_text_panel()
            self.text_panel.setPlainText(text)

    # 加载页面数据，提供页面序号，从自身数据中加载，并显示到文本页面，仅供列表界面使用
    def load_page(self, page_number):
        # 判断是否为mtm文件
        if not self.text_is_mtm:
            # 若不是，直接返回
            return

        # 开始加载
        self.is_human_editing = False
        if page_number in self.current_data:
            # 初始化行数
            self.table_panel.setRowCount(0)
            for (
                speaker,
                original_text,
                translated_text,
            ) in self.current_data[page_number]:
                # 每条文本组插入一条新行
                self.table_panel.insertRow(self.table_panel.rowCount())

                # 判断是否为预设
                if speaker == self.default_speaker:
                    speaker = ""
                if original_text == self.default_original_text:
                    original_text = ""
                if translated_text == self.deafult_translated_text:
                    translated_text = ""

                # 插入讲述人单元格
                speaker_item = QTableWidgetItem(speaker)
                speaker_item.setFlags(speaker_item.flags() | Qt.ItemIsEditable)
                speaker_item.setTextAlignment(Qt.AlignCenter)
                self.table_panel.setItem(
                    self.table_panel.rowCount() - 1, 0, speaker_item
                )

                # 插入原文单元格
                original_text_item = QTableWidgetItem(original_text)
                original_text_item.setFlags(
                    original_text_item.flags() | Qt.ItemIsEditable
                )
                original_text_item.setTextAlignment(Qt.AlignLeft)
                self.table_panel.setItem(
                    self.table_panel.rowCount() - 1, 1, original_text_item
                )

                # 插入译文单元格
                translated_text_item = QTableWidgetItem(translated_text)
                translated_text_item.setFlags(
                    translated_text_item.flags() | Qt.ItemIsEditable
                )
                translated_text_item.setTextAlignment(Qt.AlignLeft)
                self.table_panel.setItem(
                    self.table_panel.rowCount() - 1, 2, translated_text_item
                )
            # 加载结束后，更改当前页面序号
            self.current_page_number = page_number
            # 设置页数
            self.jump_page_number.setText(str(self.current_page_number))
        else:
            # 若当前页面不存在，则报出提示
            self.menu_box.show_message("提示", "目标页码不存在")
        self.is_human_editing = True

    # 更新数据
    def update_current_data(self):
        # 判断是否为mtm文件
        if not self.text_is_mtm:
            # 若不是，直接返回
            return

        # 当有内容发生更改时，判断是否由人工更改，如果是，则读取当前页面数据并覆写
        if self.is_human_editing:
            if self.current_page_number in self.current_data:
                self.current_data[self.current_page_number] = []
                # 遍历表格数据
                for row in range(self.table_panel.rowCount()):
                    # 获取Speaker
                    speaker_item = self.table_panel.item(row, 0)
                    speaker = speaker_item.text() if speaker_item else ""
                    # 获取OriginalText
                    original_text_item = self.table_panel.item(row, 1)
                    original_text = (
                        original_text_item.text() if original_text_item else ""
                    )
                    # 获取TranslatedText
                    translated_text_item = self.table_panel.item(row, 2)
                    translated_text = (
                        translated_text_item.text() if translated_text_item else ""
                    )
                    # 添加到页面内容中
                    self.current_data[self.current_page_number].append(
                        (speaker, original_text, translated_text)
                    )
        # 更改完成后自动设置行高
        self.table_panel.resizeRowsToContents()
        # 并写入文档
        self.save_text_file()

    # 显示某页文本
    def show_page(self, number):
        # 判断是否为mtm文件
        if not self.text_is_mtm:
            # 若不是，直接返回
            return

        # 确认当前是否有数据存在
        if self.current_data:
            # 若存在，更新当前页数索引
            self.current_page_number = number % len(self.current_data)
            if self.current_page_number == 0:
                self.current_page_number = len(self.current_data)
            # 加载索引
            self.load_page(self.current_page_number)
            # 切换页面时保存
            self.save_text_file()

    # 上一页文本
    def show_prev_page(self):
        # 判断是否为mtm文件
        if not self.text_is_mtm:
            # 若不是，直接返回
            return

        # 上一页
        self.show_page(self.current_page_number - 1)
        # 顺便更新隔壁图片内容
        self.image_panel.show_image(self.current_page_number - 1)

    # 下一页文本
    def show_next_page(self):
        # 判断是否为mtm文件
        if not self.text_is_mtm:
            # 若不是，直接返回
            return

        # 下一页
        self.show_page(self.current_page_number + 1)
        # 顺便更新隔壁图片内容
        self.image_panel.show_image(self.current_page_number - 1)

    # 新增文字组
    def add_text_group(self):
        # 判断是否为mtm文件
        if not self.text_is_mtm:
            # 若不是，直接返回
            return

        # 新建数据
        speaker = ""
        original_text = ""
        translated_text = ""
        # 添加到当前数据中
        self.current_data[self.current_page_number].append(
            (speaker, original_text, translated_text)
        )
        # 重载当前页面数据
        self.load_page(self.current_page_number)

    # 删除文字组
    def delete_text_group(self):
        # 判断是否为mtm文件
        if not self.text_is_mtm:
            # 若不是，直接返回
            return

        # 判断当前页面是否还有文本组
        if len(self.current_data[self.current_page_number]) == 0:
            # 如果文本组为空，则直接返回
            return

        # 删除最后一行数据
        del self.current_data[self.current_page_number][-1]
        # 重载当前页面
        self.load_page(self.current_page_number)

    # 新增页面
    def create_new_page(self):
        # 判断是否为mtm文件
        if not self.text_is_mtm:
            # 若不是，直接返回
            return

        # 获得新页面序号
        number = len(self.current_data) + 1
        # 创建新页面
        dialogs = [("", "", "")]
        # 添加新页面
        self.current_data[number] = dialogs
        # 更新总页数
        self.page_max_number.setText(str(len(self.current_data)))
        # 保存
        self.save_text_file()

    # 删除最后一个页面
    def delete_last_page(self):
        # 判断是否为mtm文件
        if not self.text_is_mtm:
            # 若不是，直接返回
            return

        # 判断当前页数
        if len(self.current_data) > 1:
            # 删除最后一页的数据
            self.current_data.popitem()
        # 更新总页数
        self.page_max_number.setText(str(len(self.current_data)))
        # 保存
        self.save_text_file()

    # 跳转
    def jump_page(self):
        # 获取目标页码
        aim_number = int(self.jump_page_number.text())

        # 跳转
        # 判断是否为mtm文件
        if not self.text_is_mtm:
            # 若不是，直接返回
            return
        self.show_page(aim_number)

        # 隔壁同理
        if not self.image_panel.image_path_list:
            return
        self.image_panel.show_image(aim_number - 1)

    # 保存数据到文件中
    def save_text_file(self):
        self.save_text_file_with_path(self.current_text_path)

    # 导出为
    def output_text_file(self, file_path):
        default_path = self.get_default_path()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "文本导出为",
            default_path,
            "MTM Files (*.mtm);;Text Files (*.txt);;CSV Files (*.csv);;All Files(*)",
        )
        self.save_text_file_with_path(file_path)

    # 保存数据到某个地方
    def save_text_file_with_path(self, file_path):
        # 判断是否存在文件
        if file_path:
            # 若存在，打开文件
            with open(file_path, "w", encoding="utf-8") as file:
                # 判断文本类型
                if self.text_is_mtm:
                    # 若是，读取所有页面
                    pages = [
                        (page_number, dialogs)
                        for page_number, dialogs in self.current_data.items()
                    ]
                    # 判断保存的文件的类型是否为CSV
                    if file_path.lower().endswith(".csv"):
                        # 若是，则遍历页面数据生成内容
                        writer = csv.writer(file)
                        # 表头
                        writer.writerow(
                            ["PageNumber", "Speaker", "OriginalText", "TranslatedText"]
                        )
                        # 内容
                        for page_number, dialogs in pages:
                            for dialog in dialogs:
                                speaker = dialog[0]
                                if not speaker:
                                    speaker = self.default_speaker
                                original_text = dialog[1]
                                if not original_text:
                                    original_text = self.default_original_text
                                translated_text = dialog[2]
                                if not translated_text:
                                    translated_text = self.deafult_translated_text
                                writer.writerow(
                                    [
                                        page_number,
                                        speaker,
                                        original_text,
                                        translated_text,
                                    ]
                                )
                    else:
                        # 若不是，调用解析器生成内容
                        content = self.parser.generate_document(pages)
                        # 写入内容
                        file.write(content)
                else:
                    # 如果不是，直接写入内容
                    text = self.text_panel.toPlainText()
                    file.write(text)

    # 复制页面原文
    def copy_page_original_text(self):
        # 判断文档是否为mtm
        if self.text_is_mtm:
            # 若是，则复制页面原文
            page_content = ""
            for speaker, original_text, translated_text in self.current_data[
                self.current_page_number
            ]:
                dialog_content = ""
                # 检测讲述人
                if speaker:
                    # 有讲述人，则添加讲述人到内容中
                    dialog_content = f"{speaker}:{original_text}"
                else:
                    # 若无讲述人
                    dialog_content = f"未知:{original_text}"
                # 添加到页面内容中
                page_content += dialog_content + "\n"
            # 添加到剪贴板
            pyperclip.copy(page_content)
        else:
            # 如果不是，则直接获取所有内容
            pyperclip.copy(self.text_panel.toPlainText())

    # 复制页面译文
    def copy_page_translated_text(self):
        # 判断文档是否为mtm
        if self.text_is_mtm:
            # 若是，则复制页面原文
            page_content = ""
            for speaker, original_text, translated_text in self.current_data[
                self.current_page_number
            ]:
                dialog_content = ""
                # 检测讲述人
                if speaker:
                    # 有讲述人，则添加讲述人到内容中
                    dialog_content = f"{speaker}:{translated_text}"
                else:
                    # 若无讲述人，则设置为“未知”
                    dialog_content = f"未知:{translated_text}"
                # 添加到页面内容中
                page_content += dialog_content + "\n"
            # 添加到剪贴板
            pyperclip.copy(page_content)
        else:
            # 如果不是，则直接获取所有内容
            pyperclip.copy(self.text_panel.toPlainText())

    # 粘贴页面译文
    def paste_translated_text(self):
        # 读取剪切板内容
        clipboard_content = pyperclip.paste()

        # 检测是否为MTM
        if not self.text_is_mtm:
            # 如果不是，直接粘贴并返回
            self.text_panel.append(clipboard_content)
            return

        # 去头去尾后按行区分
        original_lines = clipboard_content.strip().split("\n")
        lines = []
        # 对行进行处理以删去空行
        for line in original_lines:
            if line.strip():
                lines.append(line)
        # 处理每一行并给予到当前页面的数据部分
        for i in range(len(lines)):
            line = lines[i]
            content = ""
            # 判断是否包含讲述人
            if ":" in line:
                # 若包含，则取出内容
                content = line.split(":", 1)[1].strip()
            else:
                # 若不包含，则直接使用整行内容
                content = line.strip()
            # 获取内容后，获取当前对话
            if i < len(self.current_data[self.current_page_number]):
                dialog = self.current_data[self.current_page_number][i]
                new_dialog = (dialog[0], dialog[1], content)
                self.current_data[self.current_page_number][i] = new_dialog
        # 结束更新数据后重载页面
        self.load_page(self.current_page_number)

    # 增大字体大小
    def increase_font_size(self):
        self.font_size += 1
        self.update_font_size()

    # 减少字体大小
    def decrease_font_size(self):
        # 字体最小为1
        if self.font_size > 1:
            self.font_size -= 1
            self.update_font_size()

    # 更新表格界面字体大小
    def update_font_size(self):
        # 获取字体
        font = self.table_panel.font()
        # 设置字体大小
        font.setPointSize(self.font_size)
        # 设置字体
        self.table_panel.setFont(font)
        self.text_panel.setFont(font)
        # 重设行高
        self.table_panel.resizeRowsToContents()

    # 切换文本框
    def switch_text_panel(self):
        if self.text_is_mtm:
            self.stack.setCurrentWidget(self.table_panel)
            self.adjust_column_widths()
        else:
            self.stack.setCurrentWidget(self.text_panel)

    # 调整表格列宽
    def adjust_column_widths(self):
        # 总宽度，预留一段方便显示
        total_width = self.table_panel.viewport().width() - 25
        # 调整宽度为1:2:2
        self.table_panel.setColumnWidth(0, total_width // 5)
        self.table_panel.setColumnWidth(1, 2 * total_width // 5)
        self.table_panel.setColumnWidth(2, 2 * total_width // 5)

    # 当窗口大小改变时
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_column_widths()
