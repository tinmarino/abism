# Abism interface documentation

# Contents

  - [Interact with the science image](#Interact with the science image)
    - [Mouse](#Interact with the science image#Mouse)
    - [View menu](#Interact with the science image#View menu)
    - [Pick type](#Interact with the science image#Pick type)
  - [Configure Strehl measurement parameters](#Configure Strehl measurement parameters)
    - [Required parameters](#Configure Strehl measurement parameters#Required parameters)
    - [Fit parameters](#Configure Strehl measurement parameters#Fit parameters)
    - [Sky and Photometry measurement](#Configure Strehl measurement parameters#Sky and Photometry measurement)
      - [Sky](#Configure Strehl measurement parameters#Sky and Photometry measurement#Sky)
      - [Photometry](#Configure Strehl measurement parameters#Sky and Photometry measurement#Photometry)
  - [Understand output](#Understand output)
    - [Textual output](#Understand output#Textual output)
      - [Visual output](#Understand output#Textual output#Visual output)
  - [Shortcuts](#Shortcuts)


## Interact with the science image

To interact with the image view, you can use


### Mouse

On the image:

* __Left button__
  * Drag a rectangle to give it as input
  * Click to feed a 40 * 40 pixels region around the click
* __Scroll wheel__: zoom
* __Right button__: center the image on the click

On the colorbar:

Drag with left button to modify the image cut


### View menu

Change image:

* __Color__: with a matplotlib color map
* __Scale__: a function: true intensity -> visible intensity
* __Cuts__: change high and low cut according to image statistics
  * __Percent__: removes outsider keeping only a percentage of pixels near the median intensity
  * __Sigma clip__: high cut at some factor of the noise (i.e. root mean square of image intensity values)
  * __Manual__: open a frame for the user to manually enter high and low viewable intensity values. Don't forget to press enter in the entry widget. The colorbar should update adequately


### Pick type

In `Analysis` or `Tools` menu button.

Different interaction can be done between the image and Abism backend engine. Those interactions are called `pick type`.

1. __No Pick__: Disable Abism backend interaction
2. __Pick One__: Select one star
3. __Pick Binary__: Select two stars
4. __Pick Tight__: Select two stars, be precise because the center are constrained to be very close the click
5. __Profile__: Draw a line on the image and admire the 1d intensity profile along this line
6. __Stat__: Draw a rectangle and read the pixels statistics in this rectangle
7. __Ellipse__: Draw an ellipse on the image.
  * Strehl will be calculated from this ellipse
  * Not fit is performed: intensity is the max pixel, photometry is the sum of all pixels
  * Keyboard bindings are arrow keys, hjkl, eXpand, rOtate, changeU, changeV


## Configure Strehl measurement parameters
### Required parameters

In the `option` frame, which can be open with the `Image Parameters` button.

Some parameters are required for Strehl measurement. All of them should be positive:

1. __Wavelength (μm)__: Wavelength of the image. Example: 2.15 for near infra read
2. __Pixel scale (''/pix)__: Number of arcseconds per pixels. Example: 0.01. It should be inferior to 1, otherwise resolution is too bad to discriminated between an sky corrected image from a sky diffracted point spread function (PSF) (a Gaussian of 1 arcsec)
3. __Diameter (m)__: The diameter of the telescope's primary mirror. Example: 8.0 for the Very Large Telescope (VLT). It should be superior to 1 for the same reason as above.
4. __Obstruction (%)__: The percentage of primary mirror obstructed, usually by the secondary mirror. Example 14.0 for the VLT. It should be inferior to 100, otherwise, the telescope would be fully obstructed and the image black.

Some other parameters are used for the apparent magnitude of object measurement. Those are not required to evaluate the Strehl.

According to the quality of adaptive optics (i.e. Strehl value), the saturation level of the image, the distance between stars and the desired result precision, some parameters should be adjusted by the user / observer, meaning you! Here comes the science:


### Fit parameters

In `Analysis` menu button.

There are 3 primitive function to fit the PSF. Choosing one or other mostly depend on the Strehl value.

1. __Gaussian__: suitable for Strehl < 20%
2. __Moffat__: suitable for 20% < Strehl < 60%. Warning, the moffat function has two free parameters the `exponent` and the `spread` so it is a little bit degenerated.
3. __Bessel__: suitable for 60% < Strehl. This is the perfect (alias ideal, in space) diffraction pattern.

Note: If you see a diffraction halo around the star, strehl is probably superior to 50%. So do not use Gaussian.

In addition (better say multiplication) to the primitive function, some parameters can be configured:

In `more option` button.

* __Anisotropy__: If checked: Permits the fit function not to be circular adding two parameters: `theta` for the angle of the main axis and `spread_y` which is a second spread factor for the axis perpendicular to the main (hence not necessarily align to the y axis). Note that for moffat, an `exponent_y` is also added
* __Binary same psf__: If checked: In case of a binary fit, assumes that the two stars share the same psf. Which permits a much easier fit.
* __Fit saturated__: If checked: add a parameter (called `saturation`) to the fitted function. Intensity of the fitted profile cannot go higher than this free parameter. If image is NOT saturated, this is a useless parameter, usually resulting in an impossible error measurement (outputting `-1`)


### Sky and Photometry measurement

From `more option` button in `Analisys` menu button

Strehl measurement requires to model the star profile in perfect (i.e. space) conditions. To scale the diffraction pattern of a star, it is required to measure its intensity.
Sky measurement is required for photometric measurement (to be subtracted).

#### Sky

It can be done in different ways:

1. __None__: sky intensity is 0
2. __Manual__: sky intensity is given by user (in a newly spawned entry box)
  * This is useful if the star is not isolated.
3. __8Rectangle__: some rectangles at each cardinal point of the object are used
4. __Annulus__: an annulus around the object is used
5. __Fit__: the sky measurement during the fit (as an additional free parameter)

Note: for annulus and 8rect: the distance to the star

#### Photometry

1. __Fit__: integral of the fit function is used
2. __Ellipse__: an ellipse encircling 99% of the energy is used as an aperture, all pixels in the aperture are summed. (Bad pixels are median filtered). This sum is then divided by 0.99.

Other photometric measurements are experimental.


## Understand output

Abism returns:

1. text answer in the `Result` frame (bottom left).
2. visual answer in the bottom `1D` and `2D` frames


### Textual output

First read the CHI2. An high value means unreliable results, independently from the estimated error.
The current error estimation is mostly performed from fit estimated errors and is unreliable (if CHI2 is high). This is left as a future TODO.
Empirically a CHI2 lower than 10 seems to be reliable.

Your goal is to reduce the CHI2 ! Have a glimpse at fit parameters (button in result frame)

1. If theta error is high: uncheck anisotropy
2. If intensity error is high, image may be saturated (look at 1D profile). In which case, check saturation button


### Visual output

At the bottom of the window, you can see:

1. The 1D profile of (discrete) data and (continuous) fit on the same plot, as well as the supposed ideal profile. The ratio between fit max intensity and ideal max intensity is the Strehl.
2. The 2D profile of the data (left plot) and the fit (right plot)


## Shortcuts

| KeyBind | Command          | Comment |
| ---     | ---              | --- |
| `<C-B>` | **B**ackward     | cube image |
| `<C-D>` | **D**ictionaries | Toogle fit parameters and errors |
| `<C-F>` | **F**orward      | cube image |
| `<C-H>` | open **H**eader  | Toogle popup |
| `<C-I>` | **I**mage param  | Toogle Frame |
| `<C-K>` | s**K**y coord    | Toogle anwser coordinate system |
| `<C-M>` | **M**ore option  | Toogle Frame |
| `<C-O>` | **O**pen file    | Popup |
| `<C-R>` | **R**estart      | !! Irreversible !! |
| `<C-S>` | **S**ave         | Previous (100) results |
| `<C-?>` | **?** What **?** | Toogle current popud md viewer |


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
