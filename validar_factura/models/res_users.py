# -*- encoding: utf-8 -*-
############################################################################
#    Module for OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Zenpar - http://www.zeval.com.mx/
#    All Rights Reserved.
############################################################################
#    Coded by: miguel.miguel@bias.com.mx
#    Manager: Eduardo Bayardo eduardo.bayardo@bias.com.mx
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################



from osv import osv, fields

class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'allowed_partners': fields.many2many('res.partner', 'allowed_partners_rel', 'user_id', 'partner_id', 'Consolidated Children'),
    }

res_users()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: