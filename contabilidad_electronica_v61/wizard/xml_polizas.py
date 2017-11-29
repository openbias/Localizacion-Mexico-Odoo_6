# -*- encoding: utf-8 -*-
import xml.etree.ElementTree as ET
from osv import osv

def xml_polizas(data):
    namespace_uri = "www.sat.gob.mx/esquemas/ContabilidadE/1_1/PolizasPeriodo"
    schemaLocation = "www.sat.gob.mx/esquemas/ContabilidadE/1_1/PolizasPeriodo http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/PolizasPeriodo/PolizasPeriodo_1_1.xsd"
    version = "1.1"
    if data.get('version') == '1_3':
            namespace_uri = "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/PolizasPeriodo"
            schemaLocation = "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/PolizasPeriodo http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/PolizasPeriodo/PolizasPeriodo_1_3.xsd"
            version = "1.3"


    namespace_prefix = "PLZ"
    ET.register_namespace(namespace_prefix, namespace_uri)
    ns = namespace_prefix + ":"
    root = ET.Element(ns+"Polizas", {
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
    for poliza in data["polizas"]:
        nodo_poliza = ET.SubElement(root, ns+"Poliza", {
            "NumUnIdenPol": "%s"%poliza["num"],
            "Fecha": "%s"%poliza["fecha"],
            "Concepto": "%s"%poliza["concepto"]
        })
        for transaccion in poliza["transacciones"]:
            nodo_transaccion = ET.SubElement(nodo_poliza, ns+"Transaccion", {
                "NumCta": "%s"%transaccion["num_cta"],
                "DesCta": "%s"%transaccion["des_cta"],
                "Concepto": "%s"%transaccion["concepto"],
                "Debe": "%.2f"%transaccion["debe"],
                "Haber": "%.2f"%transaccion["haber"],
            })
            for comprobante in transaccion["comprobantes"]:
                el = ET.SubElement(nodo_transaccion, ns+"CompNal", {
                    "UUID_CFDI": "%s"%comprobante["uuid"],
                    "MontoTotal": "%.2f"%comprobante["monto"],
                    "RFC": "%s"%comprobante["rfc"]
                })
                if comprobante.get("moneda", False):
                    el.attrib["Moneda"] = "%s"%comprobante["moneda"]
                    el.attrib["TipCamb"] = "%.2f"%comprobante["tip_camb"]
            for comprobante in transaccion["comprobantes_cfd_cbb"]:
                el = ET.SubElement(nodo_transaccion, ns+"CompNalOtr", {
                    "CFD_CBB_NumFol": "%s"%comprobante["folio"],
                    "MontoTotal": "%.2f"%comprobante["monto"],
                    "RFC": "%s"%comprobante["rfc"]
                })
                if comprobante.get("serie", False):
                     el.attrib["CFD_CBB_Serie"] = "%s"%comprobante["serie"]
                if comprobante.get("moneda", False):
                    el.attrib["Moneda"] = "%s"%comprobante["moneda"]
                    el.attrib["TipCamb"] = "%.2f"%comprobante["tip_camb"]
            for comprobante in transaccion["comprobantes_ext"]:
                el = ET.SubElement(nodo_transaccion, ns+"CompExt", {
                    "NumFactExt": "%s"%comprobante["num"],
                    "MontoTotal": "%.2f"%comprobante["monto"],
                })
                if comprobante.get("tax_id", False):
                    el.attrib["TaxID"] = "%s"%comprobante["tax_id"]
                if comprobante.get("moneda", False):
                    el.attrib["Moneda"] = "%s"%comprobante["moneda"]
                    el.attrib["TipCamb"] = "%.2f"%comprobante["tip_camb"]
            for cheque in transaccion["cheques"]:
                el = ET.SubElement(nodo_transaccion, ns+"Cheque", {
                    "Num": "%s"%cheque["num"],
                    "BanEmisNal": "%s"%cheque["banco"],
                    "CtaOri": "%s"%cheque["cta_ori"],
                    "Fecha": "%s"%cheque["fecha"],
                    "Monto": "%.2f"%cheque["monto"],
                    "Benef": "%s"%cheque["benef"],
                    "RFC": "%s"%cheque["rfc"],
                })
                if cheque.get("banco_ext", False):
                    el.attrib["BanEmisExt"] = cheque["banco_ext"]
                if cheque.get("moneda", False):
                    el.attrib["Moneda"] = "%s"%cheque["moneda"]
                    el.attrib["TipCamb"] = "%.2f"%cheque["tip_camb"]
            for transferencia in transaccion["transferencias"]:
                el = ET.SubElement(nodo_transaccion, ns+"Transferencia", {
                    "CtaOri": "%s"%transferencia["cta_ori"],
                    "BancoOriNal": "%s"%transferencia["banco_ori"],
                    "Monto": "%.2f"%transferencia["monto"],
                    "CtaDest": "%s"%transferencia["cta_dest"],
                    "BancoDestNal": "%s"%transferencia["banco_dest"],
                    "Fecha": "%s"%transferencia["fecha"],
                    "Benef": "%s"%transferencia["benef"],
                    "RFC": "%s"%transferencia["rfc"]
                })
                if transferencia.get("banco_ori_ext", False):
                    el.attrib["BancoOriExt"] = transferencia["banco_ori_ext"]
                if transferencia.get("banco_dest_ext", False):
                    el.attrib["BancoDestExt"] = transferencia["banco_dest_ext"]  
                if transferencia.get("moneda", False):
                    el.attrib["Moneda"] = "%s"%transferencia["moneda"]
                    el.attrib["TipCamb"] = "%.2f"%transferencia["tip_camb"]
            for otro in transaccion["otros_metodos"]:
                el = ET.SubElement(nodo_transaccion, ns+"OtrMetodoPago", {
                    "MetPagoPol": "%s"%otro["met_pago"],
                    "Fecha": "%s"%otro["fecha"],
                    "Benef": "%s"%otro["benef"],
                    "RFC": "%s"%otro["rfc"],
                    "Monto": "%.2f"%otro["monto"]
                })
                if otro.get("moneda", False):
                    el.attrib["Moneda"] = "%s"%otro["moneda"]
                    el.attrib["TipCamb"] = "%.2f"%otro["tip_camb"]

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
    atributos_poliza = [
        ('NumUnIdenPol', requerido),
        ('Fecha', requerido),
        ('Concepto', requerido)
    ]
    atributos_transaccion = [
        ('NumCta', requerido),
        ('Concepto', requerido),
        ('Debe', requerido),
        ('Haber', requerido),
    ]
    atributos = {}
    atributos["CompNal"] = [
        ('UUID_CFDI', requerido)
    ]
    atributos["CompNalOtr"] = [
        ('CFD_CBB_Serie', requerido),
        ('CFD_CBB_NumFol', requerido)
    ]
    atributos["CompExt"] = [
        ('NumFactExt', requerido)
    ]
    atributos["Cheque"] = [
        ('Num', requerido),
        ('BanEmisNal', requerido),
        ('BanEmisExt', opcional),
        ('CtaOri', requerido),
        ('Fecha', requerido),
        ('Benef', requerido),
        ('RFC', requerido),
        ('Monto', requerido),
        ('Moneda', opcional),
        ('TipCamb', opcional),
    ]
    atributos["Transferencia"] = [
        ('CtaOri', requerido),
        ('BancoOriNal', requerido),
        ('BancoOriExt', opcional),
        ('CtaDest', requerido),
        ('BancoDestNal', requerido),
        ('BancoDestExt', opcional),
        ('Fecha', requerido),
        ('Benef', requerido),
        ('RFC', requerido),
        ('Monto', requerido),
        ('Moneda', opcional),
        ('TipCamb', opcional),
    ]
    atributos["OtrMetodoPago"] = [
        ('MetPagoPol', requerido),
        ('Fecha', requerido),
        ('Benef', requerido),
        ('RFC', requerido),
        ('Monto', requerido),
        ('Moneda', opcional),
        ('TipCamb', opcional),
    ]

    cadena = ["|"]

    def procesar(nodo, atributos, cadena):
        for a,f in atributos:
            valor = nodo.attrib.get(a, False)
            if f == requerido and valor == False:
                raise osv.except_osv("Error", u"Atributo requerido '%s' ausente en el nodo: %s"%(a,nodo.attrib))
            cadena[0] += f(valor)

    procesar(root, atributos_root, cadena)
    for poliza in root:
        procesar(poliza, atributos_poliza, cadena)
        for transaccion in poliza:
            procesar(transaccion, atributos_transaccion, cadena)
            for nodo in transaccion:
                tag = nodo.tag[nodo.tag.index('}')+1:]
                procesar(nodo, atributos[tag], cadena)

    return cadena[0] + "||"


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: