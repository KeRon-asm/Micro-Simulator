# Micro-Simulator

**A single-cycle processor and memory hierarchy simulator, built from the gates up in Python.**

Micro-Simulator models how a CPU actually runs a program: a 32-bit instruction is fetched, decoded into control signals, executed by an ALU, and written back to a register file, all in a single clock cycle. A separate memory hierarchy simulator shows how that instruction travels from SSD through DRAM and three levels of cache before it reaches the CPU, and what it costs in cycles.

Every component is built on the same foundation: a 32-bit two's complement integer unit with overflow detection and saturation, so values behave like real hardware registers rather than unbounded Python integers.

No external libraries. Python 3.x only.

---

## What's inside

| Component | File | What it does |
|---|---|---|
| **Single-cycle datapath** | `datapath.py` | Fetch → Decode → Execute → Writeback in one cycle, with a per-cycle execution trace |
| **Control unit** | `control_unit.py` | Decodes 32-bit instructions into opcode, register fields, and control signals (`ALU_op`, `RegWrite`, `invert_a`) |
| **ALU** | `alu.py` | 32-bit AND / OR with an input-inversion control signal and a zero flag |
| **Register file** | `register_file.py` | Eight 32-bit registers (`t0`–`t7`) with write-enable gating |
| **Memory hierarchy** | `Memory_Hierarchy_Simulation.py` | SSD → DRAM → L3 → L2 → L1 with configurable capacities, latencies, and LRU / FIFO / random eviction |
| **Integer unit** | `Processor_Parser.py` | 32-bit signed encoding, overflow detection, saturation, and DEC / BIN / HEX output |
| **Logic minimizer** | `combinational_logic.py` | Truth table → canonical SOP/POS → Karnaugh map → simplified Boolean expression, verified against the original table |
| **Demo driver** | `main.py` | Runs a scripted memory access trace and prints the final cache state |

---

## Architecture

```
            ┌──────────────────── one clock cycle ────────────────────┐
 instruction│                                                          │
 ──────────▶│  Control Unit ──▶ control signals (ALU_op, RegWrite,    │
            │       │           invert_a)                              │
            │       ▼                                                  │
            │  Register File ──rs1, rs2──▶ ALU ──result──▶ Register   │
            │   (t0–t7)                  (AND/OR,         File (rd)    │
            │                             ~A, zero)                    │
            └──────────────────────────────────────────────────────────┘

 Memory:   SSD ──20──▶ DRAM ──10──▶ L3 ──4──▶ L2 ──2──▶ L1 ──▶ CPU
                     (transfer latency in cycles, configurable)
```

### Instruction format (32-bit)

| Bits | Field | Meaning |
|---|---|---|
| `[31:30]` | opcode | `00` = AND, `01` = OR |
| `[29]` | invert_a | `1` = invert the first ALU input |
| `[28:24]` | rd | destination register |
| `[23:19]` | rs1 | source register 1 |
| `[18:14]` | rs2 | source register 2 |
| `[13:0]` | — | unused |

---

## How to run

Each component can be run on its own. It runs built-in tests first, then offers an interactive mode.

### Single-cycle datapath
```bash
python3 datapath.py
```
Runs a three-instruction program that computes **Y = A·B + C'·D**, checks it against four test cases, then lets you enter your own A, B, C, D.

```
Program: Y = A·B + C'·D
  and t4, t0, t1    ; t4 = A & B
  and t6, ~t2, t3   ; t6 = (~C) & D
  or  t0, t4, t6    ; t0 = t4 | t6 = Y

  Test: A=1 B=1 C=0 D=1 -> Y=1   [PASS]
  Test: A=0 B=1 C=1 D=1 -> Y=0   [PASS]
  Test: A=1 B=0 C=1 D=1 -> Y=0   [PASS]
  Test: A=0 B=0 C=0 D=1 -> Y=1   [PASS]
```

### Memory hierarchy
```bash
python3 main.py                            # scripted demo trace
python3 Memory_Hierarchy_Simulation.py     # interactive: set sizes, policy, and issue READ/WRITE
```
Shows cold misses propagating data up to L1, L1 hits on re-reads, evictions when L1 fills, and per-level hit/miss counts with total cycle cost.

### Individual components
```bash
python3 control_unit.py        # encode and decode instructions
python3 alu.py                 # run ALU operations
python3 register_file.py       # load and display registers
python3 Processor_Parser.py    # 32-bit conversion and overflow behavior
python3 combinational_logic.py # K-map simplification
```

---

## Design decisions

- **NOT is a control signal, not an instruction.** Rather than adding a third opcode, `invert_a` inverts the first ALU input. This lets `C'·D` run as a single AND instruction and mirrors how real ALUs implement inversion.
- **Every value passes through the 32-bit integer unit.** Register loads, ALU results, and memory writes are all validated by the same parser, so overflow and saturation behave consistently across the whole machine.
- **Write-enable gating on the register file.** Writes only land when the control unit asserts `RegWrite`, matching real datapath behavior.
- **Hierarchy constraints are enforced.** The memory simulator rejects configurations that violate SSD > DRAM > L3 > L2 > L1.
- **Eviction policy is swappable.** LRU, FIFO, and random share one code path built on `OrderedDict`, so policies can be compared on the same access trace.
- **The logic minimizer checks its own work.** After simplifying, it re-evaluates the expression against every row of the original truth table.

---

## Combinational logic example (n=2, SOP)

```
Row 0: 0 0 0
Row 1: 0 1 1
Row 2: 1 0 1
Row 3: 1 1 1

Canonical SOP: F = A'B + AB' + AB
Minterms: m[1, 2, 3]

K-Map (AB):
         B = 0       B = 1
A = 0      0           1
A = 1      1           1

Simplified Expression: F = A + B
Validation passed!
```

Supports 2–4 input variables, truth table validation (binary values, no duplicates, complete combinations), Gray code K-map ordering, and automatic minimal grouping.

---

## Roadmap

- Extend the ISA with arithmetic (ADD/SUB), load/store, and branch instructions
- Connect the datapath's instruction fetch to the memory hierarchy
- Add a visual step-through mode

---

## Author

**Ke'Ron Clark** · B.S. Computer Science, Georgia State University (Dec 2026)
[LinkedIn](https://linkedin.com/in/ke-ron-clark-544589254) · clark.keron.e@gmail.com
