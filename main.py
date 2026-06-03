import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import BacktestApp

if __name__ == "__main__":
    app = BacktestApp()
    app.mainloop()
