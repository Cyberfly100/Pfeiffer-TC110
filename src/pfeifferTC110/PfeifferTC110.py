# %%
import pyvisa as visa
from pyvisa.constants import StopBits, Parity
import logging
logging.basicConfig(filename='TC110.log', encoding='utf-8', level=logging.WARNING)
from time import sleep

class TC110:
    def __init__(self, device_id=1, port=None, autoconnect=True):
        self.device_id = self._format_id(device_id)
        self.communication = {'BAUDRATE' : 9600,
                              'DATA_BITS' : 8,
                              'PARITY' : Parity.none,
                              'START_BITS' : 1,
                              'STOP_BITS' : StopBits.one}
        self.rm = visa.ResourceManager('@py')
        self.devices = self.rm.list_resources()
        if port == None:
            if len(self.devices)>0:
                self.port = self.devices[0]
            else:
                raise Exception('No device connected or not de-initialized. Try connecting/turning on the pump or restarting the python kernel.')
        else:
            self.port = port
        self.data_types = {0:{'description':'False / true', 'length':'06', 'example':'000000 / 111111'},
                          1:{'description':'Positive integer number', 'length':'06', 'example':'000000 to 999999'},
                          2:{'description':'Positive fixed comma number', 'length':'06', 'example':'001571' 'equal to 15,71'},
                          4:{'description':'Symbol chain', 'length':'06', 'example':'TC_400'},
                          7:{'description':'Positive integer number', 'length':'03', 'example':'000 to 999'},
                          11:{'description':'Symbol chain', 'length':'16', 'example':'BrezelBier&Wurst'}}
        self.commands = {'Heating': {'number': '001',  'description': 'Heating', 'data type': 0, 'access': 'RW', 'min': 0, 'max': 1, 'default': 0, 'non-volatile': True},
                    'Standby': {'number': '002',  'description': 'Standby', 'data type': 0, 'access': 'RW', 'min': 0, 'max': 1, 'default': 0, 'non-volatile': True},
                    'RUTimeCtrl': {'number': '004',  'description': 'Run-up time control', 'data type': 0, 'access': 'RW', 'min': 0, 'max': 1, 'default': 1, 'non-volatile': True},
                    'ErrorAckn': {'number': '009',  'description': 'Error acknowledgement', 'data type': 0, 'access': 'W', 'min': 1, 'max': 1, 'default': 1, 'non-volatile': False},
                    'PumpgStatn': {'number': '010',  'description': 'Pumping station', 'data type': 0, 'access': 'RW', 'min': 0, 'max': 1, 'default': 0, 'non-volatile': True},
                    'EnableVent': {'number': '012',  'description': 'Enable venting', 'data type': 0, 'access': 'RW', 'min': 0, 'max': 1, 'default': 0, 'non-volatile': True},
                    'CfgSpdSwPt': {'number': '017',  'description': 'Configuration rotation speed switch point', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 1, 'default': 0, 'non-volatile': True},
                    'Cfg_DO2': {'number': '019',  'description': 'Configuration output DO2', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 1, 'default': 0, 'non-volatile': True},
                    'MotorPump': {'number': '023',  'description': 'Motor pump', 'data type': 0, 'access': 'RW', 'min': 0, 'max': 1, 'default': 1, 'non-volatile': True},
                    'Cfg_DO1': {'number': '024',  'description': ' Configuration output DO1', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 15, 'default': 0, 'non-volatile': True},
                    'OpMode_BKP': {'number': '025',  'description': 'Operation mode backing pump', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 2, 'default': 0, 'non-volatile': True},
                    'SpdSetMode': {'number': '026',  'description': 'Rotation speed setting mode', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 1, 'default': 0, 'non-volatile': True},
                    'GasMode': {'number': '027',  'description': ' Gas mode', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 2, 'default': 0, 'non-volatile': True},
                    'VentMode': {'number': '030',  'description': 'Venting mode', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 2, 'default': 0, 'non-volatile': True},
                    'Cfg_Acc_A1': {'number': '035',  'description': 'Configuration accessory connection A1', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 8, 'default': 0, 'non-volatile': True},
                    'Cfg_Acc_B1': {'number': '036',  'description': 'Configuration accessory connection B1', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 8, 'default': 1, 'non-volatile': True},
                    'Cfg_Acc_A2': {'number': '037',  'description': 'Configuration accessory connection A2', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 8, 'default': 3, 'non-volatile': True},
                    'Cfg_Acc_B2': {'number': '038',  'description': 'Configuration accessory connection B2', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 8, 'default': 2, 'non-volatile': True},
                    'SealingGas': {'number': '050',  'description': 'Sealing gas', 'data type': 0, 'access': 'RW', 'min': 0, 'max': 1, 'default': 0, 'non-volatile': True},
                    'Cfg_AO1': {'number': '055',  'description': ' Configuration output AO1', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 4, 'default': 0, 'non-volatile': True},
                    'CtrlViaInt': {'number': '060',  'description': 'Control via interface', 'data type': 7, 'access': 'RW', 'min': 1, 'max': 255, 'default': 1, 'non-volatile': True},
                    'IntSelLckd': {'number': '061',  'description': 'Interface selection locked', 'data type': 0, 'access': 'RW', 'min': 0, 'max': 1, 'default': 0, 'non-volatile': True},
                    'Cfg_DI1': {'number': '062',  'description': 'Configuration input DI1', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 6, 'default': 1, 'non-volatile': True},
                    'Cfg_DI2': {'number': '063',  'description': 'Configuration input DI2', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 6, 'default': 2, 'non-volatile': True},
                    'RemotePrio': {'number': '300',  'description': 'Remote priority', 'data type': 0, 'access': 'R', 'min': 0, 'max': 1, 'default': None, 'non-volatile': False},
                    'SpdSwPtAtt': {'number': '302',  'description': 'Rotation speed switch point attained', 'data type': 0, 'access': 'R', 'min': 0, 'max': 1, 'default': None, 'non-volatile': False},
                    'Error_code ': {'number': '303',  'description': 'Error code', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': False},
                    'OvTempElec': {'number': '304',  'description': 'Excess temperature electronic drive unit', 'data type': 0, 'access': 'R', 'min': 0, 'max': 1, 'default': None, 'non-volatile': False},
                    'OvTempPump': {'number': '305',  'description': ' Excess temperature pump', 'data type': 0, 'access': 'R', 'min': 0, 'max': 1, 'default': None, 'non-volatile': False},
                    'SetSpdAtt': {'number': '306',  'description': 'Set rotation speed attained', 'data type': 0, 'access': 'R', 'min': 0, 'max': 1, 'default': None, 'non-volatile': False},
                    'PumpAccel': {'number': '307',  'description': 'Pump accelerates', 'data type': 0, 'access': 'R', 'min': 0, 'max': 1, 'default': None, 'non-volatile': False},
                    'SetRotSpd': {'number': '308',  'description': 'Set rotation speed (Hz)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 999999, 'default': None, 'non-volatile': False},
                    'ActualSpd': {'number': '309',  'description': 'Active rotation speed (Hz)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 999999, 'default': None, 'non-volatile': False},
                    'DrvCurrent': {'number': '310',  'description': 'Drive current (A)', 'data type': 2, 'access': 'R', 'min': 0, 'max': 1, 'default': None, 'non-volatile': False},
                    'OpHrsPump': {'number': '311',  'description': 'Operating hours pump (h)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 9999.99, 'default': None, 'non-volatile': True},
                    'Fw_version': {'number': '312',  'description': 'Firmware version electronic drive unit', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': False},
                    'DrvVoltage': {'number': '313',  'description': 'Drive voltage (V)', 'data type': 2, 'access': 'R', 'min': 0, 'max': 9999.99, 'default': None, 'non-volatile': False},
                    'OpHrsElec': {'number': '314',  'description': 'Operating hours electronic drive unit (h)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 65535, 'default': None, 'non-volatile': True},
                    'Nominal_Spd': {'number': '315',  'description': 'Nominal rotation speed (Hz)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 999999, 'default': None, 'non-volatile': False},
                    'DrvPower': {'number': '316',  'description': 'Drive power (W)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 999999, 'default': None, 'non-volatile': False},
                    'PumpCylces': {'number': '319',  'description': 'Pump cycles', 'data type': 1, 'access': 'R', 'min': 0, 'max': 65535, 'default': None, 'non-volatile': True},
                    'TempElec': {'number': '326',  'description': 'Temperature electronic (°C)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 999999, 'default': None, 'non-volatile': False},
                    'TempPmpBot': {'number': '330',  'description': 'Temperature pump bottom part (°C)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 999999, 'default': None, 'non-volatile': False},
                    'AccelDecel': {'number': '336',  'description': 'Acceleration / Deceleration (rpm/s)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 999999, 'default': None, 'non-volatile': False},
                    'Pressure': {'number': '340',  'description': 'Active pressure value (mbar)', 'data type': 7, 'access': 'R', 'min': 1E-10, 'max': 1E3, 'default': None, 'non-volatile': False},
                    'TempBearng': {'number': '342',  'description': 'Temperature bearing (°C)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 999999, 'default': None, 'non-volatile': False},
                    'TempMotor': {'number': '346',  'description': 'Temperature motor (°C)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 999999, 'default': None, 'non-volatile': False},
                    'ElecName': {'number': '349',  'description': 'Name of electronic drive unit', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': False},
                    'Ctr_Name': {'number': '350',  'description': 'Type of display and control unit', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': False},
                    'Ctr_Software': {'number': '351',  'description': 'Software of display and control unit', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': False},
                    'HW_Version': {'number': '354',  'description': 'Hardware version electronic drive unit', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': False},
                    'ErrHist1': {'number': '360',  'description': 'Error code history, pos. 1', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': True},
                    'ErrHist2': {'number': '361',  'description': 'Error code history, pos. 2', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': True},
                    'ErrHist3': {'number': '362',  'description': 'Error code history, pos. 3', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': True},
                    'ErrHist4': {'number': '363',  'description': 'Error code history, pos. 4', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': True},
                    'ErrHist5': {'number': '364',  'description': 'Error code history, pos. 5', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': True},
                    'ErrHist6': {'number': '365',  'description': 'Error code history, pos. 6', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': True},
                    'ErrHist7': {'number': '366',  'description': 'Error code history, pos. 7', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': True},
                    'ErrHist8': {'number': '367',  'description': 'Error code history, pos. 8', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': True},
                    'ErrHist9': {'number': '368',  'description': 'Error code history, pos. 9', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': True},
                    'ErrHist10': {'number': '369',  'description': 'Error code history, pos. 10', 'data type': 4, 'access': 'R', 'min': None, 'max': None, 'default': None, 'non-volatile': True},
                    'SetRotSpd_rpm': {'number': '397',  'description': 'Set rotation speed (rpm)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 999999, 'default': None, 'non-volatile': False},
                    'ActualSpd_rpm': {'number': '398',  'description': 'Actual rotation speed (rpm)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 999999, 'default': None, 'non-volatile': False},
                    'NominalSpd_rpm': {'number': '399',  'description': 'Nominal rotation speed (rpm)', 'data type': 1, 'access': 'R', 'min': 0, 'max': 999999, 'default': None, 'non-volatile': False},
                    'RUTimeSVal': {'number': '700',  'description': 'Set value run-up time (min)', 'data type': 1, 'access': 'RW', 'min': 1, 'max': 120, 'default': 8, 'non-volatile': True},            
                    'SpdSwPt1': {'number': '701',  'description': 'Rotation speed switch point 1 (%)', 'data type': 1, 'access': 'RW', 'min': 50, 'max': 97, 'default': 80, 'non-volatile': True},
                    'SpdSVal': {'number': '707',  'description': 'Set value in rot. speed setting mode (%)', 'data type': 2, 'access': 'RW', 'min': 20, 'max': 100, 'default': 50, 'non-volatile': True},
                    'PwrSVal': {'number': '708',  'description': 'Set value power consumption (%)', 'data type': 7, 'access': 'RW', 'min': 10, 'max': 100, 'default': 100, 'non-volatile': True},
                    'SwOff BKP': {'number': '710',  'description': 'Switching off threshold backing pump in intermittend mode (W)', 'data type': 1, 'access': 'RW', 'min': 0, 'max': 1000, 'default': 0, 'non-volatile': True},
                    'SwOn BKP': {'number': '711',  'description': 'Switching on threshold backing pump in intermittend mode (W)', 'data type': 1, 'access': 'RW', 'min': 0, 'max': 1000, 'default': 0, 'non-volatile': True},
                    'StdbySVal': {'number': '717',  'description': 'Set value rotation speed at standby (%)', 'data type': 2, 'access': 'RW', 'min': 20, 'max': 100, 'default': 66.7, 'non-volatile': True},
                    'SpdSwPt2': {'number': '719',  'description': 'Rotation speed switch point 2 (%)', 'data type': 1, 'access': 'RW', 'min': 5, 'max': 97, 'default': 20, 'non-volatile': True},
                    'VentSpd': {'number': '720',  'description': 'Venting rot. speed at delayed venting (%)', 'data type': 7, 'access': 'RW', 'min': 40, 'max': 98, 'default': 50, 'non-volatile': True},
                    'VentTime': {'number': '721',  'description': 'Venting time at delayed venting (s)', 'data type': 1, 'access': 'RW', 'min': 6, 'max': 3600, 'default': 3600, 'non-volatile': True},
                    'Gaugetype': {'number': '738',  'description': 'Type of pressure gauge', 'data type': 4, 'access': 'RW', 'min': None, 'max': None, 'default': None, 'non-volatile': False},
                    'NomSpdConf': {'number': '777',  'description': 'Nominal rotation speed confirmation (Hz)', 'data type': 1, 'access': 'RW', 'min': 0, 'max': 1500, 'default': 0, 'non-volatile': True},
                    'Param_set': {'number': '794',  'description': 'Parameterset', 'data type': 7, 'access': 'RW', 'min': 0, 'max': 1, 'default': 0, 'non-volatile': False},
                    'Servicelin': {'number': '795',  'description': 'Insert service line', 'data type': 7, 'access': 'RW', 'min': None, 'max': None, 'default': 795, 'non-volatile': False},
                    'RS485Adr': {'number': '797',  'description': 'RS485 device address', 'data type': 1, 'access': 'RW', 'min': 1, 'max': 255, 'default': 1, 'non-volatile': True}}
        if autoconnect:
            self.connect(self.device_id, self.port)

    def connect(self, device_id=1, port=None):
        if port is not None:
            self.port = port        
        self.device_id = self._format_id(device_id)
        if self.port in self.devices:
            self.inst = self.rm.open_resource(self.port, baud_rate=self.communication["BAUDRATE"], data_bits=self.communication["DATA_BITS"], parity=self.communication["PARITY"], stop_bits=self.communication["STOP_BITS"])
            self.inst.write_termination = '\r'
            # try communicating and try other ports in self.devices if unsuccessful. If all fails, raise Exception('No Pfeiffer device found.').
        else:
            raise Exception('No Pfeiffer device found.')
    
    @classmethod
    def _pad_payload(cls, payload, length):
        payload = str(payload)
        if len(payload) >= length:
            return payload
        else:
            return cls._pad_payload('0'+payload, length)
    @classmethod
    def _format_id(cls, id):
        if type(id) not in [str,int]:
            raise TypeError(f'ID should be an integer between 1 and 255. {type(id)} was given.')
        if int(id) > 255 or int(id) < 1:
            raise ValueError(f'ID should be an integer between 1 and 255. {id} was given.')
        formatted_id = cls._pad_payload(str(int(id)),3)
        return formatted_id
    @classmethod
    def _calculate_checksum(cls, message_string):
        #Could also just attempt conversion with message_string = str(message_string)
        if type(message_string)==str:
            checksum = cls._pad_payload(str(sum(message_string.encode('ascii')) % 256),3)
            return checksum
        else:
            raise TypeError(f'Expected input of type string but received {type(message_string)}.')
    @classmethod
    def _received_ok(cls, received_string):
        if type(received_string)==str:
            bool_result = cls._calculate_checksum(received_string[:-3])==received_string[-3:]
        else:
            raise TypeError(f'Expected input of type string but received {type(received_string)}.')
        return bool_result

    # def receive_message_backup(self):
    #     response_header = self.inst.read_bytes(10)
    #     payload_length = int(response_header[-2:])
    #     payload, checksum = self.inst.read_bytes(
    #         payload_length), self.inst.read_bytes(3)
    #     if not self.received_ok(response_header+payload+checksum):
    #         warnings.warn('Checksum error.')
    #         return None
    #     else:
    #         return payload

    def receive_message(self):
        full_response = self.inst.read(termination='\r')
        logging.debug(f'Received: {full_response}')
        if not self._received_ok(full_response):
            logging.warning('Checksum error.')
            return None
        else:
            device_id = full_response[:3]
            action = full_response[4]
            param_number = full_response[5:8]
            payload_length = int(full_response[8:10])
            payload = full_response[10:-3]
            if payload_length != len(payload):
                logging.warning('Payload length error.')
                return None
            else:
                message = {'device_id':device_id, 'action' : action, 'param_number' : param_number, 'payload_length' : payload_length, 'payload' : payload}
                return message

    def send_message(self, command, device_id=None, query_only=True, payload='=?'):
        if device_id == None:
            device_id = self.device_id
        else:
            device_id = self._format_id(device_id)
        param_number = str(command["number"])
        action = '00' if query_only else '10'
        payload_length = '02' if query_only else self.data_types[command["data type"]]["length"]
        message_string = device_id+action+param_number+payload_length+payload
        checksum = self._calculate_checksum(message_string)
        full_message = message_string+checksum
        logging.debug(f'Sending: {full_message}')
        self.inst.write(full_message)
        return full_message

    def get_pressure(self, device_id=None):        
        self.send_message(command=self.commands["Pressure"], device_id=device_id)
        message = self.receive_message()
        if message:
            #FIXME check for error messages from pump
            return message['payload']
        else:
            logging.warning('Pressure not received sucessfully.')
            return None

    def get_speed(self, device_id=None):
        self.send_message(command=self.commands["ActualSpd"], device_id=device_id)
        message = self.receive_message()
        if message:
            #FIXME check for error messages from pump
            return int(message["payload"])
        else:
            logging.warning('Speed not received sucessfully.')
            return None

    def get_power(self, device_id=None):
        self.send_message(command=self.commands["DrvPower"], device_id=device_id)
        message = self.receive_message()
        if message:
            #FIXME check for error messages from pump
            return int(message["payload"])
        else:
            logging.warning('Power not received sucessfully.')
            return None

    def get_current(self, device_id=None):
        self.send_message(command=self.commands["DrvCurrent"], device_id=device_id)
        message = self.receive_message()
        if message:
            #FIXME check for error messages from pump
            return float(message["payload"])
        else:
            logging.warning('Current not received sucessfully.')
            return None

    def start(self, device_id=None):
        self.send_message(command=self.commands["PumpgStatn"], device_id=device_id, query_only=False, payload='111111')
        message = self.receive_message()
        if message:
            #FIXME check for error messages from pump
            return bool(int(message["payload"]))
        else:
            logging.warning('Reply not received sucessfully.')
            return None
    
    def stop(self, device_id=None):
        self.send_message(command=self.commands["PumpgStatn"], device_id=device_id, query_only=False, payload='000000')
        message = self.receive_message()
        if message:
            #FIXME check for error messages from pump
            return bool(int(message["payload"]))
        else:
            logging.warning('Reply not received sucessfully.')
            return None

    def toggle(self, device_id=None):
        self.send_message(command=self.commands["PumpgStatn"], device_id=device_id, query_only=True, payload='=?')
        message = self.receive_message()
        if message["payload"] in ['000000','111111']:
            new_payload = self._pad_payload(str(int(message["payload"])^111111),6)#flip 111111 to 000000 and the other way round.
            self.send_message(command=self.commands["PumpgStatn"], device_id=device_id, query_only=False, payload=new_payload)
            message = self.receive_message()
            if message:
                #FIXME check for error messages from pump
                return bool(int(message["payload"]))
            else:
                logging.warning('Reply not received sucessfully.')
                return None
        else:
            logging.warning(f'Invalid pump status received: {message["payload"]}.')
            return None

    def get_running(self, device_id=None):
        self.send_message(command=self.commands["PumpgStatn"], device_id=device_id)
        message = self.receive_message()
        if message:
            #FIXME check for error messages from pump
            return bool(int(message["payload"]))
        else:
            logging.warning('On/off status not received sucessfully.')
            return None
    
    def get_status(self, device_id=None):
        running = self.get_running(device_id=device_id)
        speed = self.get_speed(device_id=device_id)
        pressure = self.get_pressure(device_id=device_id)
        status = {'Running':running, 'Speed':speed, 'Pressure':pressure}
        return status

    def run_timed(self, seconds):
        try:
            self.timer = BoolTimer(seconds)
            self.timer.start()
            self.start()
            while self.timer.state:
                sleep(0.3)
                status = self.get_status()
                print(f'Frequency: {status["Speed"]} Hz')
                if not self.timer.state:
                    break
                sleep(0.05)
        finally:
            self.stop()
    
    def close(self):
        self.inst.close()
# %%

from threading import Thread, Event

class BoolTimer(Thread):
    """A boolean value that toggles after a specified number of seconds:

    bt = BoolTimer(30.0, False)
    bt.start()
    bt.cancel() # prevent the booltimer from toggling if it is still waiting
    """

    def __init__(self, interval, initial_state=True):
        Thread.__init__(self)
        self.interval = interval
        self.state = initial_state
        self.finished = Event()

    def __nonzero__(self):
        return bool(self.state)

    def cancel(self):
        """Stop BoolTimer if it hasn't toggled yet"""
        self.finished.set()

    def run(self):
        self.finished.wait(self.interval)
        if not self.finished.is_set():
            self.state = not self.state
        self.finished.set()