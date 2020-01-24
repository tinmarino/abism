# Parse arguments
from abism.util import parse_argument
parse_argument()

# Go
from abism.front.window_root import WindowRoot
root_window = WindowRoot()
root_window.mainloop()
