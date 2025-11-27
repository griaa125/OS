import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon

# URL сайта, который нужно открыть
SITE_URL = "https://visvision.lovable.app/"
# Имя файла иконки. Убедитесь, что этот файл находится рядом с вашим скриптом.
ICON_FILE = "icon.png"
PROFILE_NAME = "VisVisionPersistentProfile"

# --- ИЗМЕНЕНИЕ: ВОЗВРАТ К НАИБОЛЕЕ НАДЕЖНОМУ ПУТИ ДЛЯ EXE ---

# Для обеспечения надежного сохранения данных аккаунта при запуске
# скомпилированного .exe, используем стандартный каталог данных пользователя.
# Это гарантирует, что данные сохранятся, даже если .exe запускается из временной папки.
APP_DATA_DIR = os.path.join(os.path.expanduser('~'), ".visvision_app_data")

# JavaScript для удаления водяного знака "Lovable" по уникальному ID
REMOVE_WATERMARK_JS = """
    function removeLovableWatermark() {
        var badge = document.getElementById('lovable-badge');
        if (badge) {
            badge.style.display = 'none';
        }
    }
    // Запускаем с небольшой задержкой (2 секунды) для полной загрузки сайта
    setTimeout(removeLovableWatermark, 2000);
"""


class WebAppBrowser(QMainWindow):
    """
    Главное окно приложения, встраивающее веб-браузер (QWebEngineView).
    """

    def __init__(self):
        super().__init__()

        # 1. Настройка окна
        self.setWindowTitle("VisVision")
        self.setGeometry(100, 100, 1000, 700)
        try:
            self.setWindowIcon(QIcon(ICON_FILE))
        except:
            pass  # Игнорируем, если иконка не найдена

        # 2. Setup the persistent profile (для сохранения логина)
        try:
            # Создаем папку для данных в домашнем каталоге
            os.makedirs(APP_DATA_DIR, exist_ok=True)
            self.profile = QWebEngineProfile(PROFILE_NAME, self)
            self.profile.setPersistentStoragePath(APP_DATA_DIR)
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        except Exception as e:
            # Fallback на профиль по умолчанию, если не удалось создать папку
            print(f"Ошибка создания постоянного профиля: {e}. Используется профиль по умолчанию.")
            self.profile = QWebEngineProfile.defaultProfile()

            # 3. Создание виджета веб-движка
        self.browser = QWebEngineView()
        self.page = QWebEnginePage(self.profile, self.browser)
        self.browser.setPage(self.page)
        self.browser.setUrl(QUrl(SITE_URL))

        # Привязываем выполнение JavaScript после завершения загрузки
        self.browser.page().loadFinished.connect(self.on_load_finished)

        # 4. Установка веб-движка как центрального виджета
        self.setCentralWidget(self.browser)

        self.show()

    def on_load_finished(self, success):
        """Выполняется после загрузки страницы для удаления водяного знака."""
        if success:
            # Выполняем скрипт для удаления водяного знака
            self.browser.page().runJavaScript(REMOVE_WATERMARK_JS)


if __name__ == "__main__":
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    app.setApplicationName("VisVisionApp")

    window = WebAppBrowser()
    sys.exit(app.exec())