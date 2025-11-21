import sys
sys.path.append('.')

from fdbacc import app

print("Rotas registradas no Flask:")
for rule in app.url_map.iter_rules():
    print(f"{rule.rule} - {list(rule.methods)}")