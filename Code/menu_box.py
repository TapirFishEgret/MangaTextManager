from PyQt5.QtWidgets import (
    QMessageBox,
    QInputDialog,
)


class MenuBox:
    # 生成信息框
    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    # 生成确认框
    def show_confirmation_dialog(self, title, message, yes_callback, no_callback):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        # 显示消息框并获取用户的选择
        reply = msg_box.exec_()

        # 根据用户的选择执行相应的回调
        if reply == QMessageBox.Yes:
            yes_callback()
        else:
            no_callback()

    # 生成文本输入框
    def show_text_input_dialog(self, title, label, default_text=""):
        text, ok = QInputDialog.getText(self, title, label, text=default_text)
        if ok and text:
            return text
        return None

    # 生成确认框随后生成文本输入框
    def show_confirmation_with_input(
        self, title, message, input_title, input_label, yes_callback, no_callback
    ):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        # 显示确认框并获取用户的选择
        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            # 若用户选择“是”，则弹出文本输入对话框
            user_input = self.show_text_input_dialog(input_title, input_label)
            if user_input:
                yes_callback(user_input)
            else:
                no_callback()
        else:
            no_callback()
