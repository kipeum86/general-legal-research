import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import json
import tempfile
import shutil
from legal_store import (
    extract_crossrefs, write_article_md, update_index, lookup,
    update_crossref_reverse_index, query_reverse_crossrefs,
)


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


def test_write_article_creates_md_file(tmp_path):
    write_article_md(
        law_name="개인정보보호법",
        law_dir="pipa",
        article_number=17,
        title="개인정보의 제공",
        content="① 개인정보처리자는 다음 각 호...",
        jurisdiction="KR",
        source="law.go.kr",
        source_id="001823",
        library_dir=tmp_path,
    )
    art_file = tmp_path / "pipa" / "art017.md"
    assert art_file.exists()
    text = art_file.read_text(encoding="utf-8")
    assert "law: 개인정보보호법" in text
    assert "article_number: 17" in text
    assert "grade: A" in text
    assert "fetched_at:" in text
    assert "① 개인정보처리자는 다음 각 호" in text


def test_write_article_overwrites_existing(tmp_path):
    for content in ["old content", "new content"]:
        write_article_md(
            law_name="테스트법",
            law_dir="test-law",
            article_number=1,
            title="테스트",
            content=content,
            jurisdiction="KR",
            source="test",
            source_id="000",
            library_dir=tmp_path,
        )
    text = (tmp_path / "test-law" / "art001.md").read_text(encoding="utf-8")
    assert "new content" in text
    assert "old content" not in text


def test_write_article_creates_meta_json(tmp_path):
    write_article_md(
        law_name="테스트법",
        law_dir="test-law",
        article_number=1,
        title="테스트",
        content="내용",
        jurisdiction="KR",
        source="test",
        source_id="000",
        library_dir=tmp_path,
    )
    meta = tmp_path / "test-law" / "_meta.json"
    assert meta.exists()
    data = json.loads(meta.read_text())
    assert data["law_name"] == "테스트법"
    assert data["jurisdiction"] == "KR"


def test_update_index_creates_files(tmp_path):
    update_index(
        law_name="테스트법",
        law_dir="test-law",
        jurisdiction="KR",
        articles=[{"number": 1, "title": "총칙"}, {"number": 2, "title": "정의"}],
        index_dir=tmp_path,
    )
    assert (tmp_path / "article-index.json").exists()
    assert (tmp_path / "source-registry.json").exists()
    idx = json.loads((tmp_path / "article-index.json").read_text())
    assert "테스트법" in idx


def test_lookup_hit(tmp_path):
    write_article_md(
        law_name="테스트법", law_dir="test-law", article_number=1,
        title="총칙", content="내용", jurisdiction="KR",
        source="test", source_id="000", library_dir=tmp_path,
    )
    result = lookup("테스트법", article=1, library_dir=tmp_path)
    assert result is not None
    assert result["hit"] is True
    assert "내용" in result["content"]


def test_lookup_miss(tmp_path):
    result = lookup("존재안하는법", library_dir=tmp_path)
    assert result is None or result["hit"] is False


def test_lookup_staleness_warning(tmp_path):
    art_path = tmp_path / "test-law"
    art_path.mkdir(parents=True)
    old_date = "2025-01-01T00:00:00+00:00"
    content = f"---\nlaw: 테스트법\narticle_number: 1\nfetched_at: {old_date}\n---\n내용"
    (art_path / "art001.md").write_text(content, encoding="utf-8")
    # Need _meta.json for lookup to find the law dir
    meta = json.dumps({"law_name": "테스트법", "law_dir": "test-law", "jurisdiction": "KR"})
    (art_path / "_meta.json").write_text(meta, encoding="utf-8")
    result = lookup("테스트법", article=1, library_dir=tmp_path)
    assert result is not None
    assert result.get("stale") is True


def test_reverse_index_creation(tmp_path):
    refs = [
        {"type": "external", "law": "정보통신망법", "article": 24, "raw": "「정보통신망법」 제24조"},
    ]
    update_crossref_reverse_index(
        source_law="개인정보보호법",
        source_article=17,
        cross_refs=refs,
        index_dir=tmp_path,
    )
    result = query_reverse_crossrefs("정보통신망법", article=24, index_dir=tmp_path)
    assert len(result) >= 1
    assert result[0]["source_law"] == "개인정보보호법"
    assert result[0]["source_article"] == 17
