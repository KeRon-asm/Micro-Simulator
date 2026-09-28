class Parser: 
    def __init__(self, value):
        min_int32 = -(2**31)
        max_int32 = (2**31) -1
        self.overflow = 0
        self.saturated = 0
        #Overflow Handling
        if value > max_int32:
            self.value = max_int32
            self.overflow = 1
            self.saturated = 1
        elif value < min_int32:
            self.value = min_int32
            self.overflow = 1
            self.saturated = 1
        else:
            self.value = value
    def dec_to_bin(self):
        temp = abs(self.value)
        bits = ""
        if temp == 0:
            bits = "0"
        while temp > 0:
            bits = str(temp % 2) + bits
            temp //= 2
        
        # Padding
        while len(bits) < 32:
            bits = "0" + bits

        if self.value < 0:
            inverted = "".join('1' if b == '0' else '0' for b in bits)
            result = ""
            carry = 1
            for i in range(31, -1, -1):
                sum_bit = int(inverted[i]) + carry
                result = str(sum_bit % 2) + result
                carry = sum_bit // 2
            return result
        return bits
    
    def bin_to_hex(self,bin_str):
        hex_digits = "0123456789ABCDEF"
        hex_out = ""
        
        for i in range(0, 32, 4):
            chunk = bin_str[i:i+4]
            
            decimal_val = 0
            if chunk[0] == '1': decimal_val += 8
            if chunk[1] == '1': decimal_val += 4
            if chunk[2] == '1': decimal_val += 2
            if chunk[3] == '1': decimal_val += 1
            
            # Map out
            hex_out += hex_digits[decimal_val]
            
        return "0x" + hex_out
    
    def bin_to_dec(self, bin_str):
        if bin_str[0] == '0':
            return int(bin_str, 2)
        
        inverted = ""
        for bit in bin_str:
            if bit == '0':
                inverted += '1'
            else:
                inverted += '0'
        
        decimal_val = int(inverted, 2) + 1
        return -decimal_val
    def get_output(self, fmt):
        # Internal rep
        b_str = self.dec_to_bin()
        if fmt == "BIN":
            out = b_str
        elif fmt == "HEX":
            out = self.bin_to_hex(b_str)
        else:
            out = self.bin_to_dec(b_str)
            
        return out, self.overflow, self.saturated
# Tests
def run_tests():
    print("\n--- Running Tests ---")
    test_cases = [123, 0, -123, 2147483647, -2147483648, 2147483648, -2147483649]
    for t in test_cases:
        p = Parser(t)
        res, o, s = p.get_output("HEX")
        print(f"In: {t} | Out: {res} | O: {o} | S: {s}")
if __name__ == "__main__":
    run_tests()    
    try:
        val_in = int(input("Enter decimal: "))
        fmt_in = input("Format (DEC, BIN, HEX): ").upper()

        processor = Parser(val_in)
        val_out, ovf, sat = processor.get_output(fmt_in)

        print(f"\nValue: {val_out}")
        print(f"Overflow: {ovf}")
        print(f"Saturated: {sat}")
    except ValueError:
        print("Invalid input")
