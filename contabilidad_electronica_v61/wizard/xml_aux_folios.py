# -*- encoding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
import inspect
from osv import osv
from files import TempFileTransaction

def xml_aux_folios(data):
    namespace_uri = "www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarFolios"
    schemaLocation = "www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarFolios http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarFolios/AuxiliarFolios_1_2.xsd"
    version = "1.2"
    if data.get('version') == '1_3':
            namespace_uri = "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/AuxiliarFolios"
            schemaLocation = "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/AuxiliarFolios http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/AuxiliarFolios/AuxiliarFolios_1_3.xsd"
            version = "1.3"

    namespace_prefix = "RepAux"
    ET.register_namespace(namespace_prefix, namespace_uri)
    ns = namespace_prefix + ":"
    root = ET.Element(ns+"RepAuxFol", {
        'xsi:schemaLocation': schemaLocation,
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xmlns:' + namespace_prefix: namespace_uri,
        'Version': version,
        'RFC': "%s"%data["rfc"],
        'Mes': "%s"%data["mes"],
        'Anio': "%s"%data["ano"],
        'TipoSolicitud': "%s"%data["tipo_solicitud"],
        'noCertificado': "%s"%data["noCertificado"]
    })
    if data.get('num_orden',False):
        root.attrib["NumOrden"] = "%s"%data['num_orden']
    if data.get('num_tramite', False):
        root.attrib["NumTramite"] = "%s"%data['num_tramite']
    for detalle in data["detalles"]:
        nodo_detalle = ET.SubElement(root, ns+"DetAuxFol", {
            "NumUnIdenPol": "%s"%detalle["num"],
            "Fecha": "%s"%detalle["fecha"],
        })
        for comprobante in detalle["comprobantes"]:
            el = ET.SubElement(nodo_detalle, ns+"ComprNal", {
                "UUID_CFDI": "%s"%comprobante["uuid"],
                "MontoTotal": "%.2f"%comprobante["monto"],
                "RFC": "%s"%comprobante["rfc"]
            })
            if comprobante.get("moneda", False):
                el.attrib["Moneda"] = "%s"%comprobante["moneda"]
                el.attrib["TipCamb"] = "%.2f"%comprobante["tip_camb"]
            if comprobante.get("MetAuxPago", False):
                el.attrib["MetAuxPago"] = "%s"%omprobante["MetAuxPago"]
        for comprobante in detalle["comprobantes_cfd_cbb"]:
                el = ET.SubElement(nodo_detalle, ns+"ComprNalOtr", {
                    "CFD_CBB_NumFol": "%s"%comprobante["folio"],
                    "MontoTotal": "%.2f"%comprobante["monto"],
                    "RFC": "%s"%comprobante["rfc"]
                })
                if comprobante.get("serie", False):
                     el.attrib["CFD_CBB_Serie"] = "%s"%comprobante["serie"]
                if comprobante.get("moneda", False):
                    el.attrib["Moneda"] = "%s"%comprobante["moneda"]
                    el.attrib["TipCamb"] = "%.2f"%comprobante["tip_camb"]
                if comprobante.get("MetAuxPago", False):
                    el.attrib["MetAuxPago"] = "%s"%omprobante["MetAuxPago"]
        for comprobante in detalle["comprobantes_ext"]:
            el = ET.SubElement(nodo_detalle, ns+"ComprExt", {
                "NumFactExt": "%s"%comprobante["num"],
                "MontoTotal": "%.2f"%comprobante["monto"],
            })
            if comprobante.get("tax_id", False):
                el.attrib["TaxID"] = "%s"%comprobante["tax_id"]
            if comprobante.get("moneda", False):
                el.attrib["Moneda"] = "%s"%comprobante["moneda"]
                el.attrib["TipCamb"] = "%.2f"%comprobante["tip_camb"]
            if comprobante.get("MetAuxPago", False):
                el.attrib["MetAuxPago"] = "%s"%omprobante["MetAuxPago"]
    return root


def cadena_original(xml):

    def normalizar_espacios(valor):
        return " ".join(valor.split())

    def requerido(valor):
        return "|" + normalizar_espacios(valor)

    def opcional(valor):
        return "|" + normalizar_espacios(valor) if valor else ""

    root = ET.fromstring(xml)
    atributos_root = [
        ('Version', requerido),
        ('RFC', requerido),
        ('Mes', requerido),
        ('Anio', requerido),
        ('TipoSolicitud', requerido),
        ('NumOrden', opcional),
        ('NumTramite', opcional)
    ]
    atributos_detalle = [
        ('NumUnIdenPol', requerido),
        ('Fecha', requerido),
    ]
    atributos = {}
    atributos["ComprNal"] = [
        ('UUID_CFDI', requerido),
        ('RFC', requerido),
        ('MetPagoAux', opcional),
        ('MontoTotal', requerido),
        ('Moneda', opcional),
        ('TipCamb', opcional)
    ]
    atributos["ComprNalOtr"] = [
        ('CFD_CBB_Serie', requerido),
        ('CFD_CBB_NumFol', requerido),
        ('RFC', requerido),
        ('MetPagoAux', opcional),
        ('MontoTotal', requerido),
        ('Moneda', opcional),
        ('TipCamb', opcional)
    ]
    atributos["ComprExt"] = [
        ('NumFactExt', requerido),
        ('MetPagoAux', opcional),
        ('MontoTotal', requerido),
        ('Moneda', opcional),
        ('TipCamb', opcional)
    ]

    cadena = ["|"]

    def procesar(nodo, atributos, cadena):
        for a,f in atributos:
            valor = nodo.attrib.get(a, False)
            if f == requerido and valor == False:
                raise osv.except_osv("Error", u"Atributo requerido '%s' ausente en el nodo: %s"%(a,nodo.attrib))
            cadena[0] += f(valor)

    procesar(root, atributos_root, cadena)
    for detalle in root:
        procesar(detalle, atributos_detalle, cadena)
        for nodo in detalle:
            tag = nodo.tag[nodo.tag.index('}')+1:]
            procesar(nodo, atributos[tag], cadena)

    return cadena[0] + "||"


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: