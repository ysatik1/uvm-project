#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from assembler import UVMAssembler
    from interpreter import UVMInterpreter
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что assembler.py и interpreter.py находятся в той же папке")


class UVMGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Учебная Виртуальная Машина (УВМ)")
        self.root.geometry("1000x700")

        self.assembler = UVMAssembler()
        self.interpreter = UVMInterpreter()

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        title_label = ttk.Label(main_frame,
                                text="Учебная Виртуальная Машина",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        left_frame = ttk.LabelFrame(main_frame, text="Редактор программы", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)

        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        control_frame = ttk.LabelFrame(right_frame, text="Управление", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        output_frame = ttk.LabelFrame(right_frame, text="Выполнение и память", padding="10")
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.code_editor = scrolledtext.ScrolledText(left_frame, width=50, height=20, font=("Courier New", 10))
        self.code_editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.load_example_code()

        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        run_button = ttk.Button(button_frame, text="▶ Ассемблировать и выполнить", command=self.run_program)
        run_button.grid(row=0, column=0, padx=(0, 10))

        clear_button = ttk.Button(button_frame, text="🗑 Очистить", command=self.clear_output)
        clear_button.grid(row=0, column=1, padx=(0, 10))

        load_button = ttk.Button(button_frame, text="📁 Загрузить", command=self.load_file)
        load_button.grid(row=0, column=2, padx=(0, 10))

        save_button = ttk.Button(button_frame, text="💾 Сохранить", command=self.save_file)
        save_button.grid(row=0, column=3)

        range_frame = ttk.Frame(control_frame)
        range_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Label(range_frame, text="Диапазон памяти:").grid(row=0, column=0, padx=(0, 10))

        ttk.Label(range_frame, text="от").grid(row=0, column=1, padx=(0, 5))
        self.start_addr = ttk.Entry(range_frame, width=5)
        self.start_addr.insert(0, "0")
        self.start_addr.grid(row=0, column=2, padx=(0, 10))

        ttk.Label(range_frame, text="до").grid(row=0, column=3, padx=(0, 5))
        self.end_addr = ttk.Entry(range_frame, width=5)
        self.end_addr.insert(0, "300")
        self.end_addr.grid(row=0, column=4)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, font=("Courier New", 9))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

    def load_example_code(self):
        example_code = """; Пример программы для УВМ
; Загрузка данных в память и применение SGN

; Исходный вектор
LOAD_CONST 5
WRITE_MEM 100
LOAD_CONST 0
WRITE_MEM 101
LOAD_CONST 8
WRITE_MEM 102

; Применение SGN
SGN 100
WRITE_MEM 200
SGN 101
WRITE_MEM 201
SGN 102
WRITE_MEM 202

; Дополнительные операции
LOAD_CONST 10
WRITE_MEM 103
READ_MEM 103
WRITE_MEM 203"""

        self.code_editor.delete(1.0, tk.END)
        self.code_editor.insert(1.0, example_code)

    def run_program(self):
        def thread_target():
            self.status_var.set("Ассемблирование...")
            try:
                source_code = self.code_editor.get(1.0, tk.END)

                self.assembler.assemble(source_code)
                binary_data = self.assembler.generate_binary("temp.bin", test_mode=False)

                self.status_var.set("Выполнение...")

                try:
                    start_addr = int(self.start_addr.get())
                    end_addr = int(self.end_addr.get())
                except ValueError:
                    start_addr, end_addr = 0, 300

                import io
                import contextlib

                output_buffer = io.StringIO()
                with contextlib.redirect_stdout(output_buffer):
                    self.interpreter.run("temp.bin", "temp_memory.csv", (start_addr, end_addr))

                output_text = output_buffer.getvalue()
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(1.0, output_text)

                try:
                    with open("temp_memory.csv", "r", encoding="utf-8") as f:
                        memory_dump = f.read()
                    self.output_text.insert(tk.END, "\n\n" + "=" * 50 + "\n")
                    self.output_text.insert(tk.END, "ДАМП ПАМЯТИ:\n")
                    self.output_text.insert(tk.END, "=" * 50 + "\n")
                    self.output_text.insert(tk.END, memory_dump)
                except FileNotFoundError:
                    self.output_text.insert(tk.END, "\n\nОшибка: файл дампа памяти не найден")

                self.status_var.set("Программа завершена успешно")

            except Exception as e:
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(1.0, f"ОШИБКА: {str(e)}")
                self.status_var.set("Ошибка выполнения")

        thread = threading.Thread(target=thread_target)
        thread.daemon = True
        thread.start()

    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Вывод очищен")

    def load_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл с программой",
            filetypes=[("ASM файлы", "*.asm"), ("Все файлы", "*.*")]
        )
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                self.code_editor.delete(1.0, tk.END)
                self.code_editor.insert(1.0, content)
                self.status_var.set(f"Загружен файл: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def save_file(self):
        filename = filedialog.asksaveasfilename(
            title="Сохранить программу",
            defaultextension=".asm",
            filetypes=[("ASM файлы", "*.asm"), ("Все файлы", "*.*")]
        )
        if filename:
            try:
                content = self.code_editor.get(1.0, tk.END)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                self.status_var.set(f"Программа сохранена: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")


def main():
    try:
        root = tk.Tk()
        app = UVMGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка запуска GUI: {e}")
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()