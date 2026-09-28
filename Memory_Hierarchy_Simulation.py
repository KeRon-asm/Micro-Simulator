# Task 3: Memory Hierarchy Simulation
# SSD -> DRAM -> L3 -> L2 -> L1 -> CPU
from Processor_Parser import Parser
from collections import OrderedDict

class MemoryHierarchy:
    def __init__(self, ssd_cap=1024, dram_cap=256, l3_cap=64, l2_cap=16, l1_cap=4,
                 lat_ssd=20, lat_dram=10, lat_l3=4, lat_l2=2, policy="lru"):
        # Enforce size hierarchy
        self.valid = 1
        if not (ssd_cap > dram_cap > l3_cap > l2_cap > l1_cap):
            print("Error: Must follow SSD > DRAM > L3 > L2 > L1")
            self.valid = 0
            return

        # Capacities
        self.caps = {
            "SSD": ssd_cap, "DRAM": dram_cap,
            "L3": l3_cap, "L2": l2_cap, "L1": l1_cap
        }
        # Latencies (cycles to transfer OUT of each level)
        self.latencies = {
            "SSD": lat_ssd, "DRAM": lat_dram,
            "L3": lat_l3,   "L2": lat_l2, "L1": 1
        }
        self.policy  = policy.lower()
        self.levels  = ["SSD", "DRAM", "L3", "L2", "L1"]

        # Storage: each level holds OrderedDict {addr: 32-bit instruction}
        self.store = {lvl: OrderedDict() for lvl in self.levels}

        # Hit / miss counters per level
        self.hits   = {lvl: 0 for lvl in self.levels}
        self.misses = {lvl: 0 for lvl in self.levels}

        self.clock = 0
        self.log   = []

    # Logging
    def _log(self, msg):
        entry = f"[Cycle {self.clock:>4}] {msg}"
        self.log.append(entry)
        print(entry)

    # Advance clock by n cycles
    def _tick(self, n=1):
        self.clock += n

    # Evict one entry from a level, return (addr, instr)
    def _evict(self, lvl):
        import random
        store = self.store[lvl]
        if self.policy in ("lru", "fifo"):
            addr, instr = store.popitem(last=False)
        else:
            addr  = random.choice(list(store.keys()))
            instr = store.pop(addr)
        return addr, instr

    # Write instruction into a level, evicting if full
    def _store_at(self, lvl, addr, instr):
        store = self.store[lvl]
        evicted = None
        if addr in store:
            if self.policy == "lru":
                store.move_to_end(addr)
            store[addr] = instr
        else:
            if len(store) >= self.caps[lvl]:
                evicted = self._evict(lvl)
            store[addr] = instr
        return evicted

    # Transfer data from one level to the next, advancing the clock
    def _transfer(self, src, dst, addr, instr):
        cycles = self.latencies[src]
        self._log(f"  -> Transfer: {src} -> {dst}  addr={addr}  [{cycles} cycle(s)]")
        self._tick(cycles)
        evicted = self._store_at(dst, addr, instr)
        self._log(f"   Arrived at {dst}")
        if evicted:
            self._log(f"    Evicted from {dst}: addr={evicted[0]}")

    # Promote data from found_level up to L1, one hop at a time
    def _promote(self, addr, instr, found_idx):
        for i in range(found_idx, len(self.levels) - 1):
            src = self.levels[i]
            dst = self.levels[i + 1]
            self._transfer(src, dst, addr, instr)

    # Read: search L1 -> SSD, promote on miss
    def read(self, addr):
        if not self.valid:
            return None
        self._log(f"READ  addr={addr}")
        # Search closest to CPU first
        for idx in range(len(self.levels) - 1, -1, -1):
            lvl   = self.levels[idx]
            store = self.store[lvl]
            if addr in store:
                instr = store[addr]
                if self.policy == "lru":
                    store.move_to_end(addr)
                self.hits[lvl] += 1
                self._log(f"  Hit in {lvl}: addr={addr}")
                # Promote to L1 if not already there
                if idx < len(self.levels) - 1:
                    self._promote(addr, instr, idx)
                return instr
            self.misses[lvl] += 1
        self._log(f"  addr={addr} not found in hierarchy")
        return None

    # Write: validate with Parser, write to L1, write-back down to SSD
    def write(self, addr, value):
        if not self.valid:
            return
        p = Parser(value)
        instr, ovf, sat = p.get_output("DEC")
        if ovf:
            self._log(f"WRITE addr={addr}  Overflow/Saturated -> stored as {instr}")
        else:
            self._log(f"WRITE addr={addr}  data={value}")

        # Write to L1 first
        evicted = self._store_at("L1", addr, instr)
        self._log(f"  Written to L1")
        if evicted:
            self._log(f"    Evicted from L1: addr={evicted[0]}")

        # Write-back down to SSD
        for i in range(len(self.levels) - 2, -1, -1):
            dst = self.levels[i]
            src = self.levels[i + 1]
            self._transfer(src, dst, addr, instr)
            self._log(f"  Write-back to {dst} complete")

    # Load initial instructions into SSD
    def load_ssd(self, instructions):
        for addr, val in enumerate(instructions):
            p = Parser(val)
            instr, _, _ = p.get_output("DEC")
            self.store["SSD"][addr] = instr
        self._log(f"SSD loaded with {len(instructions)} instruction(s)")

    # Return final state, fmt controls how instruction values are displayed
    def get_output(self, fmt):
        total_hits   = sum(self.hits.values())
        total_misses = sum(self.misses.values())
        lines = []
        lines.append(f"Cycles: {self.clock} | Total Hits: {total_hits} | Total Misses: {total_misses}")
        for lvl in self.levels:
            occ   = len(self.store[lvl])
            cap   = self.caps[lvl]
            h     = self.hits[lvl]
            m     = self.misses[lvl]
            lines.append(f"\n{lvl} ({occ}/{cap})  Hits: {h}  Misses: {m}")
            for addr, instr in list(self.store[lvl].items())[:6]:
                p = Parser(instr)
                disp, _, _ = p.get_output(fmt)
                lines.append(f"  addr={addr:>4} -> {disp}")
            if occ > 6:
                lines.append(f"  ... ({occ - 6} more)")
        return "\n".join(lines), total_hits, total_misses


# Tests
def run_tests():
    print("\n--- Running Tests ---")
    sim = MemoryHierarchy()
    program = [0x00A00000 + i * 0x100 for i in range(10)]
    sim.load_ssd(program)

    test_cases = [
        ("READ",  0,  None),
        ("READ",  1,  None),
        ("READ",  2,  None),
        ("READ",  0,  None),      # L1 hit
        ("WRITE", 5,  0x00BEEF00),
        ("READ",  5,  None),      # L1 hit after write
    ]
    for op, addr, val in test_cases:
        if op == "READ":
            sim.read(addr)
        else:
            sim.write(addr, val)

    result, hits, misses = sim.get_output("HEX")
    print(f"\n--- Final State (HEX) ---")
    print(result)
    print(f"\nTotal Hits: {hits} | Total Misses: {misses}")

if __name__ == "__main__":
    #run_tests()

    try:
        print("\n--- Interactive Mode ---")
        ssd_in  = int(input("SSD capacity (instructions):  "))
        dram_in = int(input("DRAM capacity (instructions): "))
        l3_in   = int(input("L3 capacity (instructions):   "))
        l2_in   = int(input("L2 capacity (instructions):   "))
        l1_in   = int(input("L1 capacity (instructions):   "))
        pol_in  = input("Eviction policy (lru/fifo/random): ").lower()
        fmt_in  = input("Display format (DEC/BIN/HEX): ").upper()

        sim = MemoryHierarchy(ssd_in, dram_in, l3_in, l2_in, l1_in, policy=pol_in)
        if sim.valid:
            num = int(input("How many instructions to load into SSD? "))
            program = [0xADD10001 + i * 0x1000 for i in range(num)]
            sim.load_ssd(program)

            while True:
                op = input("\nOperation (READ/WRITE/DONE): ").upper()
                if op == "DONE":
                    break
                elif op == "READ":
                    addr = int(input("  Address: "))
                    sim.read(addr)
                elif op == "WRITE":
                    addr = int(input("  Address: "))
                    val  = int(input("  Value (decimal): "))
                    sim.write(addr, val)
                else:
                    print("  Unknown operation")

            result, hits, misses = sim.get_output(fmt_in)
            print(f"\n--- Final State ({fmt_in}) ---")
            print(result)
            print(f"\nTotal Hits: {hits} | Total Misses: {misses}")

    except (ValueError, EOFError):
        print("Invalid input")
