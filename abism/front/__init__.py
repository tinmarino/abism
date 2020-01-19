"""
    abism.front: Abism Graphical User Interface

1. Verify image parameters
    Have they been parsed successfully from header ?
    From Option pane, 4 parameters are necessary:
        wavelength, pixel scale, diameter and obstruction

2. Pick a star
    or Left click drag a rectangle round
    or Right click on a star

3. Admire the result:
    In Result pane


0KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK0  1
0KKKKKKKKKKKKKKKK ABISM (my_favorite_star.fits) KKKKKKKKKKKKKKKKKKKKK0  2
   ▾ABISM        ▾File  |     ▾Analysis        ▾View         ▾Tools  |  3
   QUIT     RESTART     |                                            |  4
     ▴ImageParameters   |   .................................:  .    |  5
........................|   :                                :  ..   |  6
Info|  ESO/Baade/Unk    |   :                      .lc.      :  ..   |  7
+---+                   |   :   .lc.               ,0O,      :  ..   |  8
  (like this drawing)   |   :   ,0O,                         :  ''   |  9
 ! WARNING saturated !  |   :                                :  ;,   | 10
+-----------------------+   :               ..               :  :,   | 11
Option|                 |   :             ..                 :  l:   | 12
------+                 |   :           .,xK0l'              :  o:   | 13
Wavelenght      1.6     |   :           .KMMMWl.             :  dc   | 14
Pixel Scale     0.20409 |   :          ..d0KKk.              :  kl   | 15
Diameter        6.0     |   :             .. .               :  Oo   | 16
Obstruction     15      |   :    .lc.                        :  0o   | 17
                        |   :    ,0O,                        :  Xd   | 18
------------------------+   :                                :  Nx   | 19
Result|    |↪To sky     |   :................................:  Wx   | 20
------+    +------------|                                            | 21
                        |                                            | 22
Strehl        51.2      +----------------------+---------------------+ 23
Center        32, 78    |                      |                     | 24
Photometry    12 345    |  :       _         : |                     | 25
                        |  :      /  \       : | ......... ......... | 26
                        |  :      |   |      : | :       : :   -   : | 27
                        |  :      |   |      : | :   X   : : | X | : | 28
                        |  :     _.---._     : | :       : :   -   : | 29
                        |  :   .' |   | '.   : | ......... ......... | 30
                        |  :  /   |   |   \  : |                     | 31
                        |  : |    |   |    | : |                     | 32
                        | .:.|....|...|....|.: |                     | 33
________________________|______________________|_____________________| 34
                                                                     \Lin
 00 | 05 | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 | Col \


"""
