from compiler import comp
from assembler import assemble
filename = "file.hmg"
compiled = comp(filename)
print(assemble(compiled))