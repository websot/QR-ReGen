import customtkinter as ctk
from tkinter import filedialog, messagebox
import segno  # Импортируем segno напрямую
from PIL import Image
import os

# Константы
MIN_QR_SIZE = 200  # Минимальный размер QR-кода в пикселях
QR_SIZE_STEP = 50  # Шаг изменения размера QR-кода
PREVIEW_MAX_SIZE = 350  # Максимальный размер предварительного просмотра
TEMP_QR_CODE = "temp_qrcode.png"  # Временный файл для QR-кода

# Настройка внешнего вида
ctk.set_appearance_mode("System")  # Режим темы: System, Light, Dark
ctk.set_default_color_theme("blue")  # Цветовая тема

# Функция для центрирования окна
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()  # Ширина экрана
    screen_height = window.winfo_screenheight()  # Высота экрана
    x = (screen_width // 2) - (width // 2)  # Координата X для центрирования
    y = (screen_height // 2) - (height // 2)  # Координата Y для центрирования
    window.geometry(f"{width}x{height}+{x}+{y}")  # Устанавливаем положение окна

# Основное окно
class QRCodeGeneratorApp:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Генератор QR-кодов")
        self.app.resizable(False, False)  # Запрещаем изменение размеров окна
        center_window(self.app, 500, 600)  # Центрируем основное окно

        # Переменные
        self.qr_size = ctk.IntVar(value=MIN_QR_SIZE)  # Размер QR-кода
        self.about_window = None  # Окно "О программе"

        # Обработка закрытия окна
        self.app.protocol("WM_DELETE_WINDOW", self.on_close)

        # Создаем интерфейс
        self.create_widgets()

    def create_widgets(self):
        """Создаем и размещаем элементы интерфейса."""
        # Поле для ввода данных
        input_frame = ctk.CTkFrame(self.app)
        input_frame.pack(pady=10, padx=10, fill="x")

        self.entry = ctk.CTkEntry(input_frame, placeholder_text="Введите текст или ссылку")
        self.entry.pack(side="left", padx=5, fill="x", expand=True)

        clear_button = ctk.CTkButton(input_frame, text="Очистить", command=self.clear_entry)
        clear_button.pack(side="left", padx=5)

        # Кнопка для генерации QR-кода и кнопка "О программе"
        button_frame = ctk.CTkFrame(self.app)
        button_frame.pack(pady=10, padx=10, fill="x")

        generate_button = ctk.CTkButton(button_frame, text="Сгенерировать QR-код", command=self.generate_qr)
        generate_button.pack(side="left", padx=5, fill="x", expand=True)

        about_button = ctk.CTkButton(button_frame, text="?", width=30, command=self.show_about)
        about_button.pack(side="left", padx=5)

        # Настройка размера QR-кода
        size_frame = ctk.CTkFrame(self.app)
        size_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(size_frame, text="Размер QR-кода:").pack(side="left", padx=5)
        self.size_label = ctk.CTkLabel(size_frame, text=f"{self.qr_size.get()}px")
        self.size_label.pack(side="left", padx=5)

        decrease_button = ctk.CTkButton(size_frame, text="-", width=30, command=lambda: self.change_qr_size(-QR_SIZE_STEP))
        decrease_button.pack(side="left", padx=5)

        increase_button = ctk.CTkButton(size_frame, text="+", width=30, command=lambda: self.change_qr_size(QR_SIZE_STEP))
        increase_button.pack(side="left", padx=5)

        # Кнопка для сохранения QR-кода
        save_button = ctk.CTkButton(self.app, text="Сохранить QR-код", command=self.save_qr)
        save_button.pack(pady=10, padx=10, fill="x")

        # Виджет для отображения QR-кода
        self.qr_preview_label = ctk.CTkLabel(self.app, text="")
        self.qr_preview_label.pack(pady=10, padx=10, fill="both", expand=True)

        # Метка для отображения статуса
        self.status_label = ctk.CTkLabel(self.app, text="")
        self.status_label.pack(pady=10, padx=10, fill="x")

    def generate_qr(self):
        """Генерация QR-кода."""
        data = self.entry.get()  # Получаем данные из поля ввода
        if data:
            try:
                # Создаем QR-код
                qr = segno.make_qr(data)
                # Сохраняем QR-код в временный файл
                qr.save(TEMP_QR_CODE, scale=10)
                
                # Изменяем размер изображения
                img = Image.open(TEMP_QR_CODE)
                img = img.resize((self.qr_size.get(), self.qr_size.get()), Image.Resampling.LANCZOS)
                img.save(TEMP_QR_CODE)
                
                # Отображаем QR-код
                self.show_preview()
                self.status_label.configure(text="QR-код успешно создан!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        else:
            self.status_label.configure(text="Введите данные для генерации QR-кода")

    def show_preview(self):
        """Отображение предварительного просмотра QR-кода."""
        try:
            img = Image.open(TEMP_QR_CODE)
            preview_size = min(self.qr_size.get(), PREVIEW_MAX_SIZE)  # Ограничиваем размер
            img_tk = ctk.CTkImage(light_image=img, size=(preview_size, preview_size))
            self.qr_preview_label.configure(image=img_tk)
            self.qr_preview_label.image = img_tk  # Сохраняем ссылку
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть предварительный просмотр: {e}")

    def save_qr(self):
        """Сохранение QR-кода в файл."""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="Сохранить QR-код как",
                initialfile="qrcode.png"  # Имя файла по умолчанию
            )
            if file_path:
                img = Image.open(TEMP_QR_CODE)
                img.save(file_path)
                self.status_label.configure(text=f"QR-код сохранен в {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить QR-код: {e}")

    def change_qr_size(self, delta):
        """Изменение размера QR-кода."""
        new_size = self.qr_size.get() + delta
        if new_size >= MIN_QR_SIZE:  # Запрещаем размер меньше MIN_QR_SIZE
            self.qr_size.set(new_size)
            self.size_label.configure(text=f"Размер QR-кода: {self.qr_size.get()}px")
            if os.path.exists(TEMP_QR_CODE):  # Если QR-код уже создан, обновляем его отображение
                self.generate_qr()

    def clear_entry(self):
        """Очистка поля ввода."""
        self.entry.delete(0, "end")

    def show_about(self):
        """Отображение окна 'О программе'."""
        if not self.about_window or not self.about_window.winfo_exists():
            self.about_window = ctk.CTkToplevel(self.app)
            self.about_window.title("О программе")
            self.about_window.resizable(False, False)  # Запрещаем изменение размеров окна
            self.about_window.transient(self.app)  # Окно всегда поверх главного
            center_window(self.about_window, 300, 200)  # Центрируем окно
            
            info = """
            Генератор QR-кодов
            Версия: 1.0
            Автор: Ваше Имя
            Веб-сайт: example.com
            """
            ctk.CTkLabel(self.about_window, text=info, justify="left").pack(pady=20)
        else:
            self.about_window.lift()  # Поднимаем окно наверх, если оно уже открыто

    def on_close(self):
        """Обработка закрытия окна."""
        if os.path.exists(TEMP_QR_CODE):  # Удаляем временный файл, если он существует
            os.remove(TEMP_QR_CODE)
        self.app.destroy()  # Закрываем приложение

    def run(self):
        """Запуск основного цикла."""
        self.app.mainloop()

# Запуск приложения
if __name__ == "__main__":
    app = QRCodeGeneratorApp()
    app.run()
