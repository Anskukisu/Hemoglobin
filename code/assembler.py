# Assembler for Hemoglobin (.hmg)
# Compiles into RISC-V, them compiles it into .elf
from comperrors import error
# Assemble
def assemble(AST):
    header = "# File made using Hemoglobin compiler v 1.0.0\n # You are free to redistribute this file \n"
    data_section = [".data", "      # Here we store the variables"]
    allocated_vars = set()
    for line in AST:
        pass
    return AST