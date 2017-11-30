#! /usr/bin/python
# -*- coding: utf-8 -*-
#

import lxml
from lxml import etree
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class validate_xml_schema():

    def __init__(self, xml_xds, xml_data):
        self.xml_xds = xml_xds
        self.xml_data = xml_data
        self.response_vaidate = ""


    def validate_xml(self):
        f = open(self.xml_xds)
        doc = etree.parse(f)        
        logger.info("** Validating schema ... ")
        self.response_vaidate += self.message_item('** Validating schema ...')
        try:
            schema = etree.XMLSchema(doc)
        except lxml.etree.XMLSchemaParseError:
            return False
        logger.info("** Schema OK ... ")
        self.response_vaidate += self.message_item('----> Schema OK ')

        f = open(self.xml_data)
        doc = etree.parse(f)

        logger.info("** Validating document ... ")
        self.response_vaidate += self.message_item('\n** Validating Document ...')
        try:
            schema.assertValid(doc)
        except lxml.etree.DocumentInvalid:
            error_mensaje = ''
            for l in schema.error_log.filter_from_errors()[:30]:
                error_mensaje = str(l.message.encode('utf-8'))
                logger.info("----> %s ... "%error_mensaje)
                logger.info("----> El Documento XML NO es Válido. ... ")
                error_mensaje = error_mensaje.replace("'{www.sat.gob.mx/esquemas/ContabilidadE/1_1/PolizasPeriodo}Poliza',", "")
                error_mensaje = error_mensaje.replace("'{www.sat.gob.mx/esquemas/ContabilidadE/1_1/BalanzaComprobacion}Balanza',", "")
                error_mensaje = error_mensaje.replace("'{www.sat.gob.mx/esquemas/ContabilidadE/1_1/CatalogoCuentas}Ctas',", "")
                error_mensaje = error_mensaje.replace("'{www.sat.gob.mx/esquemas/ContabilidadE/1_1/CatalogoCuentas}Catalogo',", "")
                error_mensaje = error_mensaje.replace("'{www.sat.gob.mx/esquemas/ContabilidadE/1_1/CatalogoCuentas}Catalogo',", "")
                self.response_vaidate += self.message_item('----> %s'%error_mensaje)
            if error_mensaje:
                self.response_vaidate += self.message_item('----> El Documento XML NO es Valido ...')
            return False
        logger.info("----> XML document OK ... ")
        self.response_vaidate += self.message_item('----> XML document OK')
        return 

    def message_item(self, item):
        item_msg = """%s \n"""%(item)
        return item_msg

    def return_validate(self):
        xml_response = """%s"""%(self.response_vaidate)
        return xml_response