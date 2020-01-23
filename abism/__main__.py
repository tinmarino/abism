# Parse arguments
from abism.util import parse_argument
parse_argument()

# Go
from abism.front.WindowRoot import RootWindow
root_window = RootWindow()
root_window.mainloop()
