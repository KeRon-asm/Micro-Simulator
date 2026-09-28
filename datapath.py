# Task 4: Single-Cycle Datapath
# Fetch -> Decode -> Execute -> Writeback (all in one cycle)
# Target: Y = A·B + C'·D
import Processor_Parser
from register_file import RegisterFile
from alu import ALU
from control_unit import ControlUnit

class Datapath:
    def __init__(self):
        self.valid    = 1
        self.reg_file = RegisterFile()
        self.alu      = ALU()
        self.cycle    = 0
        self.log      = []

    def _log(self, msg):
        self.log.append(msg)
        print(msg)

    # Load input values into registers (validated through Parser)
    def load_registers(self, values):
        # values: dict {reg_idx: value}
        self._log("\n  Loading Registers:")
        for idx, val in values.items():
            self.reg_file.load(idx, val)

    # Single-cycle execution: Fetch -> Decode -> Execute -> Writeback
    def execute(self, instruction):
        self.cycle += 1
        self._log(f"\n[Cycle {self.cycle}] Fetch: 0x{instruction:08X}")

        # --- Decode ---
        cu = ControlUnit(instruction)
        if not cu.valid:
            self._log("  Decode failed — halting")
            self.valid = 0
            return None
        signals, alu_op, reg_write = cu.get_output()
        self._log("  Decode / Control Signals:")
        self._log(signals)

        # --- Read Registers (MUX selects rs1, rs2) ---
        in_a, in_b = self.reg_file.read(cu.rs1, cu.rs2)
        self._log(f"  RegRead: t{cu.rs1}={in_a}  t{cu.rs2}={in_b}")

        # --- Execute (ALU) ---
        self.reg_file.write_enable = reg_write
        result, zero = self.alu.execute(in_a, in_b, alu_op, cu.invert_a)

        # --- Writeback ---
        self.reg_file.write(cu.rd, result)
        self._log(f"  Writeback complete: t{cu.rd} = {result}")
        return result

    # Return full state — fmt controls register display format
    def get_output(self, fmt):
        reg_state, _, _ = self.reg_file.get_output(fmt)
        lines = [
            f"Cycles Executed : {self.cycle}",
            f"Processor Valid : {self.valid}",
            f"\nRegister State ({fmt}):",
            reg_state,
        ]
        return "\n".join(lines), self.cycle, self.valid

# Tests
def run_tests():
    print("\n--- Running Tests (Datapath) ---")
    print("Program: Y = A·B + C'·D")
    print("  t0=A, t1=B, t2=C, t3=D")

    # --- Assemble program ---
    #   and t4, t0, t1   ; t4 = A & B        opcode=AND, invert=0
    #   and t6, t2, t3   ; t6 = (~C) & D     opcode=AND, invert=1 (C inverted in ALU)
    #   or  t0, t4, t6   ; t0 = t4 | t6 = Y  opcode=OR,  invert=0
    program = [
        ControlUnit.encode(0, 0, 4, 0, 1),
        ControlUnit.encode(0, 1, 6, 2, 3),
        ControlUnit.encode(1, 0, 0, 4, 6),
    ]

    test_cases = [
        # (A, B, C, D, label)
        (1, 1, 0, 1, "A=1 B=1 C=0 D=1 -> Y=1 (1·1 + 1·1)"),
        (0, 1, 1, 1, "A=0 B=1 C=1 D=1 -> Y=0 (0·1 + 0·1)"),
        (1, 0, 1, 1, "A=1 B=0 C=1 D=1 -> Y=0 (0·0 + 0·1)"),
        (0, 0, 0, 1, "A=0 B=0 C=0 D=1 -> Y=1 (0·0 + 1·1)"),
    ]

    for A, B, C, D, label in test_cases:
        print(f"\n  Test: {label}")
        cpu = Datapath()
        cpu.load_registers({0: A, 1: B, 2: C, 3: D})
        for instr in program:
            cpu.execute(instr)
        result, cycles, valid = cpu.get_output("DEC")
        Y = cpu.reg_file.registers[0]
        expected = (A & B) | ((~C & 1) & D)
        status = "PASS" if Y == expected else "FAIL"
        print(f"  Y (t0) = {Y}  Expected = {expected}  [{status}]")

if __name__ == "__main__":
    run_tests()

    try:
        print("\n--- Interactive Mode (Datapath) ---")
        print("Compute Y = A·B + C'·D")
        A = int(input("  A (decimal): "))
        B = int(input("  B (decimal): "))
        C = int(input("  C (decimal): "))
        D = int(input("  D (decimal): "))
        fmt_in = input("Display format (DEC/BIN/HEX): ").upper()

        program = [
            ControlUnit.encode(0, 0, 4, 0, 1),
            ControlUnit.encode(0, 1, 6, 2, 3),
            ControlUnit.encode(1, 0, 0, 4, 6),
        ]

        cpu = Datapath()
        cpu.load_registers({0: A, 1: B, 2: C, 3: D})
        print()
        for instr in program:
            cpu.execute(instr)

        result, cycles, valid = cpu.get_output(fmt_in)
        print(f"\n--- Final State ({fmt_in}) ---")
        print(result)
        print(f"\nY = t0 = {cpu.reg_file.registers[0]}")

    except (ValueError, EOFError):
        print("Invalid input")
