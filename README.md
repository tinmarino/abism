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

| KeyBind  | Command     | Comment |
| ---      | ---         | --- |
| `<C-H>`  | open Header | Popup |
| `<C-I>`  | Image Param | Toogle Frame |
| `<C-M>`  | More Option | Toogle Frame |
| `<C-O>`  | Open file   | Popup |
| `<C-R>`  | Restart     | !! Irreversible !! |


| KeyBind  | Command        | Comment |
| ---      | ---            | --- |
| `<C-P>B` | Pick Binary    | Mpl binding |
| `<C-P>N` | Pick None      | Mpl binding |
| `<C-P>P` | Pick One       | Mpl binding |
| `<C-P>P` | Pick Profile   | Mpl binding |
| `<C-P>S` | Pick Stat      | Mpl binding |
| `<C-P>T` | Pick Tight     | Mpl binding |
| `<C-T>D` | Tool Debug     | Popup (legacy) |
| `<C-T>H` | Tool Histogram | Work and display |
| `<C-T>J` | Tool Jupyter   | Popup (futur) |



License: Do whatever you want with the code

Julien Girard, Martin Tourneboeuf.
