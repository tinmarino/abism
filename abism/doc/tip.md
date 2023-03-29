
# Introspection

from ipython:

```python
# Import
from abism.run import run_async

# Launch (sm for Strehl Meter)
sm = run_async('--verbose', '1', './image.fits') 

# Print details
print(sm.state)
```

