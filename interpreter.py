#!/usr/bin/env python3
import sys
import argparse
import csv
import os


class UVMInterpreter:
    def __init__(self, memory_size=2048):
        self.data_memory = [0] * memory_size
        self.code_memory = []
        self.stack = []
        self.pc = 0
        self.halted = False

    def load_program(self, binary_file):
        if not os.path.exists(binary_file):
            raise FileNotFoundError(f"Файл {binary_file} не найден")

        with open(binary_file, 'rb') as f:
            program_data = f.read()

        self.code_memory = []
        for i in range(0, len(program_data), 3):
            instruction_bytes = program_data[i:i + 3]
            if len(instruction_bytes) == 3:
                self.code_memory.append(instruction_bytes)
            else:
                instruction_bytes += b'\x00' * (3 - len(instruction_bytes))
                self.code_memory.append(instruction_bytes)

        print(f"Загружено {len(self.code_memory)} инструкций")
        return len(self.code_memory)

    def decode_instruction(self, instruction_bytes):
        if len(instruction_bytes) != 3:
            raise ValueError(f"Инструкция должна быть 3 байта")

        byte1, byte2, byte3 = instruction_bytes
        opcode = byte1 & 0x0F

        if opcode == 14:  # LOAD_CONST
            operand_unsigned = ((byte1 & 0xF0) >> 4) | (byte2 << 4) | (byte3 << 12)
            if operand_unsigned & 0x4000:
                operand = operand_unsigned - 0x8000
            else:
                operand = operand_unsigned
            mnemonic = "LOAD_CONST"

        elif opcode == 11:  # READ_MEM
            operand = ((byte1 & 0xF0) >> 4) | (byte2 << 4)
            mnemonic = "READ_MEM"

        elif opcode == 7:  # WRITE_MEM
            operand = ((byte1 & 0xF0) >> 4) | (byte2 << 4)
            mnemonic = "WRITE_MEM"

        elif opcode == 4:  # SGN
            operand = ((byte1 & 0xF0) >> 4) | (byte2 << 4)
            mnemonic = "SGN"

        else:
            raise ValueError(f"Неизвестный код операции: {opcode}")

        return {
            'opcode': opcode,
            'operand': operand,
            'mnemonic': mnemonic,
            'bytes': instruction_bytes
        }

    def execute_instruction(self, instruction):
        opcode = instruction['opcode']
        operand = instruction['operand']
        mnemonic = instruction['mnemonic']

        print(f"[PC:{self.pc:03d}] {mnemonic} {operand:4d} | Стек: {self.stack}")

        if opcode == 14:  # LOAD_CONST
            self.stack.append(operand)

        elif opcode == 11:  # READ_MEM
            if operand < 0 or operand >= len(self.data_memory):
                raise ValueError(f"Адрес памяти {operand} вне диапазона")
            value = self.data_memory[operand]
            self.stack.append(value)

        elif opcode == 7:  # WRITE_MEM
            if operand < 0 or operand >= len(self.data_memory):
                raise ValueError(f"Адрес памяти {operand} вне диапазона")
            if not self.stack:
                raise ValueError("Стек пуст для операции WRITE_MEM")
            value = self.stack.pop()
            self.data_memory[operand] = value

        elif opcode == 4:  # SGN
            if operand < 0 or operand >= len(self.data_memory):
                raise ValueError(f"Адрес памяти {operand} вне диапазона")

            value = self.data_memory[operand]

            if value > 0:
                result = 1
            elif value < 0:
                result = -1
            else:
                result = 0

            self.stack.append(result)

    def run(self, binary_file, memory_dump_file, dump_range=None, max_steps=1000):
        instructions_count = self.load_program(binary_file)

        print("=" * 50)
        print("ЗАПУСК ИНТЕРПРЕТАТОРА УВМ")
        print("=" * 50)

        step = 0
        self.pc = 0

        try:
            while self.pc < len(self.code_memory) and step < max_steps and not self.halted:
                instruction_bytes = self.code_memory[self.pc]
                instruction = self.decode_instruction(instruction_bytes)
                self.execute_instruction(instruction)
                self.pc += 1
                step += 1

            if step >= max_steps:
                print(f"\nПРЕДУПРЕЖДЕНИЕ: Достигнут лимит {max_steps} шагов")
            elif self.halted:
                print(f"\nПрограмма завершена по команде остановки")
            else:
                print(f"\nПрограмма завершена успешно")

            print(f"Выполнено шагов: {step}")

        except Exception as e:
            print(f"\nОШИБКА ВЫПОЛНЕНИЯ на шаге {step}, PC={self.pc}: {e}")
            return False

        self.dump_memory(memory_dump_file, dump_range)
        return True

    def dump_memory(self, filename, dump_range=None):
        if dump_range:
            start, end = dump_range
        else:
            start, end = 0, len(self.data_memory)

        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Адрес', 'Значение', 'Описание'])

            non_zero_count = 0
            for addr in range(start, min(end, len(self.data_memory))):
                value = self.data_memory[addr]
                description = ""

                if value != 0:
                    non_zero_count += 1
                    if 100 <= addr <= 109:
                        description = f"Элемент массива A[{addr - 100}]"
                    elif 200 <= addr <= 209:
                        description = f"Элемент массива B[{addr - 200}]"

                writer.writerow([addr, value, description])

        print(f"Дамп памяти сохранен в {filename}")
        print(f"Диапазон адресов: {start}-{min(end, len(self.data_memory)) - 1}")
        print(f"Ненулевых ячеек: {non_zero_count}")


def parse_range(range_str):
    if not range_str:
        return None

    try:
        if '-' in range_str:
            start, end = map(int, range_str.split('-'))
            return start, end + 1
        else:
            addr = int(range_str)
            return addr, addr + 1
    except:
        raise ValueError("Неверный формат диапазона. Используйте: start-end или address")


def main():
    parser = argparse.ArgumentParser(description='Интерпретатор УВМ')
    parser.add_argument('binary_file', help='Путь к бинарному файлу с программой')
    parser.add_argument('memory_dump', help='Путь к файлу для дампа памяти')
    parser.add_argument('--range', help='Диапазон адресов для дампа (формат: start-end или address)')
    parser.add_argument('--max-steps', type=int, default=1000, help='Максимальное количество шагов выполнения')

    args = parser.parse_args()

    try:
        dump_range = parse_range(args.range)

        interpreter = UVMInterpreter()
        success = interpreter.run(args.binary_file, args.memory_dump, dump_range, args.max_steps)

        if not success:
            sys.exit(1)

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()