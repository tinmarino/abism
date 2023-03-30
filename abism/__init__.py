"""
      Adaptative Background Interferometric Strehl Meter,
                     A Software made by
            Julien Girard and Martin Tourneboeuf

                          Licence
         Do whatever you want, want whatever you do

Install, choose:
    1. pip install abism
    2. pip install --user -U git+https://github.com/tinmarino/abism
    3. git clone https://github.com/tinmarino/abism abism_source && cd abism_source

Run, choose:
    1. sh> abism
    2. sh> [bash | python] path/to/clone/abism.py
    3. sh> python -m abism
    4. py> from abism import __main__
    5. py> from abism.run import run_sync; run_sync()
    6.ipy> from abism.run import run_async; sm = run_async()

They are all equivalent except the last one

More:
    help(abism.front)  # GUI info
    help(abism.back)  # Strehl estimation info

"""
__version__ = '0.915'
