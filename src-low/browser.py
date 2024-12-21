import sys
import os
import configparser
import requests
import datetime
import random
import zipfile
import subprocess
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication, QProgressBar, QInputDialog, QMainWindow, QHBoxLayout, QWidget, QLineEdit, QToolBar, QAction, QTabWidget, QMessageBox, QStyleOptionTab, QStyle, QTabBar, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon, QPainter, QPalette, QColor, QPixmap
from PyQt5 import QtCore
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import ctypes

#Параметры
safe_mode = 0 #Безопасный режим
anonymus = 0 #Режим инкогнито

def is_user_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None, user_os="Windows"):
        super(CustomWebEnginePage, self).__init__(parent)
        self.browser_window = parent

        # Формируем User-Agent с названием браузера WaterWolf и операционной системой
        user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"

        # Устанавливаем кастомный User-Agent
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setHttpUserAgent(user_agent)
        self.loadFinished.connect(self.handle_load_finished)

    def createWindow(self, window_type):
        new_page = CustomWebEnginePage(self.browser_window)
        new_tab = QWebEngineView()
        new_tab.setPage(new_page)

        # Добавление новой вкладки с кастомными кнопками
        self.browser_window.add_new_tab_widget(new_tab, "New Tab")

        # Подключаем сигналы для обновления заголовка и иконки
        new_tab.titleChanged.connect(lambda title: self.browser_window.update_tab_title(title, new_tab))
        new_tab.iconChanged.connect(lambda icon: self.browser_window.update_tab_icon(icon, new_tab))

        return new_page

    def handle_load_finished(self, success):
        if success:  # Если страница успешно загрузилась
            current_url = self.url().toString()
            self.save_history(current_url)
            if safe_mode == 1:
                if self.is_site_blocked(current_url):
                    self.setHtml(self.custom_blocked_page())
                else:
                    self.save_history(current_url)
        # Убираем else здесь, чтобы страница не отображала ошибку при любом сбое

    def custom_error_page(self):
        return """
        <html>
        <head><title>Ошибка загрузки</title></head>
        <body>
        <h1>Страница не найдена</h1>
        <p>К сожалению, произошла ошибка при загрузке страницы.</p>
        </body>
        </html>
        """

    def save_history(self, url):
        if anonymus == 0:
            if is_user_admin():
                history_dir = os.path.join(sys.path[0], '..', '..', 'history.txt')
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(history_dir, 'a') as f:
                    f.write(f'{current_time} - {url}\n')

    def is_site_blocked(self, url):
        # Чтение черного списка сайтов
        blacklist_path = os.path.join(sys.path[0], '..', '..', 'black-web.txt')

        # Ключевые слова для блокировки (казино, ставки, торренты, порно и т.д.)
        blocked_keywords = [
            "casino", "bet", "torrent", "lottery", "hack", "malware", "phish",
            "porn", "xxx", "adult", "sex", "erotic", "nude", "cams"
        ]

        # Блокируемые доменные зоны
        blocked_domains = [".ru", ".bet", ".casino", ".torrent", ".lottery", ".poker", 
                           ".xxx", ".adult", ".sex", ".porn", ".cam"]

        if os.path.exists(blacklist_path):
            with open(blacklist_path, 'r') as f:
                blocked_sites = f.read().splitlines()
                # Проверка по черному списку URL
                for blocked_site in blocked_sites:
                    if blocked_site in url:
                        return True

        # Проверка по ключевым словам
        for keyword in blocked_keywords:
            if keyword in url:
                return True

        # Проверка по доменным зонам
        for domain in blocked_domains:
            if domain in url:
                return True

        return False

    def custom_blocked_page(self):
        return """
        <html>
        <head><title>Сайт заблокирован</title></head>
        <body>
        <h1>Сайт заблокирован</h1>
        <p>Доступ к этому сайту был ограничен администратором.</p>
        </body>
        </html>
        """


class RoundedTabBar(QTabBar):
    def paintEvent(self, event):
        painter = QPainter(self)
        option = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(option, i)
            # Округление вкладок на 20%
            option.rect = self.tabRect(i)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setBrush(option.palette.window())
            painter.setPen(Qt.NoPen)
            rounded_rect = option.rect.adjusted(5, 5, -5, -5)
            painter.drawRoundedRect(rounded_rect, rounded_rect.height() * 0.2, rounded_rect.height() * 0.2)
            self.style().drawControl(QStyle.CE_TabBarTabLabel, option, painter)

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        size.setHeight(35)  # Высота вкладки
        size.setWidth(120)  # Ширина вкладки
        return size

class Browser(QMainWindow):
    GITHUB_REPO = "foxgalaxy23g/WaterWolf"  # Замените на ваше имя пользователя и репозиторий
    CURRENT_VERSION = "1.3.3"  # Версия текущего браузера

    def __init__(self):
        super().__init__()

        if not self.ask_for_password():
            QMessageBox.critical(self, 'Ошибка', 'Три неудачные попытки ввода пароля. Браузер будет закрыт.')
            sys.exit()
        # Убираем стандартную панель заголовка окна
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        # Устанавливаем минимальные размеры для окна
        self.setMinimumSize(800, 600)

        # Путь к конфигурационным файлам
        self.config = configparser.ConfigParser()
        config_path = os.path.join(sys.path[0], '..', 'config.ini')
        self.config.read(config_path)

        # Устанавливаем путь к папке с иконками, которая находится на одну директорию ниже
        icons_path = os.path.join(sys.path[0], '..', 'icons')

        # Проверяем обновления при запуске
        self.check_for_updates()

        # Создаем виджет с вкладками
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)

        # Создаем кастомную панель заголовка
        self.create_custom_title_bar()

        # Добавляем первую вкладку
        self.add_new_tab(QUrl.fromLocalFile(os.path.join(sys.path[0], '..', 'start_page.html')), 'Home')
        # Отображаем окно
        self.show()


    def create_custom_title_bar(self):
        # Создаем кастомную панель заголовка
        title_bar = QWidget()
        title_bar.setObjectName("title_bar")
        title_bar.setStyleSheet("""
            #title_bar {
                background-color: #2E2E2E;
                color: white;
                padding: 5px;
            }
            QPushButton {
                background-color: #00000000;
                border: none;
                color: white;
                padding: 5px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #00000000;
            }
        """)
        title_bar_layout = QHBoxLayout()

        # Путь к иконкам
        icon_path = os.path.join(sys.path[0], '..', 'icons')

        # Кнопка "Назад" с изображением
        back_btn = QPushButton()
        back_btn.setIcon(QIcon(os.path.join(icon_path, 'back.png')))
        back_btn.clicked.connect(self.navigate_back)
        title_bar_layout.addWidget(back_btn)

        # Кнопка "Вперед" с изображением
        forward_btn = QPushButton()
        forward_btn.setIcon(QIcon(os.path.join(icon_path, 'forward.png')))
        forward_btn.clicked.connect(self.navigate_forward)
        title_bar_layout.addWidget(forward_btn)

        # Кнопка "Обновить" с изображением
        reload_btn = QPushButton()
        reload_btn.setIcon(QIcon(os.path.join(icon_path, 'reload.png')))
        reload_btn.clicked.connect(self.reload_page)
        title_bar_layout.addWidget(reload_btn)

        # Кнопка "Домой" с изображением
        home_btn = QPushButton()
        home_btn.setIcon(QIcon(os.path.join(icon_path, 'home.png')))
        home_btn.clicked.connect(self.navigate_home)
        title_bar_layout.addWidget(home_btn)

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)  # Прячем его по умолчанию
        title_bar_layout.addWidget(self.progress_bar)

        # Поле URL
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        title_bar_layout.addWidget(self.url_bar)

        # Кнопки управления окном
        minimize_btn = QPushButton()
        minimize_btn.setIcon(QIcon(os.path.join(icon_path, 'minimize.png')))
        minimize_btn.clicked.connect(self.showMinimized)
        title_bar_layout.addWidget(minimize_btn)

        maximize_btn = QPushButton()
        maximize_btn.setIcon(QIcon(os.path.join(icon_path, 'maximize.png')))
        maximize_btn.clicked.connect(self.toggle_maximized)
        title_bar_layout.addWidget(maximize_btn)

        close_btn = QPushButton()
        close_btn.setIcon(QIcon(os.path.join(icon_path, 'closer.png')))
        close_btn.clicked.connect(self.close)
        title_bar_layout.addWidget(close_btn)

        title_bar.setLayout(title_bar_layout)

        # Устанавливаем кастомную панель заголовка
        self.setMenuWidget(title_bar)

    def on_load_started(self):
        # Скрываем строку URL и показываем прогресс-бар
        self.url_bar.setVisible(False)
        self.progress_bar.setVisible(True)

        # Устанавливаем случайный цвет прогресс-бара
        random_color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.progress_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {random_color.name()}; }}")

    def on_load_progress(self, progress):
        # Обновляем прогресс-бар
        self.progress_bar.setValue(progress)

    def on_load_finished(self, success):
        # Когда загрузка завершена, прячем прогресс-бар и показываем строку URL
        self.progress_bar.setVisible(False)
        self.url_bar.setVisible(True)

    def mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos()

    def mouse_move_event(self, event):
        if event.buttons() & Qt.LeftButton:
            delta = event.globalPos() - self.drag_start_position
            self.move(self.pos() + delta)
            self.drag_start_position = event.globalPos()

    def toggle_maximized(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def tab_open_doubleclick(self, index):
        if index == -1:  # Если дважды щелкнули по пустому пространству вкладок
            self.add_new_tab()

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl.fromLocalFile(os.path.join(sys.path[0], '..', 'start_page.html'))

        browser = QWebEngineView()
        browser.setPage(CustomWebEnginePage(self))

        browser.setUrl(qurl)

        self.add_new_tab_widget(browser, label)

        browser.loadStarted.connect(self.on_load_started)
        browser.loadProgress.connect(self.on_load_progress)
        browser.loadFinished.connect(self.on_load_finished)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(title, browser))
        browser.iconChanged.connect(lambda icon: self.update_tab_icon(icon, browser))
        self.update_urlbar(qurl, browser)

        browser.loadFinished.connect(self.check_for_errors)
    
    def check_for_errors(self, success):
        if not success:
            current_browser = self.tabs.currentWidget()
            current_browser.setHtml(self.custom_error_page())

    def custom_error_page(self):
        return """
        <html>
        <head><title>Ошибка загрузки</title></head>
        <body>
        <h1>Страница не найдена</h1>
        <p>К сожалению, произошла ошибка при загрузке страницы.</p>
        </body>
        </html>
        """

    def add_new_tab_widget(self, webview, label="New Tab"):
        i = self.tabs.addTab(webview, label)
        self.tabs.setCurrentIndex(i)

        # Добавление кастомной кнопки закрытия
        close_btn = QPushButton()
        close_btn.setIcon(QIcon(os.path.join(sys.path[0], '..', 'icons', 'close.png')))
        close_btn.setIconSize(QPixmap(os.path.join(sys.path[0], '..', 'icons', 'close.png')).size())
        close_btn.setFlat(True)
        close_btn.clicked.connect(lambda: self.close_current_tab(self.tabs.indexOf(webview)))

        self.tabs.tabBar().setTabButton(i, QTabBar.RightSide, close_btn)

    def update_tab_icon(self, icon, browser):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabIcon(index, icon)

    def close_current_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)
        else:
            sys.exit()

    def navigate_home(self):
        start_page_path = os.path.join(sys.path[0], '..', 'start_page.html')
        start_page_url = QUrl.fromLocalFile(start_page_path)
        self.tabs.currentWidget().setUrl(start_page_url)

    def navigate_back(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().back()

    def navigate_forward(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().forward()

    def reload_page(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().reload()

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith('http'):
            # Если в адресе нет http, то считаем его поисковым запросом
            url = f'{self.get_search_engine_url()}{url}'
        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_tab_title(self, title, browser):
        if browser == self.tabs.currentWidget():
            self.setWindowTitle(title)
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, title)

    def update_urlbar(self, qurl, browser=None):
        if browser == self.tabs.currentWidget():
            self.url_bar.setText(qurl.toString())

    def get_password(self):
        password_path = os.path.join(sys.path[0], '..', 'password.txt')
        if os.path.exists(password_path):
            with open(password_path, 'r') as f:
                password = f.read().strip()
                return password if password else None
        return None
    
    def ask_for_password(self):
        stored_password = self.get_password()
        if stored_password:
            attempts = 3
            for _ in range(attempts):
                password, ok = QInputDialog.getText(self, 'Пароль', 'Введите пароль:', QLineEdit.Password)
                if ok and password == stored_password:
                    return True
                QMessageBox.warning(self, 'Неправильный пароль', f'Осталось попыток: {attempts - 1}')
            return False
        return True  # Если пароля нет, то можно запускать браузер без проверки


    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())

    def is_user_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self):
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

    def check_for_updates(self):
        if not self.ask_for_password():
            QMessageBox.critical(self, 'Ошибка', 'Три неудачные попытки ввода пароля. Обновление невозможно.')
            return
        
        try:
            response = requests.get(f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest")
            latest_release = response.json()
            latest_version = latest_release["tag_name"]
            if latest_version > self.CURRENT_VERSION:
                reply = QMessageBox.question(
                    self, "Обновление доступно",
                    f"Вышла новая версия {latest_version}. Обновить сейчас?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    if not self.is_user_admin():
                        QMessageBox.warning(self, "Требуются права администратора", "Для проверки обновлений запустите программу от имени администратора.")
                        reply = QMessageBox.question(self, "Запуск от имени администратора", "Хотите перезапустить приложение с правами администратора?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        if reply == QMessageBox.Yes:
                            self.run_as_admin()
                    else:
                        asset_url = None
                        for asset in latest_release["assets"]:
                            if asset["name"] == "update.zip":
                                asset_url = asset["browser_download_url"]
                                break

                        if asset_url:
                            self.download_and_install_update(asset_url, latest_version)
                        else:
                            QMessageBox.critical(self, "Ошибка", "Не удалось найти файл update.zip в последнем релизе.")
        except Exception as e:
            print(f"Ошибка при проверке обновлений: {e}")

    def download_and_install_update(self, url, latest_version):
        updater_dir = os.path.join(sys.path[0], '..', '..')
        update_zip_path = os.path.join(updater_dir, "update.zip")

        try:
            # Загружаем update.zip
            with requests.get(url, stream=True) as r:
                with open(update_zip_path, 'wb') as f:
                    total_length = r.headers.get('content-length')
                    if total_length is None:  # Нет информации о размере
                        f.write(r.content)
                    else:
                        dl = 0
                        total_length = int(total_length)
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                dl += len(chunk)
                                f.write(chunk)
                                done = int(50 * dl / total_length)
                                print(f"\rЗагрузка обновления: [{'=' * done}{' ' * (50-done)}] {2*done}%")

            # Запускаем update.bat для установки обновления
            update_bat_path = os.path.join(updater_dir, "update.bat")
            subprocess.Popen([update_bat_path], shell=True)

            # Закрываем приложение
            sys.exit()

        except Exception as e:
            print(f"Ошибка при загрузке и установке обновления: {e}")

    def get_search_engine_url(self):
        # Определяем поисковую систему из конфигурации
        search = self.config.get('Settings', 'search', fallback='google')
        if search == 'google':
            return 'https://www.google.com/search?q='
        elif search == 'duckduckgo':
            return 'https://duckduckgo.com/?q='
        else:
            return 'https://www.google.com/search?q='
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

        if event.key() == Qt.Key_F9:
            self.open_history_file()

        if event.key() == Qt.Key_F8:
            self.clear_history_file()

    def open_history_file(self):
        if is_user_admin():
            history_path = os.path.join(sys.path[0], '..', '..', 'history.txt')
            # Открыть файл истории в текстовом редакторе по умолчанию
            subprocess.Popen(['notepad.exe', history_path])

    def clear_history_file(self):
        if is_user_admin():
            history_path = os.path.join(sys.path[0], '..', '..', 'history.txt')
            # Очистить файл истории
            with open(history_path, 'w') as f:
                f.write('')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = Browser()
    app.exec_()