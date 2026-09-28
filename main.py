"""
Task 3: Memory Hierarchy Simulation
main.py  —  Demo driver

Run:
    python main.py

Sizes are defined in number of 32-bit instructions.
The hierarchy rule  SSD > DRAM > L3 > L2 > L1  is enforced automatically.
"""

from Memory_Hierarchy_Simulation import MemoryHierarchy

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

CONFIG = dict(
    ssd_cap        = 1024,   # instructions
    dram_cap       = 256,
    l3_cap         = 64,
    l2_cap         = 16,
    l1_cap         = 4,
    lat_ssd   = 20,     # cycles SSD  → DRAM
    lat_dram    = 10,     # cycles DRAM → L3
    lat_l3      = 4,      # cycles L3   → L2
    lat_l2      = 2,      # cycles L2   → L1
    policy         = "lru",  # lru | fifo | random
)

# ──────────────────────────────────────────────────────────────────────────────
# 2. PRINT CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

print("=" * 62)
print("  MEMORY HIERARCHY SIMULATION")
print("  Ke'Ron Clark")
print("=" * 62)
print("  Configuration:")
for k, v in CONFIG.items():
    print(f"    {k:<18} = {v}")
print()

# ──────────────────────────────────────────────────────────────────────────────
# 3. BUILD HIERARCHY & LOAD SSD
# ──────────────────────────────────────────────────────────────────────────────

sim = MemoryHierarchy(**CONFIG)

# Generate 20 fake 32-bit instructions to pre-load into SSD
program = [0xADD10001 + i * 0x1000 for i in range(20)]
sim.load_ssd(program)

# ──────────────────────────────────────────────────────────────────────────────
# 4. INSTRUCTION ACCESS TRACE
# ──────────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 62)
print("  INSTRUCTION ACCESS TRACE")
print("─" * 62)

# --- Read sequence (cold misses → data propagates up) ---
for addr in [0, 1, 2, 3]:
    sim.read(addr)

# --- Re-read addr 0 → should hit L1 now ---
sim.read(0)

# --- Read a new address (L1 eviction will occur) ---
sim.read(5)

# --- Write a new instruction to addr 10 ---
sim.write(10, 0xDEADBEEF)

# --- Read addr 10 → should hit L1 ---
sim.read(10)

# --- Read addr 1 again (may still be in L1 or L2) ---
sim.read(1)

# ──────────────────────────────────────────────────────────────────────────────
# 5. FINAL STATE
# ──────────────────────────────────────────────────────────────────────────────

result, hits, misses = sim.get_output("HEX")
print("\n" + "─" * 62)
print("  FINAL STATE")
print("─" * 62)
print(result)
