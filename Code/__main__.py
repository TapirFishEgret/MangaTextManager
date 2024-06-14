from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QSplitter,
    QAction,
    QFontComboBox,
)
from PyQt5.QtCore import Qt
from text_panel import TextPanel
from image_panel import ImagePanel
import sys


class MangaTextManager(QMainWindow):
    # 构造函数
    def __init__(self):
        # 父类构造函数
        super().__init__()

        # 程序自身
        self.app = None

        # 窗口设置
        self.setWindowTitle("Manga Text Manager")
        self.setGeometry(100, 100, 1280, 720)
        self.text_panel = TextPanel()
        self.image_panel = ImagePanel()
        self.text_panel.image_panel = self.image_panel  # 互相关联一下
        self.image_panel.text_panel = self.text_panel  # 互相关联一下

        # 分割框的设置
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.text_panel)
        self.splitter.addWidget(self.image_panel)
        self.splitter.setSizes([self.width() // 2, self.width() // 2])

        # 内容物的设置
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.splitter)
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 菜单项，打开图集
        self.open_image_folder_action = QAction("打开图集", self)
        self.open_image_folder_action.triggered.connect(
            self.image_panel.open_image_folder
        )
        self.menuBar().addAction(self.open_image_folder_action)
        # 菜单项，新建文本
        self.new_text_action = QAction("新建文本", self)
        self.new_text_action.triggered.connect(self.text_panel.new_text_file)
        self.menuBar().addAction(self.new_text_action)
        # 菜单项，打开文本
        self.open_text_action = QAction("打开文本", self)
        self.open_text_action.triggered.connect(self.text_panel.open_text_file)
        self.menuBar().addAction(self.open_text_action)
        # 菜单项，保存文本
        self.save_text_action = QAction("保存文本", self)
        self.save_text_action.triggered.connect(self.text_panel.save_text_file)
        self.menuBar().addAction(self.save_text_action)
        # 菜单项，导出文本
        self.output_text_action = QAction("导出文本", self)
        self.output_text_action.triggered.connect(self.text_panel.output_text_file)
        self.menuBar().addAction(self.output_text_action)
        # 菜单项，开关图片显示
        self.toggle_image_panel_action = QAction("开关图片显示", self)
        self.toggle_image_panel_action.triggered.connect(self.toggle_image_panel)
        self.menuBar().addAction(self.toggle_image_panel_action)
        # 菜单项，增大字号
        self.increase_font_size_action = QAction("增大字号", self)
        self.increase_font_size_action.triggered.connect(
            self.text_panel.increase_font_size
        )
        self.menuBar().addAction(self.increase_font_size_action)
        # 菜单项，减小字号
        self.decrease_font_size_action = QAction("减小字号", self)
        self.decrease_font_size_action.triggered.connect(
            self.text_panel.decrease_font_size
        )
        self.menuBar().addAction(self.decrease_font_size_action)
        # 菜单项，更换字体
        self.font_combo_box = QFontComboBox(self)
        self.font_combo_box.currentFontChanged.connect(self.change_font)
        self.menuBar().setCornerWidget(self.font_combo_box, Qt.TopRightCorner)

    # 更换字体方法
    def change_font(self, font):
        # 使用全局样式表来更改整个应用程序的字体
        QApplication.instance().setFont(font)
        # 顺便更新一下文本面板字体
        self.text_panel.update_font_size()

    # 开关图片面板显示方法
    def toggle_image_panel(self):
        # 检测当前显示与否
        if self.image_panel.isVisible():
            # 若显示，则关闭
            self.image_panel.hide()
            # 调整分割框
            self.splitter.setSizes([self.width(), 0])
        else:
            # 若不显示，则开启
            self.image_panel.show()
            # 调整分割框
            self.splitter.setSizes([self.width() // 2, self.width() // 2])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = MangaTextManager()
    manager.show()
    manager.text_panel.adjust_column_widths()  # 手动调整一次文本面板列宽
    manager.app = app
    sys.exit(app.exec_())
