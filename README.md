This is a simple package to communicate with Pfeiffer vaccum hardware (e.g. TC110) via RS485 and the telegram protocol.


### Installation

Install with `pip install git+https://github.com/Cyberfly100/Pfeiffer-TC110`.

### Try it out

    import PfeifferTC110

    try:
        pump = PfeifferTC110.TC110()
        pump.run_timed(5)
    finally:
        pump.close()
