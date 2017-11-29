<html>
<head>
    <style type="text/css">
        ${css}
        .company_address {
            font-size:10px;
        }
        .bg_theme_color {
            background-color: #8F8F8F !important;
            color: #FFFFFF !important;
        }
    </style>
</head>
<body>
    %for inv in objects :
    <% setLang(inv.partner_id.lang) %>

    <table width="100%" class="company_address">
        <tr>
            <td width="33%" vertical-align="top">
                ${helper.embed_logo_by_name('camptocamp_logo')|n}
            </td>
            <td width="34%" class="company_address" vertical-align="top">
                <div class="bg_theme_color"> ${inv.company_id.partner_id.name |entity} </div>
                <div> ${inv.company_id.street or ''|entity} </div>
                <div> ${inv.company_id.street2 or ''|entity} </div>
            </td>
            <td width="33%" class="company_address" vertical-align="top">
                <div class="bg_theme_color"> Factura </div>
                <table width="100%" class="company_address">
                    <tr>
                        <td><b>Serie</b></td>
                        <td><b>Folio</b></td>
                    </tr>
                    <tr>
                        <td> ${ inv.journal_id.serie or '' |entity } </td>
                        <td> ${ inv.number or '' |entity } </td>
                    </tr>
                    <tr>
                        <td colspan="2" class="bg_theme_color" >Fecha y Hora de Emisión</td>
                    </tr>
                    <tr>
                        <td colspan="2"> ${ inv.date_invoice_cfdi or '' |entity } </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>    

    <div>
        ${helper.embed_image('png', inv.bar_code, 300, 300)|n}
    </div>


    <table class="dest_address">
        <tr><td ><b>${inv.partner_id.title or ''|entity}  ${inv.partner_id.name |entity}</b></td></tr>
        <tr><td>${inv.address_invoice_id.street or ''|entity}</td></tr>
        <tr><td>${inv.address_invoice_id.street2 or ''|entity}</td></tr>
        <tr><td>${inv.address_invoice_id.zip or ''|entity} ${inv.address_invoice_id.city or ''|entity}</td></tr>
        %if inv.address_invoice_id.country_id :
        <tr><td>${inv.address_invoice_id.country_id.name or ''|entity} </td></tr>
        %endif
        %if inv.address_invoice_id.phone :
        <tr><td>${_("Tel")}: ${inv.address_invoice_id.phone|entity}</td></tr>
        %endif
        %if inv.address_invoice_id.fax :
        <tr><td>${_("Fax")}: ${inv.address_invoice_id.fax|entity}</td></tr>
        %endif
        %if inv.address_invoice_id.email :
        <tr><td>${_("E-mail")}: ${inv.address_invoice_id.email|entity}</td></tr>
        %endif
        %if inv.partner_id.vat :
        <tr><td>${_("VAT")}: ${inv.partner_id.vat|entity}</td></tr>
        %endif
    </table>
    <br />
    %if inv.type == 'out_invoice' :
    <span class="title">${_("Invoice")} ${inv.number or ''|entity}</span>
    %elif inv.type == 'in_invoice' :
    <span class="title">${_("Supplier Invoice")} ${inv.number or ''|entity}</span>   
    %elif inv.type == 'out_refund' :
    <span class="title">${_("Refund")} ${inv.number or ''|entity}</span> 
    %elif inv.type == 'in_refund' :
    <span class="title">${_("Supplier Refund")} ${inv.number or ''|entity}</span> 
    %endif
    <br/>
    <br/>
    <table class="basic_table" width="90%">
        <tr><td>${_("Document")}</td><td>${_("Invoice Date")}</td><td>${_("Partner Ref.")}</td></tr>
        <tr><td>${inv.name}</td><td>${formatLang(inv.date_invoice, date=True)|entity}</td><td>&nbsp;</td></tr>
    </table>
    <h1><br /></h1>
    <table class="list_table"  width="90%">
        <thead><tr><th>${_("Description")}</th><th class>${_("Taxes")}</th><th class>${_("QTY")}</th><th>${_("Unit Price")}</th><th >${_("Disc.(%)")}</th><th>${_("Price")}</th></tr></thead>
        %for line in inv.invoice_line :
        <tbody>
        <tr><td>${line.name|entity}</td><td>${ ', '.join([ tax.name or '' for tax in line.invoice_line_tax_id ])|entity}</td><td>${line.quantity}</td><td style="text-align:right;">${formatLang(line.price_unit)}</td><td  style="text-align:center;">${line.discount or 0.00}</td><td style="text-align:right;">${formatLang(line.price_subtotal)}</td></tr>
        %if line.note :
        <tr><td colspan="6" style="border-style:none"><pre style="font-family:Helvetica;padding-left:20px">${line.note |entity}</pre></td></tr>
        %endif
        %endfor
        <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>Net Total:</b></td><td style="border-top:2px solid;text-align:right">${formatLang(inv.amount_untaxed)}</td></tr>
        <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>Taxes:</b></td><td style="text-align:right">${formatLang(inv.amount_tax)}</td></tr>
        <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>Total:</b></td><td style="border-top:2px solid;text-align:right">${formatLang(inv.amount_total)}</td></tr>
        </tbody>
    </table>

    <table class="list_table" width="40%">
        <tr><th>Tax</th><th>${_("Base")}</th><th>${_("Amount")}</th></tr>
       %if inv.tax_line :
        %for t in inv.tax_line :
        <tr>
            <td>${ t.name|entity } </td>
            <td>${ t.base|entity}</td>
            <td>${ formatLang(t.amount) }</td>
        </tr>
        %endfor
        %endif
        <tr>
            <td style="border-style:none"/>
            <td style="border-top:2px solid"><b>${_("Total")}</b></td>
            <td style="border-top:2px solid">${ formatLang(inv.amount_tax) }</td>
        </tr>
    </table>        
    <p style="page-break-after:always"></p>
    %endfor
</body>
</html>