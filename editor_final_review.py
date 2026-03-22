import re

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Enlarge dialog height from 420 to 500
code = code.replace('width=420, height=420', 'width=420, height=500')

# 2. Change X button to save instead of destroy
# Currently: tk.Button(dialog, text="X", command=dialog.destroy, bg=self.bg_color...
code = code.replace('command=dialog.destroy', 'command=lambda: save()')

# 3. Clean up double minsize
code = code.replace('        self.root.minsize(450, 650)\n        self.root.geometry("450x650")\n        self.root.minsize(450, 650)\n', '        self.root.minsize(450, 650)\n        self.root.geometry("450x650")\n')

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Final review adjustments applied.")
