This is a simple package to communicate with Pfeiffer vaccum hardware (e.g. TC110) via RS485 and the telegram protocol.


### Prerequisites

It is recommended to install into a dedicated environment. If you are using conda, try `conda create -n pfeiffer python git`.
Followed by `conda activate pfeiffer` to enter the new environment.
To install from github, git needs to be installed, which should be taken care of if you used the commands above.

### Installation

Install with `pip install git+https://github.com/Cyberfly100/Pfeiffer-TC110`.

### Try it out

    import pfeifferTC110

    try:
        pump = pfeifferTC110.TC110()
        pump.run_timed(5)
    finally:
        pump.close()
