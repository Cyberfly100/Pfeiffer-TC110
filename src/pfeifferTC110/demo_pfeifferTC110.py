#%%
import pfeifferTC110
try:
    pump = pfeifferTC110.TC110(autoconnect=False)
    # For testing which port the pump is connected to
    devices = pump.rm.list_resources()
    print(devices)
finally:
    pump.close()

# %%
# Demonstrate pump
import pfeifferTC110

try:
    pump = pfeifferTC110.TC110()
    pump.run_timed(5)
finally:
    pump.close()

# %%
