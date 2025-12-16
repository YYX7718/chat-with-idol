import re

# 仅示例性的禁止词集合，生产应维护更完整的规则集及上下文检查
_FORBIDDEN_PATTERNS = [
    r"\b必然\b",
    r"\b注定\b",
    r"\b灾难\b",
    r"\b一定会\b",
]

def check_text_compliance(text: str):
    """检查文本是否包含绝对化或恐吓性语言。

    返回 (is_ok: bool, violations: list)
    """
    violations = []
    for pat in _FORBIDDEN_PATTERNS:
        if re.search(pat, text):
            violations.append(pat)
    return (len(violations) == 0, violations)
