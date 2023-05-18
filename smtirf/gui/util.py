from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QPixmap


def make_messagebox(title, icon, message, buttons):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setIconPixmap(QPixmap(f":{icon}.svg").scaled(32, 32))
    msg.setText(message)
    msg.setStandardButtons(buttons)
    return msg


def confirm_click(title, message):
    def update(func):
        def wrapped_update():
            msg = make_messagebox(
                title,
                "question",
                message,
                (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel),
            )
            msg.exec()
            response = msg.buttonRole(msg.clickedButton())
            if response == QMessageBox.ButtonRole.YesRole:
                func()

        return wrapped_update

    return update
