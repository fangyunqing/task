# @Time    : 2023/07/19 14:07
# @Author  : fyq
# @File    : t.py
# @Software: PyCharm

__author__ = 'fyq'

import json
import time

import xlwings as xl
from PIL import ImageGrab
from munch import Munch

if __name__ == "__main__":
    s = (
        '''[{'''
        '''"care of": {'''
        '''"词汇": "care of",'''
        '''"词性": "短语",'''
        '''"含义": "寄送到某人的地址并由某人代收",'''
        '''"发音": {'''
        '''"英式发音": "keər ɒv",'''
        '''"美式发音": "ker ɔv"'''
        '''},'''
        '''"语句详解": "用于邮寄地址中，表示邮件要寄到某人的地址，并由该地址上的某人代为收取。",'''
        '''"用法": "用于邮寄地址",'''
        '''"用法示例":['''
        '''{'''
        '''"中文": "请将信寄至约翰·史密斯，地址为：XXX 街道 123 号，行政区域，中国。抬头写作：“约翰·史密斯（care of）”。",'''
        '''"英文": "Please send the letter to John Smith, address: 123 Main Street, District, China. Attention should be written as 'John Smith (care of)'."'''
        ''' },'''
        ''' {'''
        '''"中文": "父母出差，将孩子送到爷爷家，邮寄地址可以写作：“爷爷姓名（care of 孩子姓名）”。",'''
        '''"英文": "When parents are on a business trip and send their child to their grandfather's house, the mailing address can be written as 'Grandfather's Name (care of Child's Name)'."'''
        '''}'''
        ''']'''
        '''},'''
        '''"care for": {'''
        '''"词汇": "care for",'''
        '''"词性": "动词短语",'''
        '''"含义": "照顾、关心、喜欢",'''
        ''' "发音": {'''
        '''"英式发音": "keər fɔː(r)",'''
        '''"美式发音": "ker fɔr"'''
        '''},'''
        '''"语句详解": "表示对某人或某事物进行照料、关心或喜欢。",'''
        '''"用法": "常用于口语和书面语",'''
        '''"用法示例": ['''
        '''{'''
        '''"中文": "她照顾小狗得很好，总是给它洗澡、喂食并带它出去散步。",'''
        '''"英文": "She cares for the puppy very well, always bathing, feeding, and taking it for walks."'''
        '''},{'''
        '''"中文": "我真的很喜欢这件衣服，你可以帮我照看一下吗？",'''
        '''"英文": "I really like this dress. Can you care for it for me?"'''
        '''},'''
        '''{'''
        '''"中文": "我会一直关心你，无论你走到哪里。",'''
        '''"英文": "I will care for you no matter where you go."'''
        '''},{'''
        '''"中文": "医生建议他要好好照顾自己的健康。",'''
        '''"英文": "The doctor advised him to take good care of his health."'''
        '''},{'''
        '''"中文": "我真的很在乎你的感受，你可以告诉我你需要什么吗？",'''
        '''"英文": "I really care for your feelings. Can you tell me what you need?"'''
        '''},{'''
        '''"中文": "这个组织致力于照顾贫困儿童的生活。",'''
        '''"英文": "This organization is committed to caring for the lives of underprivileged children."'''
        '''}]}}]'''

    )
    nodes = ["词汇", "词性", "含义", ""]
    ss = json.loads(s)
    # 检测格式 [{{} {}}]
    assert len(ss) == 1
    data1 = ss[0]
    m_list = []
    for k1, v1 in data1.items():
        m = Munch()
        m_list.append(m)
        assert "词汇" in v1
        assert isinstance(v1["词汇"], str)
        m.word = v1["词汇"]

        assert "词性" in v1
        assert isinstance(v1["词性"], str)
        m.pos = v1["词性"]

        assert "含义" in v1
        assert isinstance(v1["含义"], str)
        m.meaning = v1["含义"]

        assert "发音" in v1
        assert isinstance(v1["发音"], dict)
        m.pronunciation = Munch()
        assert "英式发音" in v1["发音"]
        assert "美式发音" in v1["发音"]
        for k2, v2 in v1["发音"].items():
            if k2 == "英式发音":
                m.pronunciation.uk = v2
            elif k2 == "美式发音":
                m.pronunciation.us = v2

        assert "语句详解" in v1
        assert isinstance(v1["语句详解"], str)
        m.sentence = v1["语句详解"]

        assert "用法" in v1
        assert isinstance(v1["用法"], str)
        m.use = v1["用法"]

        assert "用法示例" in v1
        assert isinstance(v1["用法示例"], list)
        m.usage = []
        for uu in v1["用法示例"]:
            assert isinstance(uu, dict)
            assert "英文" in uu
            assert "中文" in uu
            mm = Munch()
            mm.zh = uu["中文"]
            mm.en = uu["英文"]
            m.usage.append(mm)

    app = xl.App(visible=False, add_book=False)
    try:
        wb = app.books.open("translate.xlsx")
        try:
            sheet = wb.sheets[0]
            b = 66
            for m_idx, m in enumerate(m_list):
                b += m_idx
                s_b = chr(b)
                sheet.range(f"{s_b}1").value = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
                sheet.range(f"{s_b}1").column_width = 24
                sheet.range(f"{s_b}1").wrap_text = True
                sheet.range(f"{s_b}1").rows.autofit()
                if sheet.range(f"{s_b}1").row_height < 24:
                    sheet.range(f"{s_b}1").row_height = 24
                sheet.range(f"{s_b}2").value = m.meaning
                sheet.range(f"{s_b}2").column_width = 24
                sheet.range(f"{s_b}2").wrap_text = True
                sheet.range(f"{s_b}3").value = "\n".join([f"{k}：【{v}】" for k, v in m.pronunciation.items()])
                sheet.range(f"{s_b}3").column_width = 24
                sheet.range(f"{s_b}3").wrap_text = True
                sheet.range(f"{s_b}4").value = m.use
                sheet.range(f"{s_b}4").column_width = 24
                sheet.range(f"{s_b}4").wrap_text = True
            s_b = chr(b)
            rng = sheet.range(f"A1:{s_b}4")
            rng.api.CopyPicture()
            time.sleep(2)
            sheet.api.Paste()
            image_name = 'text.png'
            pic = sheet.pictures[0]
            pic.api.Copy()
            time.sleep(2)
            img = ImageGrab.grabclipboard()
            img.save(image_name)
            pic.delete()


        finally:
            wb.close()
    finally:
        app.quit()
