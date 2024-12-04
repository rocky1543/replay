# encoding: utf-8
import akshare as ak
import json
import logging
import re
import requests
import time
from datetime import datetime
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm
from docx.shared import Pt, RGBColor
from pyquery import PyQuery as pq


def save_word_text(lian_ban_data, print_type="A5"):
    # 创建文档
    doc = Document()
    doc.styles['Normal'].font.name = 'Times New Roman'
    doc.styles['Normal'].element.rPr.rFonts.set(qn('w:eastAsia'), u'宋体')
    doc.styles['Normal'].font.size = Pt(10)
    doc.styles['Normal'].font.color.rgb = RGBColor(0, 0, 0)

    # 设置页面大小为A5
    section = doc.sections[0]
    if print_type == "A5":
        section.page_width = Cm(14.8)
        section.page_height = Cm(21)
    else:
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)

    section.left_margin = Cm(1.27)
    section.right_margin = Cm(1.27)
    section.top_margin = Cm(1.27)
    section.bottom_margin = Cm(1.27)

    # 添加标题，0表示样式为title
    h1 = doc.add_heading("连板天梯", level=2)
    h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for line in lian_ban_data:
        # 添加段落
        doc.add_paragraph(line)

    doc.save('result/连板天梯.docx')


def get_lian_ban_data():
    lian_ban_map = {}
    fo = open("./input/连板天梯_name.txt", "w")
    for line in open("./input/连板天梯.txt"):
        data = line.split("\t")
        name = data[0].strip()
        ban_num = data[-1].strip()
        fo.write(name + "," + ban_num + "板\n")

        lian_ban_list = lian_ban_map.get(ban_num, [])
        lian_ban_list.append(name)
        lian_ban_map[ban_num] = lian_ban_list

    data = []
    for key, val in lian_ban_map.items():
        data.append("{}板: {}".format(key, ", ".join(val)))
    print("data:", data)
    return data


if __name__ == '__main__':
    lian_ban_data = get_lian_ban_data()
    save_word_text(lian_ban_data, "A4")
