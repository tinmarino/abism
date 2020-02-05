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
# Import
from abism.run import run_async

# Launch (sm for Strehl Meter)
sm = run_async('--verbose', '1', './image.fits') 

# Print details
print(sm.state)
```



## Shortcuts

| KeyBind | Command          | Comment |
| ---     | ---              | --- |
| `<C-B>` | **B**ackward     | cube image |
| `<C-D>` | **D**ictionaries | fit parameters and errors |
| `<C-F>` | **F**orward      | cube image |
| `<C-H>` | open **H**eader  | Popup |
| `<C-I>` | **I**mage param  | Toogle Frame |
| `<C-K>` | s**K**y coord    | Toogle anwser coordinate system |
| `<C-M>` | **M**ore option  | Toogle Frame |
| `<C-O>` | **O**pen file    | Popup |
| `<C-R>` | **R**estart      | !! Irreversible !! |


| KeyBind  | Command                | Comment |
| ---      | ---                    | --- |
| `<C-P>B` | **P**ick **B**inary    | Mpl binding |
| `<C-P>N` | **P**ick **N**one      | Mpl binding |
| `<C-P>O` | **P**ick **O**ne       | Mpl binding |
| `<C-P>P` | **P**ick **P**rofile   | Mpl binding |
| `<C-P>S` | **P**ick **S**tat      | Mpl binding |
| `<C-P>T` | **P**ick **T**ight     | Mpl binding |
| `<C-T>D` | **T**ool **D**ebug     | Popup (legacy) |
| `<C-T>H` | **T**ool **H**istogram | Work and display |
| `<C-T>J` | **T**ool **J**upyter   | Popup (futur) |



License: Do whatever you want with the code

Julien Girard, Martin Tourneboeuf.
