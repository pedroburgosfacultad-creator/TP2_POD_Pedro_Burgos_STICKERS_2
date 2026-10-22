"""Actualiza el código incluido en la guía; ejecutar desde cualquier carpeta."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
modules = []
for file in sorted((ROOT / 'src').glob('*.py')):
    source = file.read_text(encoding='utf-8-sig')
    tree = ast.parse(source)
    symbols = []
    def add(node, parent=''):
        name = f'{parent}.{node.name}' if parent else node.name
        symbols.append({'name':name,'kind':'clase' if isinstance(node,ast.ClassDef) else ('método' if parent else 'función'),'start':node.lineno,'end':node.end_lineno,'doc':ast.get_docstring(node) or '', 'signature':source.splitlines()[node.lineno-1].strip()})
        if isinstance(node,ast.ClassDef):
            for child in node.body:
                if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef)): add(child,name)
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.ClassDef)): add(node)
    modules.append({'name':file.name,'source':source,'symbols':symbols,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
tests=[]
for file in sorted((ROOT/'tests').glob('test_*.py')):
    source=file.read_text(encoding='utf-8-sig')
    cases=[{'name':n.name,'line':n.lineno} for n in ast.walk(ast.parse(source)) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    tests.append({'name':file.name,'source':source,'cases':cases})
def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args],text=True,encoding='utf-8').strip()
payload={'modules':modules,'tests':tests,'commit':git('rev-parse','HEAD'),'history':git('log','-10','--format=%h %s').splitlines(),'testCount':sum(len(t['cases']) for t in tests),'docs':{name:(ROOT/name).read_text(encoding='utf-8-sig') for name in ['README.md','data/README.md','tests/README.md','docs/INFORME_FINAL.md','requirements.txt','.gitignore']}}
(HERE/'src'/'project.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(modules)} módulos, {sum(len(m["symbols"]) for m in modules)} símbolos, {payload["testCount"]} tests inventariados.')
