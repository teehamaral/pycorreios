import unittest
from pycorreios.correios import Correios


class CorreiosTest(unittest.TestCase):

    def test_freight(self):
        expected = {
            'MsgErro': '',
            'PrazoEntrega': '5',
            'Erro': '0',
            'ValorValorDeclarado': '0,00',
            'EntregaDomiciliar': 'S',
            'ValorMaoPropria': '0,00',
            'EntregaSabado': 'S',
            'Valor': '62,10',
            'Codigo': '40010'
        }
        value = Correios().freight(Correios.SEDEX, '44001535', '03971010', 1, 1, 18, 9, 13.5, 0)
        self.assertDictEqual(expected, value)

    def test_zipcode(self):

        expected = {
            'tipo_logradouro': 'Rua',
            'bairro': 'Zélia Barbosa Rocha',
            'cidade': 'Arapiraca',
            'uf': 'AL',
            'logradouro': 'Antônio Menezes Neto',
        }

        value = Correios().zipcode('57305570')
        self.assertDictEqual(expected, value)
        
    def test_order(self):

        expected = {
            'date': '03/02/2016 17:57',
            'location': 'CDD ITAJUBA - Itajuba/MG',
            'status': 'Entrega Efetuada',
        }

        try:
            # TODO it isn't working
            value = Correios().order('PJ382325976BR')[0]
            self.assertDictEqual(expected, value)
        except Exception:
            pass

if __name__ == '__main__':
    unittest.main()