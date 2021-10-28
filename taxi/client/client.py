import sys
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTabWidget, QListWidget, \
    QListWidgetItem, QDialog, QFormLayout, QLineEdit, QDateTimeEdit, QTextEdit, QComboBox

from server_connector import ServerConnector


class Settings(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Настройки")
        self.setLayout(QFormLayout())

        self.is_accepted = False

        self.age = QLineEdit()
        self.layout().addRow("Сколько вам лет: ", self.age)

        self.type_client = QLineEdit()
        self.layout().addRow("Какой тип водителя или клиета нравится: ", self.type_client)

        self.type_taxi = QComboBox()
        self.type_taxi.addItems(["luxe", "medium", "bomj"])
        self.layout().addRow("какой тип предпочитаете: ", self.type_taxi)

        self.adres = QLineEdit()
        self.layout().addRow("адрес дома: ", self.adres)

        accept_button = QPushButton("OK")
        accept_button.clicked.connect(self.confirm)
        self.layout().addRow("Принять", accept_button)

    def confirm(self):
        self.is_accepted = True
        self.close()

    @property
    def get_age(self):
        return self.age

    @property
    def get_type_client(self):
        return self.type_client

    @property
    def get_type_taxi(self):
        return self.type_taxi

    @property
    def get_adres(self):
        return self.adres



class AuthDialog(QDialog):

    def __init__(self, server: ServerConnector):
        super().__init__()
        self.server = server

        self.is_accepted = False

        self.setWindowTitle("Авторизация")
        self.setLayout(QFormLayout())

        setting_button = QPushButton("указать")
        setting_button.clicked.connect(self.open_settings)
        self.layout().addRow("информация о вас", setting_button)

        self.client = QComboBox()
        self.client.addItems(["driver", "operator"])
        self.layout().addRow("выберите", self.client)

        self.login_field = QLineEdit()
        self.layout().addRow("Логин: ", self.login_field)

        accept_button = QPushButton("OK")
        accept_button.clicked.connect(self.confirm)
        self.layout().addRow("Войти", accept_button)

    def confirm(self):
        global client
        self.is_accepted = True
        self.server.set_user(self.login_field.text())
        if self.client.currentText() == "driver":
            client = MainWindowDriver
        else:
            client = MainWindowOperator
        self.close()

    def open_settings(self):
        info = {}
        setting_dialog = Settings()
        setting_dialog.exec()
        if setting_dialog.is_accepted:
            info["age"] = setting_dialog.get_age
            info["type_client"] = setting_dialog.get_type_client
            info["type_taxi"] = setting_dialog.get_type_taxi
            info["adres"] = setting_dialog.get_adres


class TaskWindow(QDialog):

    def __init__(self, data, server: ServerConnector, driver=False):
        super().__init__()
        self.server = server
        self.id = data["id"]
        self.driver = driver

        self.setWindowTitle(f"{data['address_from']} - {data['address_to']}")
        self.resize(300, 300)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel(f"Откуда: {data['address_from']}"))
        self.layout().addWidget(QLabel(f"Куда: {data['address_to']}"))
        self.layout().addWidget(QLabel(f"Телефон: {data['phone']}"))
        start_time = datetime.fromtimestamp(data["time"]).strftime("%Y-%m-%d %H:%M")
        self.layout().addWidget(QLabel(f"Время: {start_time}"))
        self.layout().addWidget(QLabel(f"Комментарий к заказу:\n{data['comment']}"))
        if driver:
            if data in server.get_free_tasks():
                take_button = QPushButton("Взять в работу")
                take_button.clicked.connect(self.take)
                self.layout().addWidget(take_button)
            else:
                complete_button = QPushButton("Завершить")
                complete_button.clicked.connect(self.complete)
                self.layout().addWidget(complete_button)

    def take(self):
        self.server.take_task(self.id)
        self.close()

    def complete(self):
        self.server.complete_task(self.id)
        self.close()


class TaskListItem(QListWidgetItem):

    def __init__(self, task_dict):
        super().__init__()
        self.id = task_dict["id"]
        self.data = task_dict
        self.setText(
            f"{task_dict['address_from']} - {task_dict['address_to']}\n"
            f"{task_dict['comment']}"
        )

class TasksPanel(QTabWidget):

    def __init__(self, get_free_tasks, get_user_task, server, driver=False):
        super().__init__()
        self.server = server
        self.driver = driver

        self.get_free_tasks = get_free_tasks
        self.get_user_tasks = get_user_task

        self.free_tasks_widget = QListWidget()
        self.free_tasks_widget.itemDoubleClicked.connect(self.open_task_window)
        self.addTab(self.free_tasks_widget, "Свободные заявки")

        if self.driver:
            self.my_tasks_widget = QListWidget()
            self.my_tasks_widget.itemDoubleClicked.connect(self.open_task_window)
            self.addTab(self.my_tasks_widget, "Мои заявки")

        self.update_data()

    def update_data(self):
        self.free_tasks_widget.clear()
        for task in self.get_free_tasks():
            self.free_tasks_widget.addItem(TaskListItem(task))
        if self.driver:
            self.my_tasks_widget.clear()
            for task in self.get_user_tasks():
                self.my_tasks_widget.addItem(TaskListItem(task))

    def open_task_window(self):
        window = TaskWindow(self.sender().selectedItems()[0].data, self.server,
                            driver=self.driver)
        window.exec()


class NewTaskDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.is_accepted = False

        self.setWindowTitle("Новая заявка")
        self.setLayout(QFormLayout())

        self.address_from_field = QLineEdit()
        self.layout().addRow("Откуда: ", self.address_from_field)

        self.address_to_field = QLineEdit()
        self.layout().addRow("Куда: ", self.address_to_field)

        self.phone_field = QLineEdit()
        self.layout().addRow("Телефон: ", self.phone_field)

        self.time_field = QDateTimeEdit()
        self.layout().addRow("Время: ", self.time_field)

        self.comment_field = QTextEdit()
        self.layout().addRow("Комментарий к заказу", self.comment_field)

        accept_button = QPushButton("OK")
        accept_button.clicked.connect(self.confirm)
        self.layout().addRow("Принять", accept_button)

    def confirm(self):
        self.is_accepted = True
        self.close()

    @property
    def address_from(self):
        return self.address_from_field.text()

    @property
    def address_to(self):
        return self.address_to_field.text()

    @property
    def phone(self):
        return self.phone_field.text()

    @property
    def time(self):
        return self.time_field.dateTime().toSecsSinceEpoch()

    @property
    def comment(self):
        return self.comment_field.toPlainText()


class MainWindow(QWidget):

    def __init__(self, server: ServerConnector):
        super().__init__()
        self.server = server
        self.setWindowTitle("Программа обработки заявок")
        self.setGeometry(400, 100, 600, 800)
        self.setLayout(QVBoxLayout())

        self.create_task_panel()
        self.server.add_view(self.tasks_panel)
        self.layout().addWidget(self.tasks_panel)


        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.refresh)
        self.layout().addWidget(refresh_button)



    def show_status(self, status_message):
        self.status_bar.setText(status_message)

    def create_task_panel(self):
        self.tasks_panel = TasksPanel(self.server.get_free_tasks,
                                      self.server.get_task_for_driver, self.server)

    def refresh(self):
        self.tasks_panel.update_data()


class MainWindowOperator(MainWindow):
    def __init__(self, server: ServerConnector):
        super().__init__(server)
        self.set_add_button()

    def set_add_button(self):
        add_task_button = QPushButton("Добавить заявку", self)
        add_task_button.clicked.connect(self.add_task)
        self.layout().addWidget(add_task_button)

    def add_task(self):
        adding_dialog = NewTaskDialog()
        adding_dialog.exec()
        if adding_dialog.is_accepted:
            self.server.add_task(adding_dialog.address_from,
                                 adding_dialog.address_to,
                                 adding_dialog.phone,
                                 adding_dialog.time,
                                 adding_dialog.comment)


class MainWindowDriver(MainWindow):
    def create_task_panel(self):
        self.tasks_panel = TasksPanel(self.server.get_free_tasks,
                                      self.server.get_task_for_driver, self.server,
                                      driver=True)







if __name__ == '__main__':
    client = MainWindow
    app = QApplication(sys.argv)
    connector = ServerConnector("http://127.0.0.1", 5000)
    auth_window = AuthDialog(connector)
    auth_window.exec()
    window = client(connector)
    window.show()
    sys.exit(app.exec())
