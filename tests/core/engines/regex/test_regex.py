from typing import List

import pytest

from deepsecrets.core.engines.regex import RegexEngine
from deepsecrets.core.model.file import File
from deepsecrets.core.model.finding import Finding, FindingMerger, FindingResponse
from deepsecrets.core.rulesets.regex import RegexRulesetBuilder
from deepsecrets.core.tokenizers.full_content import FullContentTokenizer
from deepsecrets.core.utils.fs import get_path_inside_package


@pytest.fixture(scope='module')
def file():
    path = 'tests/fixtures/regex_checks.txt'
    return File(path=path, relative_path=path)


@pytest.fixture(scope='module')
def regex_engine():
    builder = RegexRulesetBuilder()
    builder.with_rules_from_file(get_path_inside_package('rules/regexes.json'))
    return RegexEngine(ruleset=builder.rules)


def test_1(file: File, regex_engine: RegexEngine):
    findings: List[Finding] = []
    tokens = FullContentTokenizer().tokenize(file)
    for token in tokens:
        token_findings = regex_engine.search(token)
        for finding in token_findings:
            finding.map_on_file(file=file, relative_start=token.span[0])
            findings.append(finding)

    for finding in findings:
        finding.map_on_file(file=file, relative_start=finding.start_pos)
        finding.choose_final_rule()

    assert len(findings) == 9
    assert findings[0].rules[0].id == 'S0'
    assert findings[1].rules[0].id == 'S0'
    assert findings[2].rules[0].id == 'S1'
    assert findings[3].rules[0].id == 'S2'
    assert findings[4].rules[0].id == 'S3'
    assert findings[5].rules[0].id == 'S4'
    assert findings[6].rules[0].id == 'S5'
    assert findings[7].rules[0].id == 'S19'
    assert findings[8].rules[0].id == 'S19'

    findings = FindingMerger(findings).merge()
    assert len(findings) == 9

    response = FindingResponse.from_list(findings)
