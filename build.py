#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import shutil
import json


class UVMBuilder:
    def __init__(self):
        self.platform = platform.system().lower()
        self.config = self.load_config()

    def load_config(self):
        try:
            with open('build_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "app_name": "UVM",
                "version": "1.0.0",
                "description": "Учебная Виртуальная Машина",
                "main_script": "uvm_gui.py"
            }

    def check_dependencies(self):
        print("🔍 Проверка зависимостей...")

        try:
            import tkinter
            print("✅ Tkinter доступен")
        except ImportError:
            print("❌ Tkinter не доступен. Установите python3-tk")
            return False

        return True

    def create_icon(self):
        if not os.path.exists('uvm_icon.ico'):
            print("🖼️  Создание простой иконки...")
            try:
                # Создаем простой текстовый файл как заглушку
                with open('uvm_icon.ico', 'wb') as f:
                    f.write(b'')  # Пустой файл
                print("✅ Файл иконки создан")
            except:
                print("⚠️  Не удалось создать иконку")

    def build_windows(self):
        print("🔨 Сборка для Windows...")

        spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['uvm_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assembler.py', '.'),
        ('interpreter.py', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.config["app_name"]}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='uvm_icon.ico' if os.path.exists('uvm_icon.ico') else None,
)
"""

        with open('uvm_windows.spec', 'w', encoding='utf-8') as f:
            f.write(spec_content)

        try:
            subprocess.run(['pyinstaller', 'uvm_windows.spec'], check=True)
            print("✅ Сборка для Windows завершена!")

            bat_content = f"""@echo off
echo Запуск {self.config["app_name"]}...
dist\\{self.config["app_name"]}.exe
pause
"""
            with open(f'run_{self.config["app_name"]}.bat', 'w', encoding='utf-8') as f:
                f.write(bat_content)

            print(f"📁 Исполняемый файл: dist/{self.config['app_name']}.exe")
            print(f"📁 Скрипт запуска: run_{self.config['app_name']}.bat")

        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка сборки: {e}")
        except FileNotFoundError:
            print("❌ PyInstaller не установлен. Установите: pip install pyinstaller")

    def build_linux(self):
        print("🔨 Сборка для Linux...")

        try:
            subprocess.run([
                'pyinstaller',
                '--onefile',
                '--name', f'{self.config["app_name"]}',
                '--add-data', 'assembler.py:.',
                '--add-data', 'interpreter.py:.',
                'uvm_gui.py'
            ], check=True)

            sh_content = f"""#!/bin/bash
echo "Запуск {self.config['app_name']}..."
./dist/{self.config['app_name']}
"""
            with open(f'run_{self.config["app_name"]}.sh', 'w', encoding='utf-8') as f:
                f.write(sh_content)
            os.chmod(f'run_{self.config["app_name"]}.sh', 0o755)

            print("✅ Сборка для Linux завершена!")
            print(f"📁 Исполняемый файл: dist/{self.config['app_name']}")
            print(f"📁 Скрипт запуска: run_{self.config['app_name']}.sh")

        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка сборки: {e}")
        except FileNotFoundError:
            print("❌ PyInstaller не установлен. Установите: pip install pyinstaller")

    def build(self):
        print("🚀 Начало сборки УВМ")
        print(f"Платформа: {self.platform}")

        if not self.check_dependencies():
            return

        self.create_icon()

        if self.platform == 'windows':
            self.build_windows()
        elif self.platform == 'linux':
            self.build_linux()
        else:
            print(f"⚠️  Платформа {self.platform} не поддерживается напрямую")
            print("Попытка сборки в общем режиме...")
            self.build_linux()

        print("\n✅ Сборка завершена!")


def main():
    builder = UVMBuilder()
    builder.build()


if __name__ == "__main__":
    main()