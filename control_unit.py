# CSC 4210/6210 - Task 4: Control Unit
# Decodes 32-bit instruction fields and generates control signals
#
# Instruction Encoding (32-bit):
#   [31:30]  opcode   — 00=AND, 01=OR
#   [29]     invert_a — 1=invert first ALU input (encodes NOT in function field)
#   [28:24]  rd       — destination register (5 bits)
#   [23:19]  rs1      — source register 1 (5 bits)
#   [18:14]  rs2      — source register 2 (5 bits)
#   [13:0]   unused

class ControlUnit:
    def __init__(self, instruction):
        self.valid       = 1
        self.instruction = instruction & 0xFFFFFFFF
        self.log         = []

        # Decode instruction fields
        self.opcode   = (self.instruction >> 30) & 0x3
        self.invert_a = (self.instruction >> 29) & 0x1   # function field — NOT behavior
        self.rd       = (self.instruction >> 24) & 0x1F
        self.rs1      = (self.instruction >> 19) & 0x1F
        self.rs2      = (self.instruction >> 14) & 0x1F

        # Generate control signals from opcode
        if self.opcode == 0:    # AND (standard or AND-not via invert_a)
            self.alu_op    = 0
            self.reg_write = 1
        elif self.opcode == 1:  # OR
            self.alu_op    = 1
            self.reg_write = 1
        else:
            self._log(f"Error: Unknown opcode {self.opcode:#04b}")
            self.valid     = 0
            self.alu_op    = 0
            self.reg_write = 0

    def _log(self, msg):
        self.log.append(msg)
        print(msg)

    # Static helper: encode an instruction from its fields
    @staticmethod
    def encode(opcode, invert_a, rd, rs1, rs2):
        instr  = (opcode   & 0x3)  << 30
        instr |= (invert_a & 0x1)  << 29
        instr |= (rd       & 0x1F) << 24
        instr |= (rs1      & 0x1F) << 19
        instr |= (rs2      & 0x1F) << 14
        return instr

    # Return decoded signals — fmt unused but kept consistent with other files
    def get_output(self, fmt="DEC"):
        op_str  = "AND" if self.alu_op == 0 else "OR"
        inv_str = "YES (AND-not)" if self.invert_a else "NO"
        rw_str  = "YES" if self.reg_write else "NO"
        lines = [
            f"  Instruction : 0x{self.instruction:08X}",
            f"  Opcode      : {self.opcode:02b}     ({op_str})",
            f"  invert_a    : {self.invert_a}      ({inv_str})",
            f"  rd          : t{self.rd}",
            f"  rs1         : t{self.rs1}",
            f"  rs2         : t{self.rs2}",
            f"  ALU_op      : {self.alu_op}",
            f"  RegWrite    : {rw_str}",
        ]
        return "\n".join(lines), self.alu_op, self.reg_write

# Tests
def run_tests():
    print("\n--- Running Tests (ControlUnit) ---")
    # Encode the three program instructions and decode them back
    instructions = [
        ControlUnit.encode(0, 0, 4, 0, 1),   # and t4, t0, t1
        ControlUnit.encode(0, 1, 6, 2, 3),   # and t6, ~t2, t3
        ControlUnit.encode(1, 0, 0, 4, 6),   # or  t0, t4, t6
    ]
    descs = [
        "and t4, t0, t1  ; t4 = A & B",
        "and t6, ~t2, t3 ; t6 = (~C) & D",
        "or  t0, t4, t6  ; t0 = t4 | t6",
    ]
    for instr, desc in zip(instructions, descs):
        cu = ControlUnit(instr)
        result, alu_op, reg_write = cu.get_output()
        print(f"\n  {desc}")
        print(result)

run_tests()

try:
    print("\n--- Interactive Mode (ControlUnit) ---")
    op_in  = int(input("Opcode (0=AND, 1=OR): "))
    inv_in = int(input("Invert A (0=No, 1=Yes): "))
    rd_in  = int(input("Destination reg (0-7): "))
    rs1_in = int(input("Source reg 1 (0-7): "))
    rs2_in = int(input("Source reg 2 (0-7): "))

    instr = ControlUnit.encode(op_in, inv_in, rd_in, rs1_in, rs2_in)
    cu = ControlUnit(instr)
    result, alu_op, reg_write = cu.get_output()
    print(f"\nEncoded instruction: 0x{instr:08X}")
    print(result)
except (ValueError, EOFError):
    print("Invalid input")
