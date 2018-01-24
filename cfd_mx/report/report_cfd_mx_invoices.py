# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pooler
from report.interface import report_rml
from tools import to_xml
import tools
from random import shuffle

class ReportCfdInvoices(report_rml):

    def create(self, cr, uid, ids, datas, context):
        datas.update({
            'form': {
                'orientation': 'vertical',
                'paper_size': 'legal'
            }
        })
        _pageSize = ('26.6cm','33.0cm')
        if datas.has_key('form') and datas['form'].get('orientation','') == 'vertical':
            if datas['form'].get('paper_size','') == 'letter':
                _pageSize = ('21.6cm','27.9cm')
            elif datas['form'].get('paper_size','') == 'legal':
                _pageSize = ('21.6cm','35.6cm')
            elif datas['form'].get('paper_size','') == 'a4':
                _pageSize = ('21.1cm','29.7cm')
            elif datas['form'].get('paper_size','') == 'folio':
                _pageSize = ('21.6cm','33.0cm')
        elif datas.has_key('form') and datas['form'].get('orientation','') == 'horizontal':
            if datas['form'].get('paper_size','') == 'letter':
                _pageSize = ('27.9cm','21.6cm')
            elif datas['form'].get('paper_size','') == 'legal':
                _pageSize = ('35.6cm','21.6cm')
            elif datas['form'].get('paper_size','') == 'a4':
                _pageSize = ('29.7cm','21.1cm')
            elif datas['form'].get('paper_size') == 'folio':
                _pageSize = ('33.0cm','21.6cm')

        _frame_width = tools.ustr(_pageSize[0])
        _frame_height = tools.ustr(float(_pageSize[1].replace('cm','')) - float(1.90))+'cm'
        _tbl_widths = tools.ustr(float(_pageSize[0].replace('cm','')) - float(2.10))+'cm'


        pool = pooler.get_pool(cr.dbname)

        rml ="""<?xml version="1.0"?>
                <document filename="Control Assistance Report.pdf">
                <template pageSize="("""+_pageSize[0]+""","""+_pageSize[1]+""")" title='Control Assistance' author="OpenBias" allowSplitting="20" >
                    <pageTemplate id="first">
                        <frame id="first" x1="0.0cm" y1="1.0cm" width='"""+_frame_width+"""' height='"""+_frame_height+"""'/>
                        <pageGraphics>                        
                          <setFont name="Helvetica" size="8"/>
                          <stroke color="#000000"/>
                          <lines>6.5cm 1.5cm 14.0cm 1.5cm</lines>
                          <drawCentredString x="10.5cm" y="1.2cm">Nombre y Firma </drawCentredString>
                          <fill color="gray"/>
                          <setFont name="Helvetica" size="7"/>
                          <drawRightString x='"""+tools.ustr(float(_pageSize[0].replace('cm','')) - float(1.00))+'cm'+"""' y="0.6cm">Page : <pageNumber/> </drawRightString>
                    </pageGraphics>
                </pageTemplate>
                </template>
                  <stylesheet>
                    <blockTableStyle id="tbl_title">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                    </blockTableStyle>
                    <blockTableStyle id="tbl_date">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBEFORE" colorName="#000000" start="1,0" stop="1,-1"/>
                      <lineStyle kind="LINEABOVE" colorName="#000000" start="1,0" stop="1,0"/>
                      <lineStyle kind="LINEBELOW" colorName="#000000" start="1,-1" stop="1,-1"/>
                      <lineStyle kind="LINEBEFORE" colorName="#000000" start="2,0" stop="2,-1"/>
                      <lineStyle kind="LINEAFTER" colorName="#000000" start="2,0" stop="2,-1"/>
                      <lineStyle kind="LINEABOVE" colorName="#000000" start="2,0" stop="2,0"/>
                      <lineStyle kind="LINEBELOW" colorName="#000000" start="2,-1" stop="2,-1"/>
                    </blockTableStyle>
                    <blockTableStyle id="tbl_header_01">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBEFORE" colorName="#000000" start="0,0" stop="0,-1"/>
                      <lineStyle kind="LINEAFTER" colorName="#000000" start="0,0" stop="0,-1"/>
                      <lineStyle kind="LINEABOVE" colorName="#000000" start="0,0" stop="0,0"/>
                      <lineStyle kind="LINEBELOW" colorName="#000000" start="0,-1" stop="0,-1"/>
                      <blockBackground colorName="#000000" start="0,0" stop="0,-1"/>
                    </blockTableStyle>
                    <blockTableStyle id="simple_table_line">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="gray"/>
                    </blockTableStyle>
                    
                    <blockTableStyle id="Table41">
                      <blockAlignment value="CENTER"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="gray" start="0,0" stop="-1,-1"/>
                      <lineStyle kind="LINEBEFORE" colorName="gray" start="0,0" stop="-1,-1"/>
                      <lineStyle kind="LINEAFTER" colorName="gray" start="0,0" stop="-1,-1"/>
                      <blockBackground colorName="gray" start="0,0" stop="-1,-1"/>
                    </blockTableStyle>

                    <blockTableStyle id="simple_table_line_h">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="gray"/>
                      <blockBackground colorName="gray" start="0,0" stop="-1,-1"/>
                    </blockTableStyle>
                    
                    <blockTableStyle id="simple_table_line_1">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="#000000" width="100"/>
                    </blockTableStyle>
                    <blockTableStyle id="tbl_white">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="#8f8f8f" start="0,0" stop="-1,-1"/>
                      <lineStyle kind="LINEBEFORE" colorName="#8f8f8f" start="0,0" stop="-1,-1"/>
                      <lineStyle kind="LINEAFTER" colorName="#8f8f8f" start="0,0" stop="-1,-1"/>
                    </blockTableStyle>
                    <blockTableStyle id="tbl_gainsboro">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="#000000" start="0,0" stop="-1,-1"/>
                      <lineStyle kind="LINEBEFORE" colorName="#000000" start="0,0" stop="-1,-1"/>
                      <lineStyle kind="LINEAFTER" colorName="#000000" start="0,0" stop="-1,-1"/>
                      <blockBackground colorName="gainsboro" start="0,0" stop="-1,-1"/>
                    </blockTableStyle>
                    
                    <blockTableStyle id="ans_tbl_white">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="#e6e6e6" start="0,0" stop="-1,-1"/>
                    </blockTableStyle>
                    <blockTableStyle id="ans_tbl_gainsboro">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="#e6e6e6" start="0,0" stop="-1,-1"/>
                      <blockBackground colorName="gainsboro" start="0,0" stop="-1,-1"/>
                    </blockTableStyle>
                    
                    <blockTableStyle id="simple_table">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="#e6e6e6"/>
                    </blockTableStyle>
                    
                    <blockTableStyle id="note_table">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                    </blockTableStyle>
                    <blockTableStyle id="Table2">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                    </blockTableStyle>
                    <blockTableStyle id="Table3">
                      <blockAlignment value="LEFT"/>
                      <lineStyle kind="LINEBELOW" colorName="#e6e6e6" start="1,0" stop="2,-1"/>
                      <blockValign value="TOP"/>
                    </blockTableStyle>
                    <blockTableStyle id="Table4">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="#000000" start="0,-1" stop="1,-1"/>
                    </blockTableStyle>
                    <blockTableStyle id="Table5">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="#8f8f8f" start="0,-1" stop="1,-1"/>
                    </blockTableStyle>

                    <blockTableStyle id="Table51">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="#e6e6e6" start="0,0" stop="-1,-1"/>
                      <lineStyle kind="LINEBEFORE" colorName="#e6e6e6" start="0,0" stop="-1,-1"/>
                      <lineStyle kind="LINEAFTER" colorName="#e6e6e6" start="0,0" stop="-1,-1"/>
                    </blockTableStyle>
                    <blockTableStyle id="Table_heading">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                    </blockTableStyle>
                    <blockTableStyle id="title_tbl">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="#000000" start="0,-1" stop="1,-1"/>
                      <blockBackground colorName="black" start="0,0" stop="-1,-1"/>
                      <blockTextColor colorName="white" start="0,0" stop="0,0"/>
                    </blockTableStyle>
                    <blockTableStyle id="page_tbl">
                      <blockAlignment value="LEFT"/>
                      <blockValign value="TOP"/>
                      <lineStyle kind="LINEBELOW" colorName="#000000" start="0,-1" stop="1,-1"/>
                      <blockBackground colorName="gray" start="0,0" stop="-1,-1"/>
                      <blockTextColor colorName="white" start="0,0" stop="0,0"/>
                    </blockTableStyle>
                    <initialize>
                      <paraStyle name="all" alignment="justify"/>
                    </initialize>
                    
                    <paraStyle name="title_page" fontName="Helvetica-Bold" fontSize="12.0" leading="16" alignment="CENTER" spaceBefore="0.0" spaceAfter="0.0"/>
                    <paraStyle name="subtitle_page" fontName="Helvetica-Bold" fontSize="10.0" leading="13" alignment="CENTER" spaceBefore="0.0" spaceAfter="0.0"/>
                    <paraStyle name="p_line_01" fontName="Helvetica-Bold" fontSize="7.0" leading="9" alignment="LEFT"/>
                    <paraStyle name="p_line_02" fontName="Helvetica-Bold" fontSize="7.0" leading="9" alignment="CENTER"/>
                    <paraStyle name="p_line_03" fontName="Helvetica-Bold" fontSize="7.0" leading="7" spaceBefore="0.0" spaceAfter="0.0" leftIndent="0.0" alignment="LEFT" textColor="#ffffff"/>
                    <paraStyle name="P20" fontName="Helvetica-Bold" fontSize="7.0" leading="7" alignment="CENTER"/>
                    <paraStyle name="P20_DOS" fontName="Helvetica-Bold" fontSize="7.0" leading="7" alignment="LEFT"/>
                    <paraStyle name="DDI" fontName="Helvetica" fontSize="7.0" leading="8" alignment="CENTER"/>
                    
                    <paraStyle name="P20II" fontName="Helvetica-Bold" fontSize="6.0" leading="7" spaceBefore="0.0" spaceAfter="0.0" leftIndent="0.0" alignment="LEFT"/>
                    <paraStyle name="P20I" fontName="Helvetica-Bold" fontSize="7.0" leading="7" spaceBefore="0.0" spaceAfter="0.0" leftIndent="0.0" alignment="LEFT"/>
                    <paraStyle name="DDII" fontName="Helvetica" fontSize="7.0" leading="7" spaceBefore="0.0" spaceAfter="0.0" leftIndent="0.0" alignment="LEFT"/>
                    
                    <paraStyle name="P16I" fontName="Helvetica-Bold" fontSize="6.0" leading="8" alignment="JUSTIFY" textColor="blue"/>
                    <paraStyle name="P16" fontName="Helvetica" fontSize="6.0" leading="8" alignment="JUSTIFY"/>
                    <paraStyle name="P17" fontName="Helvetica" fontSize="6.0" leading="8" alignment="CENTER"/>
                    <paraStyle name="response" fontName="Helvetica-oblique" fontSize="6"/>
                    
                    <paraStyle name="title" fontName="helvetica-bold" fontSize="18.0" leftIndent="0.0" textColor="white"/>
                    <paraStyle name="answer_right" alignment="RIGHT" fontName="helvetica" fontSize="09.0" leftIndent="2.0"/>
                    <paraStyle name="Standard1" fontName="helvetica-bold" alignment="RIGHT" fontSize="09.0"/>
                    <paraStyle name="Standard" alignment="LEFT" fontName="Helvetica-Bold" fontSize="11.0"/>
                    <paraStyle name="header1" fontName="Helvetica" fontSize="11.0"/>
                    
                    <paraStyle name="page" fontName="helvetica" fontSize="11.0" leftIndent="0.0"/>
                    <paraStyle name="question" fontName="helvetica-boldoblique" fontSize="10.0" leftIndent="3.0"/>
                    <paraStyle name="answer_bold" fontName="Helvetica-Bold" fontSize="09.0" leftIndent="2.0"/>
                    <paraStyle name="answer" fontName="helvetica" fontSize="06.5" leftIndent="2.0"/>
                    <paraStyle name="answer1" fontName="helvetica" fontSize="07.0" leftIndent="2.0"/>
                    <paraStyle name="Title" fontName="helvetica" fontSize="20.0" leading="15" spaceBefore="6.0" spaceAfter="6.0" alignment="CENTER"/>
                    <paraStyle name="P2" fontName="Helvetica" fontSize="4.0" leading="5" alignment="CENTER"/>
                    <paraStyle name="comment" fontName="Helvetica" fontSize="14.0" leading="50" spaceBefore="0.0" spaceAfter="0.0"/>
                    <paraStyle name="P1" fontName="Helvetica" fontSize="9.0" leading="12" spaceBefore="0.0" spaceAfter="1.0"/>
                    <paraStyle name="terp_tblheader_Details" fontName="Helvetica-Bold" fontSize="9.0" leading="11" alignment="LEFT" spaceBefore="6.0" spaceAfter="6.0"/>
                    <paraStyle name="terp_default_9" fontName="Helvetica" fontSize="9.0" leading="11" alignment="LEFT" spaceBefore="0.0" spaceAfter="0.0"/>
                    <paraStyle name="terp_default_9_Bold" fontName="Helvetica-Bold" fontSize="9.0" leading="11" alignment="LEFT" spaceBefore="0.0" spaceAfter="0.0"/>
                    <paraStyle name="terp_tblheader_General_Centre_simple" fontName="Helvetica" fontSize="10.0" leading="10" alignment="LEFT" spaceBefore="6.0" spaceAfter="6.0"/>
                    <paraStyle name="terp_tblheader_General_Centre" fontName="Helvetica-Bold" fontSize="10.0" leading="10" alignment="LEFT" spaceBefore="6.0" spaceAfter="6.0"/>
                    <paraStyle name="terp_tblheader_General_right_simple" fontName="Helvetica" fontSize="10.0" leading="10" alignment="RIGHT" spaceBefore="6.0" spaceAfter="6.0"/>
                    <paraStyle name="terp_tblheader_General_right" fontName="Helvetica-Bold" fontSize="10.0" leading="10" alignment="RIGHT" spaceBefore="6.0" spaceAfter="6.0"/>
                    <paraStyle name="descriptive_text" fontName="helvetica-bold" fontSize="18.0" leftIndent="0.0" textColor="white"/>
                    <paraStyle name="descriptive_text_heading" fontName="helvetica-bold" fontSize="18.0" alignment="RIGHT" leftIndent="0.0" textColor="white"/>
                  </stylesheet>
                  <images/>
                  <story>"""

        model = datas.get('model')
        id = datas["id"]
        o = pool.get(model).browse(cr, uid, id)

        tbl_widths = float(_pageSize[0].replace('cm','')) - float(2.10)
        colwidth = "%scm,%scm,%scm"%( (tbl_widths/3), (tbl_widths/3), (tbl_widths/3) )

        rml += """  
            <blockTable colWidths='"""+colwidth+"""' style="simple_table">
                <tr>
                    <td>
                        ccc
                    </td>
                    <td>
                        
                    </td>
                    <td></td>
                </tr>
            </blockTable>
        """





        rml += """</story></document>"""
        report_type = datas.get('report_type', 'pdf')
        create_doc = self.generators[report_type]
        pdf = create_doc(rml, title=self.title)
        return (pdf, report_type)


ReportCfdInvoices('report.cfd_mx.invoices', 'account.invoice','','')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: