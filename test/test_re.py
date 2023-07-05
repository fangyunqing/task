# @Time    : 2023/06/24 15:13
# @Author  : fyq
# @File    : test_re.py
# @Software: PyCharm

__author__ = 'fyq'

import unittest
import uuid

import pyparsing as pp


class TestRe(unittest.TestCase):

    def test_one(self):
        s = "<标题:医美知识大揭秘>\n<小标题:了解医美的基本概念>\n<图片:医美流程>\n\n" \
            "在当今社会，医学美容（医美）已经成为一种趋势，越来越多的人开始关注和追求美丽与自信。" \
            "然而，医美是一个庞大而复杂的领域，其中涵盖了各种各样的技术和手术。在本文中，我们将为您揭开医美的面纱，介绍医美的基本概念。" \
            "\n\n首先，什么是医学美容？简单来说，医学美容是指通过医疗技术和方法来改善外貌或身体的美丽和年轻。" \
            "它不同于传统的化妆品或保养品，而是依赖于医学专业知识和技术的支持。" \
            "医美可以包括非手术方法，如注射美容、激光美容，以及手术方法，如整形手术和整体美容手术。" \
            "\n\n接下来，让我们了解一些常见的医美技术。首先是注射美容，这是通过将特定的物质注射到皮肤表层或深层，" \
            "以达到塑造轮廓、填充皱纹和改善肌肤质地的目的。" \
            "常见的注射物包括肉毒杆菌素（Botox）和透明质酸（Hyaluronic acid）等。" \
            "\n\n另一个常见的医美技术是激光美容，它利用激光器产生的高能量光束来治疗各种皮肤问题，" \
            "如色斑、疤痕、血管扩张和毛发问题等。" \
            "激光美容通常需要多次治疗才能达到最佳效果，但它是一种非侵入性的方法，恢复期相对较短。" \
            "\n\n当然，手术方法也是医美领域中重要的一部分。整形手术是一种通过手术方法改变外貌和身体形态的方式。" \
            "常见的整形手术包括隆鼻、隆胸、双眼皮手术等。整体美容手术则更加综合，它涉及多个部位的改造和调整，旨在实现整体的协调与美感。" \
            "\n\n无论选择哪种医美技术，都应该选择合适的医美机构和医生进行咨询和治疗。" \
            "了解医美的基本概念只是入门，更深入的了解需要专业的医美专家指导。在追求美丽的同时，我们始终应该注重安全和健康。" \
            "\n\n<小标题:医美前必须了解的风险和注意事项>\n<图片:医美风险>\n\n在追求美丽的道路上，我们不能忽视医美所带来的风险和注意事项。" \
            "尽管医美技术的不断进步，但仍然存在一些潜在的风险需要我们认真考虑。\n\n首先是过度依赖医美技术。" \
            "有些人可能过分追求完美的外貌，过度进行医美治疗。这可能导致对自己身体的伤害，甚至对心理健康造成负面影响。" \
            "因此，我们应该保持理性和适度，根据自身情况和需求进行选择。\n\n其次是选择合适的医美机构和医生。" \
            "在选择医美机构和医生时，我们应该考虑其资质、声誉和经验。最好选择具备相关资质认证和丰富经验的医美专家，进行咨询和治疗。" \
            "\n\n此外，我们还要了解可能出现的风险和并发症。" \
            "不同的医美技术可能会产生不同的风险，如感染、出血、过敏反应等。" \
            "在进行医美治疗前，我们应该充分了解可能的风险，并与医生进行详细的沟通和咨询。\n\n" \
            "总的来说，医美是一个复杂而广泛的领域，涉及多种技术和手术。" \
            "在追求美丽的同时，我们应该了解医美的基本概念，选择合适的医美机构和医生，并注意可能的风险和注意事项。" \
            "只有在安全和健康的前提下，我们才能真正享受医美带来的美丽和自信。"

        title_tag = pp.Suppress("<标题:") + pp.Word(pp.pyparsing_unicode.alphanums + pp.alphanums) + pp.Suppress(">")
        little_title_tag = pp.Suppress("<小标题:") + pp.Word(pp.pyparsing_unicode.alphanums) + pp.Suppress(">")
        image_tag = pp.Suppress("<图片:") + pp.Word(pp.pyparsing_unicode.alphanums) + pp.Suppress(">")
        s_lines = s.split()
        title = None

        def create_title_title_style(tt: str):
            return '<h3 data-diagnose-id="{}">{}</h3>'.format(str(uuid.uuid1()).replace("-", ""), tt)

        """
            <p style="text-align: center" 
               data-bjh-caption-id="cap-88948672" 
               class="bjh-image-container cant-justify" 
               data-bjh-helper-id="1688451002400" 
               data-bjh-caption-text="" 
               data-bjh-caption-length="16">
               <img src="http://copyright.bdstatic.com/vcg/creative/9f1d897fd0061ad809bfa95780c320c9.jpg" 
                    data-bjh-origin-src="http://copyright.bdstatic.com/vcg/creative/9f1d897fd0061ad809bfa95780c320c9.jpg" 
                    data-bjh-type="IMG" 
                    data-bjh-params="{"is_legal":1,"index":1,"credit_line":"","res_id":"","asset_family":""}" 
                    data-diagnose-id="441f9d22cc27f34d7b2ac31262a1f4b8" 
                    data-bjh-text-align="center" 
                    data-w="800" 
                    data-h="1200">
            </p>
        """

        for ss_index, ss in enumerate(s_lines.copy()):
            for ps, s, e in title_tag.scan_string(ss):
                s_lines[ss_index] = "".join(ps)
            for ps, s, e in little_title_tag.scan_string(ss):
                s_lines[ss_index] = create_title_title_style("".join(ps))
            for ps, s, e in image_tag.scan_string(ss):
                print("".join(ps))

        for ss in s_lines:
            print(ss)
