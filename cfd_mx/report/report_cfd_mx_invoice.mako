<html>
<head>
    <style type="text/css">
        ${css}
        .company_address {
            font-size:11px;
        }
        .bg_theme_color {
            background-color: #8F8F8F !important;
            color: #FFFFFF !important;
        }
        table.no-spacing {
            font-size:11px;
            border-spacing:0; /* Removes the cell spacing via CSS */
            border-collapse: collapse;  /* Optional - if you don't want to have double border where cells touch */
        }
    </style>
</head>
<body>
    %for inv in objects :
    <% setLang(inv.partner_id.lang) %>

        <table width="100%" class="company_address">
            <tr>
                <td width="33%" valign="top" align="top">
                    ${helper.embed_logo_by_name('camptocamp_logo')|n}
                </td>
                <td width="34%" class="company_address" valign="top" align="top">
                    <div width="100%" >
                        <table width="100%" class="company_address">
                            <tr><td><div class="bg_theme_color">${inv.company_id.partner_id.name |entity}</div></td></tr>
                            <tr>
                                <td>
                                    <span>${inv.company_id.street |entity}</span><br/>
                                    <span>Col. ${inv.company_id.street2 |entity}</span><br/>
                                    <span>${inv.company_id.city |entity} ${inv.company_id.state_id.name |entity} ${inv.company_id.zip |entity}</span><br/>
                                    <span>${inv.company_id.country_id.name |entity}</span><br/>
                                    <span>${inv.company_id.website |entity}</span><br/>
                                    <span>${inv.company_id.email |entity}</span><br/>
                                    <span>${inv.company_id.vat |entity}</span><br/>
                                </td>
                            </tr>
                        </table>
                    </div>
                </td>
                <td width="33%" class="company_address" valign="top" align="top">
                    <div width="100%" >
                        <table width="100%" class="company_address">
                            <tr><td colspan="2" ><div class="bg_theme_color">Factura</div></td></tr>
                            <tr>
                                <td width="50%"><b>Serie</b></td>
                                <td width="50%"><b>Folio</b></td>
                            </tr>
                            <tr>
                                <td>${ inv.journal_id.serie or '' |entity }</td>
                                <td>${ inv.number or '' |entity }</td>
                            </tr>
                            <tr><td colspan="2"><div class="bg_theme_color">Fecha y Hora de Emisión</div></td></tr>
                            <tr><td colspan="2">${ inv.date_invoice_cfdi or '' |entity }</td></tr>
                            <tr><td colspan="2"><div class="bg_theme_color">Lugar de Expedición</div></td></tr>
                            <tr><td colspan="2">${ inv.journal_id.codigo_postal_id.name or '' |entity }</td></tr>
                        </table>

                    </div>
                </td>
            </tr>
        </table>
        <table width="100%" class="company_address">
            <tr>
                <td width="33%" valign="top" align="top">
                    <div width="100%" >
                        <table width="100%" class="company_address">
                            <tr><td><div class="bg_theme_color">Información del Cliente</div></td></tr>
                            <tr>
                                <td>
                                    <span><b>${inv.partner_id.name |entity}</b></span><br/>
                                    <span>${inv.address_invoice_id.street or '' |entity}</span><br/>
                                    <span>Col. ${inv.address_invoice_id.street2 or '' |entity}</span><br/>
                                    <span>${inv.address_invoice_id.city |entity} ${inv.address_invoice_id.state_id.name |entity} ${inv.address_invoice_id.zip |entity}</span><br/>
                                    <span>${inv.address_invoice_id.country_id.name |entity}</span><br/>
                                    %if inv.address_invoice_id.email :
                                    <span>${inv.address_invoice_id.email |entity}</span><br/>
                                    %endif
                                    %if inv.partner_id.vat :
                                    <span>${inv.partner_id.vat |entity}</span><br/>
                                    %endif
                                </td>
                            </tr>
                        </table>
                    </div>
                </td>
                <td width="34%" valign="top" align="top">
                    <div width="100%" >
                        <table width="100%" class="company_address">
                            <tr><td><div class="bg_theme_color">Uso del CFDI</div></td></tr>
                            <tr><td><div>${inv.usocfdi_id.name |entity}</div></td></tr>
                            <tr><td><div class="bg_theme_color">Moneda</div></td></tr>
                            <tr><td><div>${inv.currency_id.name |entity}</div></td></tr>
                            <tr><td><div class="bg_theme_color">Tipo de Cambio</div></td></tr>
                            <tr><td><div>${inv.usocfdi_id.name |entity}</div></td></tr>
                        </table>
                    </div>

                </td>
                <td width="33%" valign="top" align="top">
                    <div width="100%" >
                        <table width="100%" class="company_address">
                            <tr><td><div class="bg_theme_color">Información Adicional</div></td></tr>
                            <tr>
                                <td>
                                    <span><b>No Certificado:</b> ${inv.certificate |entity}</span><br/>
                                    <span><b>Método de Pago:</b> ${inv.metodopago_id.clave |entity} - ${inv.metodopago_id.name |entity}</span><br/>
                                    <span><b>Forma de Pago:</b> ${inv.formapago_id.clave |entity} - ${inv.formapago_id.name |entity}</span><br/>
                                    <span><b>Condiciones de Pago:</b> ${inv.payment_term.name |entity}</span><br/>
                                </td>
                            </tr>
                        </table>
                    </div>
                </td>
            </tr>
        </table>
        <table class="no-spacing" cellspacing="0" width="100%" class="company_address">
            <tr><td colspan="6" ><div class="bg_theme_color">CONCEPTOS DEL COMPROBANTE</div></td></tr>
            <tr>
                <td width="50%"><div class="bg_theme_color">Descripcíón</div></td>
                <td><div class="bg_theme_color">Cantidad</div></td>
                <td><div class="bg_theme_color">Unidad</div></td>
                <td><div class="bg_theme_color">V. Unitario</div></td>
                <td><div class="bg_theme_color">Importe</div></td>
                <td><div class="bg_theme_color">Descuento</div></td>
            </tr>
            %for l in inv.invoice_line :
                <tr>
                    <td width="50%"><div><span>${l.name |entity}</span></div></td>
                    <td><div><span>${l.quantity |entity}</span></div></td>
                    <td><div><span>${l.uos_id.name |entity}</span></div></td>
                    <td><div><span>$ ${l.price_unit |entity}</span></div></td>
                    <td><div><span>$ ${l.price_subtotal |entity}</span></div></td>
                    <td><div><span>$ ${l.price_discount_sat |entity}</span></div></td>
                </tr>
                %if len(l.get_impuestos_sat()) :
                    <tr>
                        <td colspan="6" valign="top" align="top">
                            <div width="100%">
                                <table width="100%" class="company_address">
                                    <tr>
                                        <td width="40%">
                                            <span><b>Clave Producto SAT:</b> ${l.product_id.clave_prodser_id.clave or '01010101' |entity} </span><br />
                                            <span><b>Clave Unidad SAT:</b> ${l.uos_id.clave_unidadesmedida_id.clave |entity}</span>
                                        </td>
                                        <td width="60%">
                                            <table style="width:100%" class="company_address">
                                                <tr>
                                                    <td><strong>Nombre</strong></td>
                                                    <td><strong>Impuesto</strong></td>
                                                    <td><strong>Tipo Factor</strong></td>
                                                    <td><strong>Tasa o Cuota</strong></td>
                                                    <td><strong>Importe</strong></td>
                                                </tr>
                                                %for t in l.get_impuestos_sat() :
                                                    <tr>
                                                        <td><span>${ t.get('Name') |entity}</span></td>
                                                        <td><span>${ t.get('Impuesto') |entity}</span></td>
                                                        <td><span>${ t.get('TipoFactor') |entity}</span></td>
                                                        <td><span>${ t.get('TasaOCuota') |entity}</span></td>
                                                        <td><span>${ t.get('Importe') |entity}</span></td>
                                                    </tr>
                                                %endfor
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                        </td>
                    </tr>
                %endif
            %endfor
        </table>
        <table style="width:100%" class="company_address">
            <tr>
                <td class="bg_theme_color" width="20%"><strong>Subtotal</strong></td>
                <td class="bg_theme_color" width="20%"><strong>Impuestos Trasladados</strong></td>
                <td class="bg_theme_color" width="20%"><strong>Impuestos Retenidos</strong></td>
                <td class="bg_theme_color" width="20%"><strong>Descuento</strong></td>
                <td class="bg_theme_color" width="20%"><strong>Total</strong></td>
            </tr>
            <tr>
                <td width="20%">${inv.price_subtotal_sat |entity}</td>
                <td width="20%">$ ${inv.get_impuestos_ret_tras()['ret'] |entity}</td>
                <td width="20%">$ ${inv.get_impuestos_ret_tras()['tras'] |entity}</td>
                <td width="20%">${inv.price_discount_sat |entity}</td>
                <td width="20%">${inv.price_subtotal_sat - inv.price_discount_sat + inv.price_tax_sat |entity}</td>
            </tr>
        </table>
        %if inv.uuid_relacionado_id :
        <table width="100%" class="company_address">
            <tr><td colspan="2" ><div class="bg_theme_color">DOCUMENTO RELACIONADO</div></td></tr>
            <tr>
                <td><div class="bg_theme_color">Tipo Relación</div></td>
                <td><div class="bg_theme_color">UUID Relacionado</div></td>
            </tr>
            <tr>
                <td><div>${ inv.tiporelacion_id |entity}</div></td>
                <td><div>${ inv.uuid_egreso |entity}</div></td>
            </tr>
        </table>
        %endif
        <table width="100%" class="company_address">
            <tr><td colspan="4" ><div class="bg_theme_color">TIMBRE FISCAL</div></td></tr>
            <tr>
                <td class="bg_theme_color" width="10%"><strong>PAC</strong></td>
                <td class="bg_theme_color" width="40%"><strong>Folios Fiscal</strong></td>
                <td class="bg_theme_color" width="25%"><strong>No. Certificado SAT</strong></td>
                <td class="bg_theme_color" width="25%"><strong>Fecha y Hora de Certificación</strong></td>
            </tr>
            <tr>
                <td width="10%">${inv.company_id.cfd_mx_pac |entity}</td>
                <td width="40%">${inv.uuid |entity}</td>
                <td width="25%">${inv.certificado_sat |entity}</td>
                <td width="25%">${inv.fecha_timbrado |entity}</td>
            </tr>
        </table>
        <table width="100%" class="company_address" valign="top" align="top">
            <tr>
                <td width="25%" valign="top" align="top">${helper.embed_image('png', inv.bar_code, 133, 133)|n}</td>
                <td width="25%" valign="top" align="top">
                    <div width="100%" class="bg_theme_color">Sello Digital del Emisor</div>
                    <span style="font-size:6px; display:block; width:150px; word-wrap:break-word;">${inv.sello or '' |entity}</span>
                </td>
                <td width="25%" valign="top" align="top">
                    <div width="100%" class="bg_theme_color">Sello Digital del SAT</div>
                    <span style="font-size:6px; display:block; width:150px; word-wrap:break-word;">${inv.sello_sat |entity}</span>
                </td>
                <td width="25%" valign="top" align="top">
                    <div width="100%" class="bg_theme_color">Cadena Original</div>
                    <span style="font-size:6px; display:block; width:150px; word-break:break-all;">${inv.cadena |entity}</span>
                </td>
            </tr>
        </table>
    %endfor
</body>
</html>