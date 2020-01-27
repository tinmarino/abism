# ABISM : Adaptive Background Interferometric Strehl Meter


__Install:__
```sh
pip install -U git+https://github.com/tinmarino/abism 
```

__Start:__

from shell:
```sh
abism image.fits
```

__What:__
A graphical user interface (GUI) to measure the strehl ratio.
Meaning the quality (.fits) image from a telescope with adaptive optics.


__Who:__
For observer astronomers using adaptive optics

__How:__

On the following image, we have a Strehl ratio 50% which is excellent.
Notice the warning that we are reaching the non-linearity detector limit.
We did not take time to measure the error of the measure if non linear, it is very detector dependant.


<img  align="center" width=80% src="./abism/doc/abism_v0.900.png">


__More:__

from ipython:
```python
from abism.run import run_async; sm = run_async()
```

```python
import pprint; pp = pprint.PrettyPrinter(indent=4); pp.pprint(sm.state)
```



License: Do whatever you want with the code

Julien Girard, Martin Tourneboeuf.
