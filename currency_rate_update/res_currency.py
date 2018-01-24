# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import date
import time

from osv import osv
from osv import fields
import time

import pooler

_logger = logging.getLogger(__name__)


try:
    import feedparser
except ImportError:
    pass

def rate_retrieve():
    banxico_rss_url = "http://www.banxico.org.mx/rsscb/rss?BMXC_canal=pagos&BMXC_idioma=es" 
    feed = feedparser.parse(banxico_rss_url)
    rate = 0.0
    for f in feed.entries:
        rate = f and f.cb_exchangerate or 0.0
    return rate


class res_currency(osv.osv):
    _inherit = 'res.currency'

    def refresh_currency(self, cr, uid, ids, context=None):
        """Refresh the currencies rates !!for all companies now"""
        _logger.info('  ** Starting to refresh currencies with service %s', ids)
        if context is None:
            context = {}

        rate = rate_retrieve()
        if rate == 0.0:
            return False

        rate_obj = self.pool.get('res.currency.rate')
        currency_obj = self.pool.get('res.currency')

        rate = eval(rate)
        for res in currency_obj.browse(cr, uid, ids, context=context):
            vals = {
                'name': context.get('date_cron'),
                'currency_id': res.id,
                'rate': rate
            }
            try:
                WHERE = [('name', '=', context.get('date_cron')), ('currency_id', '=', res.id)]
                rate_brw = rate_obj.search(cr, uid, WHERE, context=context)
                if not rate_brw:
                    rate_obj.create(cr, uid, vals, context=context)
                    _logger.info('  ** Create currency rate %s -- date %s',res.name, context.get('date_cron'))
                else:
                    rate_obj.write(cr, uid, vals, context=context)
                    _logger.info('  ** Update currency rate %s -- date %s',res.name, context.get('date_cron'))
            except:
                pass
        return rate

    def run_currency_update_d(self, cr, uid, ids, context=None):
        '''
        use_new_cursor: False or the dbname
        '''
        if not context:
            context = {}
        currency_obj = self.pool.get('res.currency')
        today = date.today()
        services = {
            'cron': True,
            'date_cron': '%s'%(today)
        }
        currency_ids = currency_obj.search(cr, uid, [('name', 'in', ('MN', 'MXN'))], context=services)
        print 'currency_ids', currency_ids
        for res in currency_obj.browse(cr, uid, currency_ids, context=context):
            currency_obj.refresh_currency(cr, uid, [res.id], context=services)
            _logger.info(' === End of the currency rate update cron')
        return True



    def run_currency_update(self, cr, uid, ids=None, context=None):
        '''
        use_new_cursor: False or the dbname
        '''
        if not context:
            context={}
        r = self.run_currency_update_d(cr, uid, [], context=context)
        return True



res_currency()