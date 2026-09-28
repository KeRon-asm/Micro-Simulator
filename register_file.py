# Task 4: Register File
# 8 x 32-bit general-purpose registers (t0-t7)
from Processor_Parser import Parser

class RegisterFile:
    def __init__(self):
        self.valid        = 1
        self.registers    = [0] * 8
        self.reg_names    = [f"t{i}" for i in range(8)]
        self.write_enable = 0
        self.log          = []

    def _log(self, msg):
        self.log.append(msg)
        print(msg)

    # Load initial value into a register, validated through Parser
    def load(self, reg_idx, value):
        if reg_idx < 0 or reg_idx > 7:
            self._log(f"Error: Register index {reg_idx} out of range (0-7)")
            self.valid = 0
            return
        p = Parser(value)
        val, ovf, sat = p.get_output("DEC")
        self.registers[reg_idx] = val
        if ovf:
            self._log(f"  Load {self.reg_names[reg_idx]} = {val}  (Overflow/Saturated O:{ovf} S:{sat})")
        else:
            self._log(f"  Load {self.reg_names[reg_idx]} = {val}")

    # Read two source registers, return their values
    def read(self, rs1, rs2):
        val1 = self.registers[rs1]
        val2 = self.registers[rs2]
        return val1, val2

    # Write result to destination register — gated by write_enable
    def write(self, rd, result):
        if self.write_enable:
            p = Parser(result)
            val, ovf, sat = p.get_output("DEC")
            self.registers[rd] = val
            self._log(f"  RegWrite: {self.reg_names[rd]} = {val}  (O:{ovf} S:{sat})")
        else:
            self._log(f"  RegWrite DISABLED: {self.reg_names[rd]} not updated")

    # Return all register values displayed in fmt format
    def get_output(self, fmt):
        lines = []
        for i, val in enumerate(self.registers):
            p = Parser(val)
            disp, _, _ = p.get_output(fmt)
            lines.append(f"  {self.reg_names[i]} = {disp}")
        return "\n".join(lines), self.write_enable, self.valid

# Tests
def run_tests():
    print("\n--- Running Tests (RegisterFile) ---")
    rf = RegisterFile()
    test_loads = [(0, 5), (1, 3), (2, 6), (3, 1), (5, 6)]
    for idx, val in test_loads:
        rf.load(idx, val)
    rf.write_enable = 1
    rf.write(4, 15)
    result, we, valid = rf.get_output("HEX")
    print(f"\nRegisters (HEX): W:{we} Valid:{valid}")
    print(result)

if __name__ == "__main__":
    run_tests()

    try:
        print("\n--- Interactive Mode (RegisterFile) ---")
        fmt_in = input("Display format (DEC/BIN/HEX): ").upper()
        rf = RegisterFile()
        for i in range(8):
            val = int(input(f"  t{i} value: "))
            rf.load(i, val)
        result, we, valid = rf.get_output(fmt_in)
        print(f"\nRegisters ({fmt_in}):")
        print(result)
    except (ValueError, EOFError):
        print("Invalid input")
