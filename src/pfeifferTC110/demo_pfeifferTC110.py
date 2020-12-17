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
pump = PfeifferTC110.TC110()
try:
    pump.run_timed(15)
finally:
    pump.close()

# %%
