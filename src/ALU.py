class ALU:
    """
    Arithmetic Logic Unit για 16-bit επεξεργαστή
    
    Η ALU είναι το "μαθηματικό κέντρο" του επεξεργαστή.
    Παίρνει δύο εισόδους (A και B) και έναν κωδικό λειτουργίας (ALU_Control)
    και επιστρέφει το αποτέλεσμα της πράξης.
    """
    
    # ALU Control Codes (4-bit)
    ALU_ADD = 0b0000    # Πρόσθεση
    ALU_SUB = 0b0001    # Αφαίρεση  
    ALU_AND = 0b0010    # Λογικό AND
    ALU_OR  = 0b0011    # Λογικό OR
    ALU_XOR = 0b0100    # Λογικό XOR
    ALU_EQ  = 0b0101    # Σύγκριση ίσο
    ALU_NE  = 0b0110    # Σύγκριση διαφορετικό
    
    def __init__(self):
        """Αρχικοποίηση ALU"""
        self.last_result = 0
        self.zero_flag = False    # True αν αποτέλεσμα = 0
        self.overflow_flag = False # True αν έγινε overflow
        self.negative_flag = False # True αν αποτέλεσμα < 0 (signed)
        
        # Στατιστικά για debugging
        self.operations_count = 0
        self.operation_history = []
    
    def execute(self, input_a, input_b, alu_control):
        """
        Εκτέλεση ALU λειτουργίας
        
        Args:
            input_a (int): Πρώτη είσοδος (16-bit)
            input_b (int): Δεύτερη είσοδος (16-bit)
            alu_control (int): Κωδικός λειτουργίας (4-bit)
            
        Returns:
            int: Αποτέλεσμα (16-bit)
        """
        # Εξασφαλίζουμε ότι οι είσοδοι είναι 16-bit
        input_a = input_a & 0xFFFF
        input_b = input_b & 0xFFFF
        
        # Εκτέλεση της λειτουργίας
        if alu_control == self.ALU_ADD:
            result = self._add(input_a, input_b)
        elif alu_control == self.ALU_SUB:
            result = self._sub(input_a, input_b)
        elif alu_control == self.ALU_AND:
            result = self._and(input_a, input_b)
        elif alu_control == self.ALU_OR:
            result = self._or(input_a, input_b)
        elif alu_control == self.ALU_XOR:
            result = self._xor(input_a, input_b)
        elif alu_control == self.ALU_EQ:
            result = self._compare_eq(input_a, input_b)
        elif alu_control == self.ALU_NE:
            result = self._compare_ne(input_a, input_b)
        else:
            result = 0  # Άγνωστη λειτουργία
        
        # Ενημέρωση flags
        self._update_flags(result)
        
        # Αποθήκευση στατιστικών
        self.last_result = result
        self.operations_count += 1
        self.operation_history.append({
            'op': self._get_operation_name(alu_control),
            'a': input_a,
            'b': input_b,
            'result': result
        })
        
        return result
    
    def _add(self, a, b):
        """Πρόσθεση 16-bit"""
        result = a + b
        
        # Έλεγχος overflow (αν το αποτέλεσμα > 16-bit)
        if result > 0xFFFF:
            self.overflow_flag = True
        
        return result & 0xFFFF
    
    def _sub(self, a, b):
        """Αφαίρεση 16-bit"""
        result = a - b
        
        # Αν το αποτέλεσμα είναι αρνητικό, το μετατρέπουμε σε unsigned
        if result < 0:
            result = (1 << 16) + result  # Two's complement
        
        return result & 0xFFFF
    
    def _and(self, a, b):
        """Λογικό AND bit προς bit"""
        return (a & b) & 0xFFFF
    
    def _or(self, a, b):
        """Λογικό OR bit προς bit"""
        return (a | b) & 0xFFFF
    
    def _xor(self, a, b):
        """Λογικό XOR bit προς bit"""
        return (a ^ b) & 0xFFFF
    
    def _compare_eq(self, a, b):
        """Σύγκριση ίσο (επιστρέφει 1 αν a==b, 0 αν όχι)"""
        return 1 if a == b else 0
    
    def _compare_ne(self, a, b):
        """Σύγκριση διαφορετικό (επιστρέφει 1 αν a!=b, 0 αν όχι)"""
        return 1 if a != b else 0
    
    def _update_flags(self, result):
        """Ενημέρωση flags βάσει αποτελέσματος"""
        self.zero_flag = (result == 0)
        self.negative_flag = (result & 0x8000) != 0  # MSB = 1
        # Overflow flag ενημερώνεται στις αντίστοιχες λειτουργίες
    
    def _get_operation_name(self, alu_control):
        """Επιστρέφει το όνομα της λειτουργίας"""
        names = {
            self.ALU_ADD: "ADD",
            self.ALU_SUB: "SUB", 
            self.ALU_AND: "AND",
            self.ALU_OR: "OR",
            self.ALU_XOR: "XOR",
            self.ALU_EQ: "EQ",
            self.ALU_NE: "NE"
        }
        return names.get(alu_control, "UNKNOWN")
    
    def get_flags(self):
        """Επιστρέφει τα flags"""
        return {
            'zero': self.zero_flag,
            'overflow': self.overflow_flag,
            'negative': self.negative_flag
        }
    
    def display_status(self):
        """Εμφάνιση κατάστασης ALU"""
        print("┌" + "─" * 50 + "┐")
        print("│" + " " * 20 + "ALU STATUS" + " " * 19 + "│")
        print("├" + "─" * 50 + "┤")
        print(f"│ Last Result: 0x{self.last_result:04X} ({self.last_result:>5})  │")
        print(f"│ Zero Flag:   {'✓' if self.zero_flag else '✗'}                 │")
        print(f"│ Overflow:    {'✓' if self.overflow_flag else '✗'}             │")
        print(f"│ Negative:    {'✓' if self.negative_flag else '✗'}             │")
        print(f"│ Operations:  {self.operations_count:>5}                        │")
        print("└" + "─" * 50 + "┘")
    
    def display_history(self, last_n=5):
        """Εμφάνιση ιστορικού λειτουργιών"""
        print("\n┌" + "─" * 60 + "┐")
        print("│" + " " * 22 + "ALU HISTORY" + " " * 25 + "│")
        print("├" + "─" * 60 + "┤")
        
        history_to_show = self.operation_history[-last_n:] if len(self.operation_history) > last_n else self.operation_history
        
        for i, op in enumerate(history_to_show):
            op_str = f"{op['op']} 0x{op['a']:04X}, 0x{op['b']:04X} → 0x{op['result']:04X}"
            print(f"│ {i+1:2}. {op_str:<50} │")
        
        if not history_to_show:
            print("│" + " " * 22 + "No operations yet" + " " * 19 + "│")
        
        print("└" + "─" * 60 + "┘")
    
    def reset(self):
        """Επαναφορά ALU σε αρχική κατάσταση"""
        self.last_result = 0
        self.zero_flag = False
        self.overflow_flag = False
        self.negative_flag = False
        self.operations_count = 0
        self.operation_history = []


# Κύρια συνάρτηση για command line χρήση
def main():
    """Κύρια συνάρτηση για demo της ALU"""
    print("ALU Demo - RISC-V 16-bit Processor")
    print("=" * 40)
    
    alu = ALU()
    
    print("\n1. Δημιουργία ALU...")
    alu.display_status()
    
    print("\n2. Εκτέλεση μερικών πράξεων...")
    
    # Μερικές δοκιμές
    alu.execute(10, 20, ALU.ALU_ADD)
    alu.execute(100, 50, ALU.ALU_SUB)
    alu.execute(0xFF, 0x0F, ALU.ALU_AND)
    
    print("\n3. Κατάσταση ALU:")
    alu.display_status()
    
    print("\n4. Ιστορικό:")
    alu.display_history()


if __name__ == "__main__":
    main()