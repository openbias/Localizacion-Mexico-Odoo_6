# -*- encoding: utf-8 -*-
{
    'name' : 'Factura Electronica Mexico 3.3',
    'version' : '1.0',
    'author' : 'BIAS',
    'category' : 'Accounting & Finance',
    'description': '',
    'depends' : [
        'bias_electronic_invoice_v6'
    ],
    'init_xml': [
        # 'secuence_data.xml'
        "data/cfd_mx.aduana.xml",
        "data/account.tax.group.xml",
        "data/cfd_mx.formapago.xml",
        "data/cfd_mx.metodopago.xml",
        "data/cfd_mx.regimen.xml",
        "data/cfd_mx.tiporelacion.xml",
        "data/cfd_mx.usocfdi.xml",
        "data/res.bank.xml",
        "data/res.country.xml",
    ],
    'update_xml' : [
        'security/ir.model.access.csv',
        'views/cfd_mx_models_view.xml',
        'views/account_view.xml',
        'views/res_partner_view.xml',
        'views/product_view.xml',
        'views/res_company_view.xml',
        'views/account_invoice_view.xml',

        'report/cfd_mx_report_document.xml'
        # 'account_view.xml',
        # 'res_company_view.xml',
        # 'account_invoice_workflow.xml',
        # 'partner_view.xml',
        # 'invoice_report.xml',
        # 'invoice_wizard.xml'
    ],
    'active': False,
    'installable': True,
    
    
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:{

