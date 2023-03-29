# ABISM: Adaptive Background Interferometric Strehl Meter

A graphical user interface (GUI) to measure the Strehl ratio of astronomical images,
i.e. the quality of adaptive optics system on optical telescopes.

# Quickstart

```bash
# Install Abism
pip install -U git+https://github.com/tinmarino/abism  # or just `pip install abism` for non-developpers

# Download a test image
wget https://github.com/tinmarino/abism/wiki/crowded.fits

# Launch the GUI
abism crowded.fits
```

# Details

On the following image, we have a Strehl ratio 50% which is excellent.
Notice the warning that we are reaching the non-linearity detector limit.
We did not take time to measure the systematic error if intensity is reaching a non linear level, it is very detector dependant.


<img align="center" width=80% src="./abism/doc/abism_v0.900.png">


# Links

* [Paper 2016](https://www.eso.org/sci/libraries/SPIE2016/9909-303.pdf)
* [Slide 2012](https://tinmarino.github.io/?show=abism_slide)


# Credits

__License__: do whatever you want with the code

__Authors__: [Julien Girard](https://www.juliengirard.space), [Martin Tourneboeuf](https://tinmarino.github.io)
