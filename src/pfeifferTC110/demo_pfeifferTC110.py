#%%
# For testing the pump functions
import PfeifferTC110
pump = PfeifferTC110.TC110()

#%%
# For testing what the pump identifies as
import visa
rm = visa.ResourceManager('@py')
devices = rm.list_resources()
print(devices)

# %%
# Demonstrate pump
import PfeifferTC110

try:
    pump = PfeifferTC110.TC110()
    pump.run_timed(5)
finally:
    pump.close()

# %%
