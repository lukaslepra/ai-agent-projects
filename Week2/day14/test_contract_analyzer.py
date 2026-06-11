# test_contract_analyzer.py
# 练习 3：pytest 断言验证
# 目标：写 3 个测试函数，验证 API 返回格式是否符合预期
#
# 运行方式：
# cd E:\Agent岗位培训\Week2\day14-practice
# pytest test_contract_analyzer.py -v

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import pytest
from contract_analyzer import ContractAnalyzer

# 测试用的合同条款（固定内容，保证测试可重复）
TEST_CLAUSE = """
乙方须在签约后7个工作日内完成全部交付物，
如逾期，每日按合同总金额的5%计算违约金，无上限。
"""


@pytest.fixture
def analyzer():
    """pytest fixture：每个测试函数运行前自动创建一个新的 analyzer"""
    return ContractAnalyzer()


def test_analyze_returns_dict(analyzer):
    """测试1：analyze 必须返回字典类型"""
    result = analyzer.analyze(TEST_CLAUSE)
    assert isinstance(result, dict)


def test_analyze_has_required_fields(analyzer):
    """测试2：返回结果必须包含4个必填字段"""
    result = analyzer.analyze(TEST_CLAUSE)
    assert "risk_level" in result
    assert "risk_points" in result
    assert "suggestions" in result
    assert "summary" in result


def test_risk_level_is_valid(analyzer):
    """测试3：risk_level 的值只能是 低/中/高 之一"""
    result = analyzer.analyze(TEST_CLAUSE)
    assert result["risk_level"] in ["低", "中", "高"]
