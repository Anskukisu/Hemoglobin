from compiler import comp
from assembler import assemble
# In VS Code, this is the path, so that's why it won't work for you if you directly run this file.
filename = "file.hmg"
compiled = comp(filename)
print(assemble(compiled))
