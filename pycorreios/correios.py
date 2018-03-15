# -*- coding: utf-8 -*-
"""
correios.py
----------

Package to use Correios data
"""

__version__ = '1.1.0'
__author__ = {
    'Teeh Amaral': 'teehamaral1992@gmail.com',
    'Thiago Avelino': 'thiagoavelinoster@gmail.com',
    'Dilan Nery': 'dnerylopes@gmail.com',
}

import urllib
import requests
import re
from xml.dom import minidom

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise Exception('BeautifulSoup module is needed', ImportError)


class Correios(object):
    PAC = 41106
    SEDEX = 40010
    SEDEX_10 = 40215
    SEDEX_HOJE = 40290
    E_SEDEX = 81019
    OTE = 44105
    NORMAL = 41017
    SEDEX_A_COBRAR = 40045

    def __init__(self):
        self.status = 'OK'

    def _getData(self, tags_name, dom):
        data = {}

        for tag_name in tags_name:
            try:
                data[tag_name] = dom.getElementsByTagName(tag_name)[0]
                data[tag_name] = data[tag_name].childNodes[0].data
            except:
                data[tag_name] = ''

        return data

    # Vários campos viraram obrigatórios para cálculo de frete:
    # http://www.correios.com.br/webServices/PDF/SCPP_manual_implementacao_calculo_remoto_de_precos_e_prazos.pdf (páginas 2 e 3)
    def freight(self, code, GOCEP, HERECEP, weight, format, lenght, height, width, diameter, own_hand='N',
                declared_value='0', receipt_alert='N', company='', password='', toback='xml'):

        base_url = "http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx"

        fields = [
            ('nCdEmpresa', company),
            ('sDsSenha', password),
            ('nCdServico', code),
            ('sCepOrigem', HERECEP),
            ('sCepDestino', GOCEP),
            ('nVlPeso', weight),
            ('nCdFormato', format),
            ('nVlComprimento', lenght),
            ('nVlAltura', height),
            ('nVlLargura', width),
            ('nVlDiametro', diameter),
            ('sCdMaoPropria', own_hand),
            ('nVlValorDeclarado', declared_value),
            ('sCdAvisoRecebimento', receipt_alert),
            ('StrRetorno', toback),
        ]

        url = base_url + "?" + urllib.parse.urlencode(fields)
        response = requests.get(url)
        dom = minidom.parseString(response.text)

        tags_name = ('MsgErro',
                     'Erro',
                     'Codigo',
                     'Valor',
                     'PrazoEntrega',
                     'ValorMaoPropria',
                     'ValorValorDeclarado',
                     'EntregaDomiciliar',
                     'EntregaSabado',)

        return self._getData(tags_name, dom)

    def zipcode(self, number):
        url = 'http://cep.republicavirtual.com.br/web_cep.php?formato=' \
              'xml&cep=%s' % str(number)

        response = requests.get(url)
        dom = minidom.parseString(response.text)

        tags_name = ('uf',
                     'cidade',
                     'bairro',
                     'tipo_logradouro',
                     'logradouro',)

        result = dom.getElementsByTagName('resultado')[0]
        result = int(result.childNodes[0].data)
        if result != 0:
            return self._getData(tags_name, dom)
        else:
            return {}

    def order(self, number):
        # Usado como referencia o codigo do Guilherme Chapiewski
        # https://github.com/guilhermechapiewski/correios-api-py

        url = 'http://websro.correios.com.br/sro_bin/txect01$.QueryList?' \
              'P_ITEMCODE=&P_LINGUA=001&P_TESTE=&P_TIPO=001&P_COD_UNI=%s' % \
              str(number)

        response = requests.get(url, timeout=10)
        html = response.text

        table = re.search(r'<table.*</TABLE>', html, re.S).group(0)

        parsed = BeautifulSoup(table)
        data = []

        for count, tr in enumerate(parsed.table):
            if count > 4 and str(tr).strip() != '':
                if re.match(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}',
                            tr.contents[0].string):

                    data.append({
                        'date': unicode(tr.contents[0].string),
                        'location': unicode(tr.contents[1].string),
                        'status': unicode(tr.contents[2].font.string)
                    })

                else:
                    data[len(data) - 1]['detalhes'] = unicode(tr.contents[0].string)

        return data
