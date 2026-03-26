import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import json
from legal_store import extract_crossrefs


def test_extract_kr_explicit_article_ref():
    text = "제15조에 따른 동의를 받은 경우에는 제17조 제1항에 따라 제공할 수 있다."
    refs = extract_crossrefs(text, "KR")
    articles = [r["article"] for r in refs if r["type"] == "internal"]
    assert 15 in articles
    assert 17 in articles


def test_extract_kr_external_law_ref():
    text = "「정보통신망 이용촉진 및 정보보호 등에 관한 법률」 제24조에 따른 조치"
    refs = extract_crossrefs(text, "KR")
    external = [r for r in refs if r["type"] == "external"]
    assert len(external) >= 1
    assert external[0]["law"] == "정보통신망 이용촉진 및 정보보호 등에 관한 법률"
    assert external[0]["article"] == 24


def test_extract_kr_no_refs():
    text = "이 법은 개인정보의 처리에 관한 사항을 정함으로써 개인의 자유와 권리를 보호한다."
    refs = extract_crossrefs(text, "KR")
    assert refs == []


def test_extract_eu_article_ref():
    text = "In accordance with Article 6(1) of Regulation (EU) 2016/679."
    refs = extract_crossrefs(text, "EU")
    assert any(r["article"] == 6 for r in refs)


def test_extract_eu_no_refs():
    text = "This regulation shall be binding in its entirety."
    refs = extract_crossrefs(text, "EU")
    assert refs == []
