


## Interact with the science image

To interact with the image view, you can use

### Mouse

On the image:

* Left button
  * Drag a rectangle to give it as input
  * Click to feed a 40 * 40 pixels region around the click
* Scroll wheel: zoom
* Right button: center the image on the click

On the colorbar:

Drag with left button to modify the image cut

### View menu

Change image:

* Color: with a matplotlib color map
* Scale: a function: true intensity -> visible intensity
* Cuts: change high and low cut according to image statistics
  * Percent: removes outsider keeping only a percentage of pixels near the median intensity
  * Sigma clip: high cut at some factor of the noise (i.e. root mean square of image intensity values)
  * Manual: open a frame for the user to manually enter high and low viewable intensity values. Don't forget to press enter in the entry widget. The colorbar should update adequately


### Pick type

TODO


## Configure Strehl estimation parameters


### Required parameters

Some parameters are required for Strehl estimation. All of them should be positive:

1. Wavelenght (μm): Wavelenght of the image. Example: 2.15 for near infra read
2. Pixel scale (''/pix): Number of arcseconds per pixels. Example: 0.01. It should be inferior to 1, otherwise resolution is too bad to discriminated between an sky corrected image from a sky difracted point spread function (a Gaussian of 1 arcsec)
3. Diameter (m): The diameter of the telescope's primary miroir. Example: 8.0 for the Very Large Telescope (VLT). It should be superior to 1 for the same reason as above.
4. Obstruction (%): The percentage of primary miroir obstructed, usually by the secondary miroir. Example 14.0 for the VLT. It should be inferior to 100, otherwise, the telescope would be fully obstructed and the image black.

Some other parameters are used for the apparent magnitude of object estimation. Those are not required to evaluate the Strehl.

According to the quality of adaptive optics (i.e. Strehl value), the saturation level of the image, the distance between stars and the desired result precision, some parameters should be adjusted by the user / observer, meaning you! Here comes the science:



## Understand output



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
