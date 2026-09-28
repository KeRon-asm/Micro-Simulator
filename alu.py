# Task 4: ALU
# Supports AND, OR with optional input inversion (NOT via control signal)
# NOT is NOT a separate instruction — it is an ALU control signal (invert_a)
import Processor_Parser

class ALU:
    def __init__(self):
        self.valid     = 1
        self.result    = 0
        self.zero_flag = 0
        self.log       = []

    def _log(self, msg):
        self.log.append(msg)
        print(msg)

    # Execute ALU operation
    # alu_op  : 0 = AND, 1 = OR
    # invert_a: 1 = bitwise NOT on input_a before operation (NOT via control signal)
    def execute(self, input_a, input_b, alu_op, invert_a):
        mask = 0xFFFFFFFF

        # Inversion of input_a — controlled via invert_a signal (encodes NOT)
        if invert_a:
            input_a = (~input_a) & mask
            self._log(f"  ALU: invert_a=1, ~A = 0x{input_a:08X}")

        if alu_op == 0:
            raw    = input_a & input_b
            op_str = "AND"
        else:
            raw    = input_a | input_b
            op_str = "OR"

        # Validate result through Parser (32-bit saturation / overflow check)
        p = Processor_Parser.Parser(raw)
        self.result, ovf, sat = p.get_output("DEC")
        self.zero_flag = 1 if self.result == 0 else 0

        self._log(f"  ALU: {op_str}(0x{input_a:08X}, 0x{input_b:08X})"
                  f" = 0x{raw & mask:08X}  O:{ovf} S:{sat} Zero:{self.zero_flag}")
        return self.result, self.zero_flag

    # Return last result in fmt format
    def get_output(self, fmt):
        p = Processor_Parser.Parser(self.result)
        disp, ovf, sat = p.get_output(fmt)
        return disp, self.zero_flag, ovf

# Tests
def run_tests():
    print("\n--- Running Tests (ALU) ---")
    alu = ALU()
    test_cases = [
        # input_a, input_b, alu_op, invert_a, description
        (0b1010,  0b1100, 0, 0, "AND(A, B)         -> A&B"),
        (0b0110,  0b0001, 0, 1, "AND(~C, D)        -> (~C)&D"),
        (0b1000,  0b0111, 1, 0, "OR(t4, t6)        -> t4|t6"),
        (0,       0,      0, 0, "AND(0,0) zero flag"),
    ]
    for a, b, op, inv, desc in test_cases:
        result, zero = alu.execute(a, b, op, inv)
        out, z, ovf = alu.get_output("BIN")
        print(f"  {desc}")
        print(f"    Result (BIN): {out}  Zero:{z}\n")

if __name__ == "__main__":
    run_tests()

    try:
        print("\n--- Interactive Mode (ALU) ---")
        a_in   = int(input("Input A (decimal): "))
        b_in   = int(input("Input B (decimal): "))
        op_in  = int(input("ALU op (0=AND, 1=OR): "))
        inv_in = int(input("Invert A? (0=No, 1=Yes): "))
        fmt_in = input("Format (DEC/BIN/HEX): ").upper()

        alu = ALU()
        result, zero = alu.execute(a_in, b_in, op_in, inv_in)
        disp, z, ovf = alu.get_output(fmt_in)
        print(f"\nResult: {disp}")
        print(f"Zero: {z}  Overflow: {ovf}")
    except (ValueError, EOFError):
        print("Invalid input")
