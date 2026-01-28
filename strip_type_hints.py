# strip_type_hints.py
# A script to remove type hints from Python source code files.

import sys
import ast
import astor

class TypeHintRemover(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        node.returns = None
        if node.args.args:
            for arg in node.args.args:
                arg.annotation = None
        return node

    def visit_ClassDef(self, node):
        node.type_params = []
        new_bases = []
        for base in node.bases:
            if isinstance(base, ast.Subscript):
                new_bases.append(base.value)
            else:
                new_bases.append(base)
        node.bases = new_bases
 
            
        # Optionally, process the class body or its attributes
        self.generic_visit(node)  # Continue visiting child nodes
        return node

    def visit_Import(self, node):
        node.names = [n for n in node.names if n.name != 'typing']
        return node if node.names else None

    def visit_ImportFrom(self, node):
        return node if node.module != 'typing' else None

    def visit_Assign(self, node):
        # Remove T = TypeVar('T') assignments
        if (len(node.targets) == 1 and 
            isinstance(node.targets[0], ast.Name) and 
            node.targets[0].id == 'T' and
            isinstance(node.value, ast.Call) and
            isinstance(node.value.func, ast.Name) and
            node.value.func.id == 'TypeVar'):
            return None
        return node

def remove_type_hints(source: str) -> str:
    parsed = ast.parse(source)
    transformed = TypeHintRemover().visit(parsed)
    return astor.to_source(transformed)

def main():
    if len(sys.argv) != 3:
        print("Usage: python strip_type_hints.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, "r") as f:
        source = f.read()

    cleaned_code = remove_type_hints(source)

    with open(output_file, "w") as f:
        f.write(cleaned_code)       

if __name__ == "__main__":
    main()
