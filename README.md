# ABISM: Adaptive Background Interferometric Strehl Meter

A graphical user interface (GUI) to measure the Strehl ratio of astronomical images,
i.e. the quality of adaptive optics system on optical telescopes.

# Quickstart

```bash
# Install Abism
pip install -U git+https://github.com/tinmarino/abism 

# Download test resource
wget https://github.com/tinmarino/abism/wiki/crowded.fits

# Launch the GUI
abism crowded.fits
```

# Step by step

__Install:__
```sh
pip install abism
```

or for developpers:
```sh
pip install -U git+https://github.com/tinmarino/abism 
```

__Start:__
from shell:
```sh
abism image.fits
```


__Who:__
For observer astronomers using adaptive optics

__How:__
On the following image, we have a Strehl ratio 50% which is excellent.
Notice the warning that we are reaching the non-linearity detector limit.
We did not take time to measure the error of the measure if non linear, it is very detector dependant.


<img align="center" width=80% src="./abism/doc/abism_v0.900.png">


# More

from ipython:

```python
# Import
from abism.run import run_async

# Launch (sm for Strehl Meter)
sm = run_async('--verbose', '1', './image.fits') 

# Print details
print(sm.state)
```

# Credits

__License__: Do whatever you want with the code

__Authors__: [Julien Girard](https://www.juliengirard.space), [Martin Tourneboeuf](https://tinmarino.github.io)
