* Sky: see how is is estimated annulus and 8rect, because it must be feeded to fit but depends on fit

# Latter
################################################################################

# Refactor

* SthrelImage discirminator: Sthrel is just a wrapper, join them ?

## Latter feature

* Add fit param button only if fit param are present (see ellipse)
  * Ellipse pick answer should delete fit param: I may give stat in place
* 3h Argument parsing, link with AbismState
* 1h Ellipse (refactor in plugin)
* 2h TightBinary
  * Anisoplanetism = false: otherwise more degenerated, or think of it, give user the choice
* Have a glimps at first guess which is really really important, especially for moffat


### Latter fix
* More options, test my stuff (also on binary)

# Always possible
################################################################################

* Better preference saving, loading
  * Appdir module
  * In util, parse_argument and restart
* Clean code (especially backend)
  * Lint all
  * Beware the magic (FrameText 22, xtermTk, fontsize)
  * Consistent naming
