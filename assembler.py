#!/usr/bin/env python3
import sys
import argparse
import struct


class UVMAssembler:
    def __init__(self):
        self.instructions = []

    OPCODES = {
        'LOAD_CONST': 14,
        'READ_MEM': 11,
        'WRITE_MEM': 7,
        'SGN': 4
    }

    def parse_line(self, line):
        line = line.strip()
        if not line or line.startswith(';'):
            return None

        if ';' in line:
            line = line.split(';')[0].strip()

        parts = line.split()
        if not parts:
            return None

        mnemonic = parts[0].upper()
        if mnemonic not in self.OPCODES:
            raise ValueError(f"Неизвестная мнемоника: {mnemonic}")

        if len(parts) != 2:
            raise ValueError(f"Неверное количество аргументов для {mnemonic}")

        try:
            operand = int(parts[1])
        except ValueError:
            raise ValueError(f"Неверный формат операнда: {parts[1]}")

        if mnemonic == 'LOAD_CONST':
            if operand < -16384 or operand > 16383:
                raise ValueError(f"Константа {operand} вне диапазона -16384..16383")
        else:
            if operand < 0 or operand > 2047:
                raise ValueError(f"Адрес {operand} вне диапазона 0-2047")

        return {
            'opcode': self.OPCODES[mnemonic],
            'operand': operand,
            'mnemonic': mnemonic
        }

    def assemble(self, source_code):
        self.instructions = []

        for line_num, line in enumerate(source_code.split('\n'), 1):
            try:
                instruction = self.parse_line(line)
                if instruction:
                    self.instructions.append(instruction)
            except Exception as e:
                raise ValueError(f"Ошибка в строке {line_num}: {e}")

        return self.instructions

    def encode_instruction(self, instruction):
        opcode = instruction['opcode']
        operand = instruction['operand']

        if instruction['mnemonic'] == 'LOAD_CONST':
            # Преобразуем в 15-битное беззнаковое представление
            if operand < 0:
                operand = operand & 0x7FFF

            byte1 = (opcode & 0x0F) | ((operand & 0x0F) << 4)
            byte2 = (operand >> 4) & 0xFF
            byte3 = (operand >> 12) & 0x07
            return bytes([byte1, byte2, byte3])
        else:
            byte1 = (opcode & 0x0F) | ((operand & 0x0F) << 4)
            byte2 = (operand >> 4) & 0xFF
            byte3 = 0
            return bytes([byte1, byte2, byte3])

    def generate_binary(self, output_file, test_mode=False):
        binary_data = b''

        for instr in self.instructions:
            binary_instr = self.encode_instruction(instr)
            binary_data += binary_instr

            if test_mode:
                hex_repr = ', '.join([f'0x{byte:02X}' for byte in binary_instr])
                print(f"{instr['mnemonic']} {instr['operand']}: {hex_repr}")

        with open(output_file, 'wb') as f:
            f.write(binary_data)

        return binary_data

    def display_intermediate(self):
        print("Промежуточное представление:")
        print("A\tB\tМнемоника")
        print("-" * 30)

        for instr in self.instructions:
            a = instr['opcode']
            b = instr['operand']
            mnemonic = instr['mnemonic']
            print(f"{a}\t{b}\t{mnemonic}")


def main():
    parser = argparse.ArgumentParser(description='Ассемблер УВМ')
    parser.add_argument('input_file', help='Путь к исходному файлу')
    parser.add_argument('output_file', help='Путь к двоичному файлу-результату')
    parser.add_argument('--test', action='store_true', help='Режим тестирования')

    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()

        assembler = UVMAssembler()
        assembler.assemble(source_code)

        if args.test:
            assembler.display_intermediate()
            print("\nБинарное представление:")
            binary_data = assembler.generate_binary(args.output_file, test_mode=True)
        else:
            binary_data = assembler.generate_binary(args.output_file)

        print(f"\nУспешно ассемблировано {len(assembler.instructions)} команд")

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()