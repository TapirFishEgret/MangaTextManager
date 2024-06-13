from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QScrollArea,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
)
from PyQt5.QtGui import QPixmap, QMouseEvent
from PyQt5.QtCore import Qt, QDir, QPoint, QEvent
from menu_box import MenuBox
import re
import os


class ImagePanel(QWidget):
    # 构造函数
    def __init__(self):
        # 调用父类构造函数
        super().__init__()

        # 开始调整布局
        self.layout = QVBoxLayout(self)  # 整体为垂直布局

        # 添加顶部控制栏
        self.up_control_layout = QHBoxLayout()  # 控制栏自身为横向布局
        # 添加图片名称标签
        self.image_name_lable = QLabel("图片名称")  # 图片名称标签
        self.image_name_lable.setAlignment(Qt.AlignCenter)
        # 设置
        self.up_control_layout.addWidget(self.image_name_lable)
        # 添加控制栏到总布局中
        self.layout.addLayout(self.up_control_layout)

        # 添加图片面板
        self.scroll_area = QScrollArea()
        self.image_label = QLabel()
        # 图片居中
        self.image_label.setAlignment(Qt.AlignCenter)
        # 将图片放入滚动面板中
        self.scroll_area.setWidget(self.image_label)
        # 允许面板缩放
        self.scroll_area.setWidgetResizable(True)
        # 添加图片面板到总布局中
        self.layout.addWidget(self.scroll_area)

        # 添加底部控制栏
        self.down_control_layout = QHBoxLayout()
        # 添加操作按钮
        self.prev_button = QPushButton("上一张图片")  # 显示上一张图片
        self.next_button = QPushButton("下一张图片")  # 显示下一张图片
        # 添加跳页控制
        self.jump_image_number = QLineEdit(self)
        self.jump_image_number.setPlaceholderText("请输入页码")
        self.image_max_number = QLabel("总页数")
        self.jump_button = QPushButton("跳转")
        # 设置控制栏布局
        self.down_control_layout.addWidget(self.jump_image_number)
        self.down_control_layout.addWidget(
            self.image_max_number, alignment=Qt.AlignCenter
        )
        self.down_control_layout.addWidget(self.jump_button)
        self.down_control_layout.addWidget(self.prev_button)
        self.down_control_layout.addWidget(self.next_button)
        # 添加布局
        self.layout.addLayout(self.down_control_layout)

        # 其他数据成员
        self.image = None  # 图片文件
        self.scale_factor = 1.0  # 缩放比例
        self.image_path_list = []  # 图片文件路径列表
        self.current_image_index = -1  # 当前图片索引
        self.menu_box = MenuBox()  # 信息盒子
        self.text_panel = None  # 隔壁的图片面板

        # 鼠标拖拽相关
        self.last_mouse_pos = QPoint()
        self.is_dragging = False

        # 绑定事件
        self.image_label.installEventFilter(self)  # 安装事件过滤器
        self.scroll_area.viewport().installEventFilter(self)  # 安装事件过滤器
        self.jump_button.clicked.connect(self.jump_to_image)
        self.prev_button.clicked.connect(self.show_prev_image)  # 绑定信号与信号槽
        self.next_button.clicked.connect(self.show_next_image)  # 绑定信号与信号槽

    # 其他函数
    # 获取默认文件位置
    def get_default_path(self):
        # 判断文本面板是否有选中
        if self.text_panel.current_text_path:
            # 若有，返回该文件所在路径
            return os.path.dirname(self.text_panel.current_text_path)
        # 判断自身有没有
        if self.image_path_list:
            # 若有，返回0号位
            return os.path.dirname(self.image_path_list[0])
        else:
            return QDir.homePath()

    # 更新图片大小
    def update_image(self):
        # 判断图片文件是否存在
        if self.image:
            # 若存在，根据当前scale_factor缩放
            scaled_image = self.image.scaled(
                self.image.size() * self.scale_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            # 缩放完成后显示
            self.image_label.setPixmap(scaled_image)
            self.image_label.adjustSize()

    # 打开图集
    def open_image_folder(self):
        # 获取目标文件夹
        default_path = self.get_default_path()
        folder_path = QFileDialog.getExistingDirectory(
            self, "选择图片文件夹", default_path
        )
        self.open_image_folder_with_path(folder_path)

    # 打开图集，但是需要提供路径
    def open_image_folder_with_path(self, folder_path):
        # 对目标文件夹进行判断
        if folder_path:
            # 获取目标文件夹下所有图片文件
            self.image_path_list = [
                os.path.normpath(os.path.join(folder_path, f))
                for f in os.listdir(folder_path)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))
            ]

            # 对图片文件进行排序
            # 自定义排序方法
            def extract_numbers(file_name):
                # 提取文件名称中的所有数字，并转化为整数
                numbers = re.findall(r"\d+", file_name)
                return [int(num) for num in numbers]

            # 排序
            self.image_path_list.sort(
                key=lambda f: extract_numbers(os.path.basename(f))
            )

            # 检测是否成功获取图片文件路径列表
            if self.image_path_list:
                # 若成功获取，设置各项参数
                self.image_max_number.setText(str(len(self.image_path_list)))
                self.show_image(0)

                # 并检测目录下是否存在mtm后缀的文件
                text_file_path_list = [
                    os.path.normpath(os.path.join(folder_path, f))
                    for f in os.listdir(folder_path)
                    if f.lower().endswith(".mtm")
                ]
                # 判断数量
                if len(text_file_path_list) == 1:
                    # 若存在且只存在一个，则读取
                    text_file_path = text_file_path_list[0]
                    if os.path.exists(text_file_path):
                        self.text_panel.open_text_file_with_path(text_file_path)
                        return
                elif len(text_file_path_list) == 0:
                    # 若不存在，弹出信息，随后读取
                    self.menu_box.show_message("提示", "当前目录下无文档文件，请创建")
                    self.text_panel.new_text_file()
                    return
                else:
                    # 若存在多个文档，输出信息
                    self.menu_box.show_message(
                        "提示", "路径下存在多个文档文件，请保留其一"
                    )
            else:
                # 若没有图片文件，输出一条信息
                self.menu_box.show_message("提示", "路径下没有图片文件")

    # 加载图片
    def load_image(self, file_path):
        # 判断路径是否存在
        if os.path.exists(file_path):
            # 若存在，读取
            self.image = QPixmap(file_path)

            # 计算缩放比例
            # 获取面板大小
            panel_width = self.scroll_area.viewport().width()
            panel_height = self.scroll_area.viewport().height()
            # 获取图片原始长宽
            original_width = self.image.width()
            original_height = self.image.height()
            # 计算长宽缩放比例
            scale_width = panel_width / original_width
            scale_height = panel_height / original_height
            # 选取缩放比例更小的，作为真正缩放比例
            self.scale_factor = min(scale_width, scale_height)

            # 自动缩放图片适应面板大小
            if not self.image.isNull():
                self.update_image()

            # 更改图片名称显示
            self.image_name_lable.setText(os.path.basename(file_path))

    # 切换至某张图片
    def show_image(self, index):
        # 判断图片文件路径列表是否存在
        if self.image_path_list:
            # 若存在，获取索引
            self.current_image_index = index % len(self.image_path_list)
            # 随后加载
            self.load_image(self.image_path_list[self.current_image_index])
            # 顺便更改当前页数的值
            self.jump_image_number.setText(str(self.current_image_index + 1))

    # 切换至前一张图片
    def show_prev_image(self):
        # 判断图片文件路径列表是否存在
        if not self.image_path_list:
            # 若不存在，返回
            return
        # 加载上一张
        self.show_image(self.current_image_index - 1)
        # 顺便更新隔壁文本内容
        self.text_panel.show_page(self.current_image_index + 1)

    # 切换至下一张图片
    def show_next_image(self):
        # 判断图片文件路径列表是否存在
        if not self.image_path_list:
            # 若不存在，返回
            return
        # 加载下一张
        self.show_image(self.current_image_index + 1)
        # 顺便更新隔壁文本内容
        self.text_panel.show_page(self.current_image_index + 1)

    # 跳转至某张图片
    def jump_to_image(self):
        # 获取目标页码
        aim_number = int(self.jump_image_number.text())

        # 跳转
        # 判断图片文件路径列表是否存在
        if not self.image_path_list:
            # 若不存在，返回
            return
        self.show_image(aim_number - 1)

        # 隔壁同理
        # 判断隔壁文件是否为mtm
        if not self.text_panel.text_is_mtm:
            # 若不是，同样返回
            return
        self.text_panel.show_page(aim_number)

    # 拖拽处理
    # 处理鼠标按下事件
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.last_mouse_pos = event.pos()

    # 处理鼠标移动事件
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_dragging:
            delta = event.pos() - self.last_mouse_pos
            self.scroll_area.horizontalScrollBar().setValue(
                self.scroll_area.horizontalScrollBar().value() - delta.x()
            )
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().value() - delta.y()
            )
            self.last_mouse_pos = event.pos()

    # 处理鼠标释放事件
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    # 滚轮控制缩放处理
    def eventFilter(self, source, event):
        # 处理滚轮事件
        if event.type() == QEvent.Wheel:
            # 确定为滚轮事件后进行缩放
            if event.angleDelta().y() > 0:
                self.scale_factor *= 1.1
            else:
                self.scale_factor *= 0.9
            self.update_image()
            # 缩放结束后返回，表示事件已经处理，不再传递，方式滚轮顺便控制了滚轴移动
            return True
        return super().eventFilter(source, event)
