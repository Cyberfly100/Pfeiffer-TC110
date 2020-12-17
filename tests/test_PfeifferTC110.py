import sys
sys.path.append('C:\\Users\\vLab\\Documents\\Python Scripts\\Pfeiffer TC110\\src')

from pfeifferTC110 import TC110
import pytest



class TestTC110:
    def test_calculate_checksum(self):
        assert TC110._calculate_checksum('1230030902=?') == '112'
        assert TC110._calculate_checksum('1231030906000633') == '037'
        assert TC110._calculate_checksum('0421001006111111') == '020'
        
    def test_pad_payload(self):
        assert TC110._pad_payload('1230030902=?',3) == '1230030902=?'
        assert TC110._pad_payload(12,6) == '000012'
        assert TC110._pad_payload('12',3) == '012'

    def test_format_id(self):
        assert TC110._format_id('1') == '001'
        assert TC110._format_id(12) == '012'
        assert TC110._format_id('123') == '123'
        with pytest.raises(TypeError):
            TC110._format_id(False)
        with pytest.raises(ValueError):
            TC110._format_id('123589')
        
    def test_received_ok(self):
        assert TC110._received_ok('1230030902=?112') == True
        assert TC110._received_ok('1230030902=?113') == False
        assert TC110._received_ok('1231030906000633037') == True
        assert TC110._received_ok('0421001006111111020') == True

        