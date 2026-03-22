import app
import traceback

print("Initiating test...")
a = app.App()
print("App initialized")
a.bg_color = "#FF0000"
a.fg_color = "#00FF00"
try:
    a.apply_theme()
    print("Theme applied successfully")
except Exception as e:
    print("Theme crash:", e)
    traceback.print_exc()
print("Done")
