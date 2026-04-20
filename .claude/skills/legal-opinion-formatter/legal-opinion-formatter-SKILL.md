---
name: legal-opinion-formatter
description: >
  Format legal opinions as professional-format Word documents (.docx).
  Use this skill whenever the user wants to generate, format, or export a legal opinion,
  legal memorandum, legal advice letter, or formal analysis letter as a Word document.
  Triggers include: "법률의견서 작성", "legal opinion 생성", "legal opinion docx",
  "의견서 포맷", "format as legal letter", "make it look like a professional legal letter",
  "export to Word", "docx로 변환", or any request to produce a professional legal
  document in .docx format. Also trigger when the user has already generated legal
  opinion text and wants it formatted professionally, or when creating legal documents
  that need letterhead, signature blocks, confidentiality markings, or formal legal
  document structure. Supports English, Korean (한국어), and bilingual documents.
---

# Legal Opinion Letter Formatter

Generate professional-format legal opinion letters as .docx files using `python-docx`.

## When to Activate

- User requests a legal opinion, legal memo, or formal analysis letter as a .docx file
- User has generated legal opinion text and wants professional formatting
- User mentions "법률의견서", "법률검토보고서", "legal opinion letter", "legal memo"
- User asks to "format this as a professional legal letter" or similar
- User wants to export legal analysis to a Word document

---

## Document Architecture

A professional legal opinion letter follows a specific visual hierarchy. The formatter
must produce documents that look like polished, audit-friendly legal memoranda — not a
Word template with default styles.

### Visual Design Principles

1. **Typography**: Use a serif font for body text (Times New Roman or Garamond, 11-12pt)
   and a clean sans-serif for the letterhead (Arial or Calibri). Never mix more than
   two font families.

2. **Spacing**: Use 1.15 line spacing for body text (not single, not double).
   Add 6pt spacing after paragraphs. Use generous margins (1 inch or 2.54cm all sides).

3. **Color palette**: Keep it conservative. Black (#000000) for body text,
   dark navy (#1B2A4A) or dark charcoal (#333333) for letterhead/headings.
   One accent color maximum for decorative lines (navy or dark gold #8B7355).

4. **Hierarchy signals**: Use horizontal rules, font weight, and spacing to create
   visual hierarchy — not excessive colors or large font sizes.

---

## Document Structure

Every legal opinion letter consists of these components, in order. Some are optional
depending on context — the agent should determine which to include based on the
opinion type and user instructions.

### 1. Letterhead Block (Header)

The letterhead appears in the document header (first page only, or all pages).

```
KP Legal Orchestrator                ← Bold, 14-16pt, sans-serif, navy
AI Legal Workflow System             ← 9pt, italic or light weight
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ← Thin horizontal rule (navy or gold)
[Address Line 1]  |  Tel: [Phone]  |  [Email]  |  [Website]
```

For Korean-format outputs:
```
KP 리걸 오케스트레이터
KP Legal Orchestrator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[주소]  |  전화: [번호]  |  [이메일]  |  [웹사이트]
```

**Implementation notes:**
- Place in the document header using `python-docx` header functionality
- Use placeholder text: `[FIRM NAME]`, `[ADDRESS]`, `[PHONE]`, `[EMAIL]`, `[WEBSITE]`
- Add a bottom border (thin line) to separate letterhead from body
- First page header can differ from subsequent pages

### 2. Classification Marking (Optional)

If the opinion is privileged or confidential:

```
PRIVILEGED & CONFIDENTIAL
INTERNAL LEGAL WORKFLOW DRAFT
```

Or in Korean:
```
비밀유지 / 내부 법률 워크플로 초안
```

- Centered, bold, 9-10pt, all caps
- Placed immediately below letterhead, above date

### 3. Date & Addressee Block

```
[Date]                               ← Left-aligned, same font as body

[Recipient Name]
[Recipient Title]
[Company/Organization Name]
[Address Line 1]
[Address Line 2]
```

- Date format: "March 5, 2026" (English) or "2026년 3월 5일" (Korean)
- Use placeholders: `[RECIPIENT NAME]`, `[RECIPIENT TITLE]`, etc.

### 4. Reference Line

```
Re:    [Subject Matter of the Opinion]
       [Additional reference information if needed]
```

Or Korean:
```
건명:   [의견서 제목/대상]
```

- "Re:" or "건명:" in bold, followed by the subject
- Can span multiple lines with hanging indent

### 5. Salutation

```
Dear [Recipient Name]:
```

Or Korean:
```
[수신인 이름] 귀하
```

### 6. Body — Introduction / Purpose

A brief paragraph stating:
- Who requested the opinion
- What question(s) were asked
- The scope and purpose of the opinion
- Any limitations or qualifications on scope

### 7. Body — Executive Summary (Optional but Recommended)

A concise summary of the conclusions (2-4 sentences), placed before the detailed
analysis. This allows busy executives/clients to get the bottom line immediately.

### 8. Body — Background / Facts

Statement of the factual background on which the opinion is based.
Include a disclaimer that the opinion relies on the accuracy of stated facts.

### 9. Body — Issues Presented

Clearly numbered list of legal questions addressed:

```
The specific legal issues addressed in this opinion are:

1.  Whether [first legal question]...
2.  Whether [second legal question]...
```

### 10. Body — Applicable Law

Summary of the relevant legal framework, statutes, regulations, and precedents.

### 11. Body — Analysis / Discussion

The core legal analysis. Each issue should be addressed under its own heading:

```
A.  [Issue 1 Heading]

    [Analysis text...]

B.  [Issue 2 Heading]

    [Analysis text...]
```

**Formatting rules for analysis section:**
- Use letter headings (A, B, C) or Roman numerals (I, II, III) for top-level issues
- Use numbered sub-points (1, 2, 3) for sub-arguments
- Indent block quotes of statutes or case citations
- Bold key legal conclusions within paragraphs

### 12. Body — Conclusions / Opinion

Clearly stated conclusions corresponding to each issue:

```
Based on the foregoing analysis, it is our opinion that:

1.  [Conclusion for Issue 1]...
2.  [Conclusion for Issue 2]...
```

### 13. Body — Qualifications & Limitations

Standard qualifications:
- Jurisdictional scope
- Reliance on stated facts
- No opinion on matters not specifically addressed
- Changes in law disclaimer

### 14. Body — Recommendations (Optional)

Practical recommendations for the client based on the legal conclusions.

### 15. Closing & Signature Block

```
Very truly yours,

[ORGANIZATION NAME]


____________________________
[SPECIALIST NAME]
[Title / Position]
[Reference / Registration]
```

Korean:
```
이상과 같이 의견을 드립니다.

[조직명]


____________________________
[스페셜리스트 이름]
[직위]
[참조 번호 / 등록 정보]
```

### 16. Disclaimers / Notices (Optional)

Standard legal disclaimers in smaller font (8-9pt) at the bottom or as a footnote:
- Not legal advice to third parties
- Confidentiality notice
- Limitation on reliance

### 17. Footer

Page numbering: "Page X of Y" or "- X -" centered
Optional: Document reference number, "CONFIDENTIAL" marking

---

## python-docx Implementation Guide

### Required Setup

```python
pip install python-docx
```

### Core Imports

```python
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import datetime
```

### Page Setup

```python
doc = Document()

# Set default font
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(11)
font.color.rgb = RGBColor(0, 0, 0)

# Set East Asian font for Korean text support
rPr = style.element.get_or_add_rPr()
rFonts = rPr.get_or_add_rFonts()
rFonts.set(qn('w:eastAsia'), '맑은 고딕')  # Malgun Gothic for Korean

# Page margins (1 inch = 914400 EMU)
for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1.25)  # Slightly wider left for binding
    section.right_margin = Inches(1)
    section.page_width = Inches(8.5)    # US Letter
    section.page_height = Inches(11)
```

### Letterhead Header

```python
def create_letterhead(doc, firm_info):
    """Create professional letterhead in document header."""
    section = doc.sections[0]
    section.different_first_page_header_footer = True

    header = section.first_page_header

    # Firm name
    p_firm = header.paragraphs[0]
    p_firm.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p_firm.add_run(firm_info.get('name', 'KP Legal Orchestrator'))
    run.font.name = 'Arial'
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x1B, 0x2A, 0x4A)  # Navy

    # Subtitle
    if firm_info.get('subtitle'):
        p_sub = header.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p_sub.add_run(firm_info['subtitle'])
        run.font.name = 'Arial'
        run.font.size = Pt(9)
        run.font.italic = True
        run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # Horizontal rule
    p_rule = header.add_paragraph()
    p_rule.paragraph_format.space_before = Pt(4)
    p_rule.paragraph_format.space_after = Pt(4)
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'  <w:bottom w:val="single" w:sz="6" w:space="1" w:color="1B2A4A"/>'
        f'</w:pBdr>'
    )
    p_rule.paragraph_format.element.get_or_add_pPr().append(pBdr)

    # Contact info line
    contact_parts = []
    if firm_info.get('address'):
        contact_parts.append(firm_info['address'])
    if firm_info.get('phone'):
        contact_parts.append(f"Tel: {firm_info['phone']}")
    if firm_info.get('email'):
        contact_parts.append(firm_info['email'])
    if firm_info.get('website'):
        contact_parts.append(firm_info['website'])

    if contact_parts:
        p_contact = header.add_paragraph()
        p_contact.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p_contact.add_run('  |  '.join(contact_parts))
        run.font.name = 'Arial'
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # Subsequent page header (simpler)
    header2 = section.header
    p2 = header2.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run2 = p2.add_run(firm_info.get('name', 'KP Legal Orchestrator'))
    run2.font.name = 'Arial'
    run2.font.size = Pt(9)
    run2.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    # Add bottom border to subsequent header
    pBdr2 = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="1" w:color="CCCCCC"/>'
        f'</w:pBdr>'
    )
    p2.paragraph_format.element.get_or_add_pPr().append(pBdr2)
```

### Custom Styles

```python
def setup_styles(doc):
    """Define custom paragraph styles for the legal opinion."""
    styles = doc.styles

    # --- Heading styles ---
    # Section Heading (e.g., "I. BACKGROUND")
    s = styles.add_style('LOHeading1', 1)  # 1 = WD_STYLE_TYPE.PARAGRAPH
    s.font.name = 'Times New Roman'
    s.font.size = Pt(13)
    s.font.bold = True
    s.font.color.rgb = RGBColor(0x1B, 0x2A, 0x4A)
    s.paragraph_format.space_before = Pt(18)
    s.paragraph_format.space_after = Pt(8)
    s.paragraph_format.keep_with_next = True

    # Sub-heading (e.g., "A. First Issue")
    s2 = styles.add_style('LOHeading2', 1)
    s2.font.name = 'Times New Roman'
    s2.font.size = Pt(12)
    s2.font.bold = True
    s2.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    s2.paragraph_format.space_before = Pt(12)
    s2.paragraph_format.space_after = Pt(6)
    s2.paragraph_format.keep_with_next = True

    # Body text
    s3 = styles.add_style('LOBody', 1)
    s3.font.name = 'Times New Roman'
    s3.font.size = Pt(11)
    s3.font.color.rgb = RGBColor(0, 0, 0)
    s3.paragraph_format.space_after = Pt(6)
    s3.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    s3.paragraph_format.line_spacing = 1.15
    # Set first line indent for body paragraphs (optional, formal style)
    # s3.paragraph_format.first_line_indent = Inches(0.5)

    # Block quote (for statute citations, case excerpts)
    s4 = styles.add_style('LOBlockQuote', 1)
    s4.font.name = 'Times New Roman'
    s4.font.size = Pt(10)
    s4.font.italic = True
    s4.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    s4.paragraph_format.left_indent = Inches(0.75)
    s4.paragraph_format.right_indent = Inches(0.5)
    s4.paragraph_format.space_before = Pt(6)
    s4.paragraph_format.space_after = Pt(6)
    s4.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    s4.paragraph_format.line_spacing = 1.0

    # Confidential marking
    s5 = styles.add_style('LOConfidential', 1)
    s5.font.name = 'Arial'
    s5.font.size = Pt(9)
    s5.font.bold = True
    s5.font.all_caps = True
    s5.font.color.rgb = RGBColor(0x80, 0x00, 0x00)  # Dark red
    s5.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s5.paragraph_format.space_before = Pt(0)
    s5.paragraph_format.space_after = Pt(12)

    # Signature block
    s6 = styles.add_style('LOSignature', 1)
    s6.font.name = 'Times New Roman'
    s6.font.size = Pt(11)
    s6.font.color.rgb = RGBColor(0, 0, 0)
    s6.paragraph_format.space_after = Pt(2)
    s6.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    # Small disclaimer text
    s7 = styles.add_style('LODisclaimer', 1)
    s7.font.name = 'Arial'
    s7.font.size = Pt(8)
    s7.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    s7.paragraph_format.space_before = Pt(12)
    s7.paragraph_format.space_after = Pt(2)
    s7.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    return styles
```

### Footer with Page Numbers

```python
def create_footer(doc, confidential=False):
    """Add footer with page numbers and optional confidential marking."""
    section = doc.sections[0]
    footer = section.footer
    footer.is_linked_to_previous = False

    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if confidential:
        run_conf = p.add_run("CONFIDENTIAL")
        run_conf.font.name = 'Arial'
        run_conf.font.size = Pt(7)
        run_conf.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
        run_conf.font.all_caps = True

        # Add line break
        from docx.oxml import OxmlElement
        br = OxmlElement('w:br')
        p._element.append(br)

    # Page number: "- X -" format
    run1 = p.add_run("- ")
    run1.font.name = 'Arial'
    run1.font.size = Pt(9)
    run1.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # Insert PAGE field
    fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    p._element.append(fldChar1)
    instrText = parse_xml(f'<w:instrText {nsdecls("w")}> PAGE </w:instrText>')
    p._element.append(instrText)
    fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    p._element.append(fldChar2)

    run2 = p.add_run(" -")
    run2.font.name = 'Arial'
    run2.font.size = Pt(9)
    run2.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
```

### Adding Content Sections

```python
def add_confidential_marking(doc, text="PRIVILEGED & CONFIDENTIAL\nINTERNAL LEGAL WORKFLOW DRAFT"):
    """Add confidentiality marking at top of document."""
    for line in text.split('\n'):
        p = doc.add_paragraph(style='LOConfidential')
        p.add_run(line)

def add_date_and_addressee(doc, date_str, recipient):
    """Add date and recipient block."""
    # Date
    p_date = doc.add_paragraph(style='LOBody')
    p_date.add_run(date_str)
    p_date.paragraph_format.space_after = Pt(18)

    # Recipient
    for line in recipient:
        p = doc.add_paragraph(style='LOBody')
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(line)
        if line == recipient[0]:  # Bold the name
            run.bold = True

def add_reference_line(doc, subject):
    """Add Re: line."""
    p = doc.add_paragraph(style='LOBody')
    p.paragraph_format.space_before = Pt(12)
    run_re = p.add_run("Re:\t")
    run_re.bold = True
    run_subject = p.add_run(subject)
    run_subject.bold = True

def add_section_heading(doc, number, title):
    """Add a numbered section heading (e.g., 'I. BACKGROUND')."""
    p = doc.add_paragraph(style='LOHeading1')
    p.add_run(f"{number}.\t{title.upper()}")

def add_sub_heading(doc, label, title):
    """Add a sub-heading (e.g., 'A. First Issue')."""
    p = doc.add_paragraph(style='LOHeading2')
    p.add_run(f"{label}.\t{title}")

def add_body_paragraph(doc, text, first_line_indent=False):
    """Add a body text paragraph."""
    p = doc.add_paragraph(style='LOBody')
    p.add_run(text)
    if first_line_indent:
        p.paragraph_format.first_line_indent = Inches(0.5)
    return p

def add_block_quote(doc, text):
    """Add an indented block quote (for statutes, citations)."""
    p = doc.add_paragraph(style='LOBlockQuote')
    p.add_run(text)
    return p

def add_signature_block(doc, firm_name, attorney_name, title, bar_number=None):
    """Add closing and signature block."""
    # Closing
    p_closing = doc.add_paragraph(style='LOBody')
    p_closing.paragraph_format.space_before = Pt(24)
    p_closing.add_run("Very truly yours,")

    # Firm name
    p_firm = doc.add_paragraph(style='LOSignature')
    p_firm.paragraph_format.space_before = Pt(6)
    run = p_firm.add_run(firm_name)
    run.bold = True

    # Signature line (space for physical signature)
    p_space = doc.add_paragraph(style='LOSignature')
    p_space.paragraph_format.space_before = Pt(36)
    p_space.add_run("____________________________")

    # Signatory info
    p_name = doc.add_paragraph(style='LOSignature')
    run = p_name.add_run(attorney_name)
    run.bold = True

    p_title = doc.add_paragraph(style='LOSignature')
    p_title.add_run(title)

    if bar_number:
        p_bar = doc.add_paragraph(style='LOSignature')
        p_bar.add_run(bar_number)
```

### Korean Signature Block Variant

```python
def add_signature_block_ko(doc, firm_name, attorney_name, title, bar_number=None):
    """Korean-style closing and signature block."""
    p_closing = doc.add_paragraph(style='LOBody')
    p_closing.paragraph_format.space_before = Pt(24)
    p_closing.add_run("이상과 같이 의견을 드립니다.")

    p_firm = doc.add_paragraph(style='LOSignature')
    p_firm.paragraph_format.space_before = Pt(12)
    run = p_firm.add_run(firm_name)
    run.bold = True

    p_space = doc.add_paragraph(style='LOSignature')
    p_space.paragraph_format.space_before = Pt(36)
    p_space.add_run("____________________________")

    p_name = doc.add_paragraph(style='LOSignature')
    run = p_name.add_run(attorney_name)
    run.bold = True

    p_title = doc.add_paragraph(style='LOSignature')
    p_title.add_run(title)

    if bar_number:
        p_bar = doc.add_paragraph(style='LOSignature')
        p_bar.add_run(f"등록 정보: {bar_number}")
```

---

## Complete Assembly Example

```python
def generate_legal_opinion(content, config):
    """
    Generate a complete legal opinion letter .docx.

    Args:
        content: dict with keys matching document sections
            - confidential: bool
            - date: str
            - recipient: list[str] (name, title, company, address lines)
            - subject: str
            - salutation: str
            - introduction: str
            - executive_summary: str (optional)
            - background: str
            - issues: list[str]
            - applicable_law: str
            - analysis: list[dict] with keys 'heading', 'body' (str or list[str])
            - conclusions: list[str]
            - qualifications: str
            - recommendations: str (optional)
            - language: 'en' | 'ko' | 'bilingual'

        config: dict with firm info
            - firm_name: str
            - firm_subtitle: str (e.g., "AI Legal Workflow System")
            - address: str
            - phone: str
            - email: str
            - website: str
            - attorney_name: str
            - attorney_title: str
            - bar_number: str (optional)

    Returns:
        Document object (call doc.save('output.docx') to write)
    """
    doc = Document()
    setup_styles(doc)

    # Firm info with defaults
    firm_info = {
        'name': config.get('firm_name', 'KP Legal Orchestrator'),
        'subtitle': config.get('firm_subtitle', 'AI Legal Workflow System'),
        'address': config.get('address', '[ADDRESS]'),
        'phone': config.get('phone', '[PHONE]'),
        'email': config.get('email', '[EMAIL]'),
        'website': config.get('website', '[WEBSITE]'),
    }

    create_letterhead(doc, firm_info)
    create_footer(doc, confidential=content.get('confidential', False))

    # Confidential marking
    if content.get('confidential', False):
        if content.get('language') == 'ko':
            add_confidential_marking(doc, "비밀유지\n내부 법률 워크플로 초안")
        else:
            add_confidential_marking(doc)

    # Date & Addressee
    add_date_and_addressee(doc, content['date'], content['recipient'])

    # Reference line
    add_reference_line(doc, content['subject'])

    # Salutation
    p_sal = doc.add_paragraph(style='LOBody')
    p_sal.paragraph_format.space_before = Pt(12)
    p_sal.add_run(content['salutation'])

    # Section numbering
    section_num = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    idx = 0

    # Introduction
    add_section_heading(doc, section_num[idx], "Introduction" if content.get('language') != 'ko' else "서론")
    add_body_paragraph(doc, content['introduction'])
    idx += 1

    # Executive Summary (optional)
    if content.get('executive_summary'):
        heading = "Executive Summary" if content.get('language') != 'ko' else "요약"
        add_section_heading(doc, section_num[idx], heading)
        add_body_paragraph(doc, content['executive_summary'])
        idx += 1

    # Background / Facts
    heading = "Background" if content.get('language') != 'ko' else "사실관계"
    add_section_heading(doc, section_num[idx], heading)
    add_body_paragraph(doc, content['background'])
    idx += 1

    # Issues Presented
    heading = "Issues Presented" if content.get('language') != 'ko' else "쟁점"
    add_section_heading(doc, section_num[idx], heading)
    preamble = ("The specific legal issues addressed in this opinion are:"
                if content.get('language') != 'ko'
                else "본 의견서에서 검토한 법적 쟁점은 다음과 같습니다:")
    add_body_paragraph(doc, preamble)
    for i, issue in enumerate(content['issues'], 1):
        p = doc.add_paragraph(style='LOBody')
        p.paragraph_format.left_indent = Inches(0.5)
        run_num = p.add_run(f"{i}.\t")
        run_num.bold = True
        p.add_run(issue)
    idx += 1

    # Applicable Law
    if content.get('applicable_law'):
        heading = "Applicable Law" if content.get('language') != 'ko' else "관련 법령"
        add_section_heading(doc, section_num[idx], heading)
        if isinstance(content['applicable_law'], list):
            for para in content['applicable_law']:
                add_body_paragraph(doc, para)
        else:
            add_body_paragraph(doc, content['applicable_law'])
        idx += 1

    # Analysis / Discussion
    heading = "Analysis" if content.get('language') != 'ko' else "분석"
    add_section_heading(doc, section_num[idx], heading)
    labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i, item in enumerate(content['analysis']):
        add_sub_heading(doc, labels[i], item['heading'])
        if isinstance(item['body'], list):
            for para in item['body']:
                add_body_paragraph(doc, para, first_line_indent=True)
        else:
            add_body_paragraph(doc, item['body'], first_line_indent=True)
    idx += 1

    # Conclusions
    heading = "Conclusions" if content.get('language') != 'ko' else "결론"
    add_section_heading(doc, section_num[idx], heading)
    preamble = ("Based on the foregoing analysis, it is our opinion that:"
                if content.get('language') != 'ko'
                else "이상의 분석을 바탕으로, 다음과 같이 의견을 드립니다:")
    add_body_paragraph(doc, preamble)
    for i, conclusion in enumerate(content['conclusions'], 1):
        p = doc.add_paragraph(style='LOBody')
        p.paragraph_format.left_indent = Inches(0.5)
        run_num = p.add_run(f"{i}.\t")
        run_num.bold = True
        p.add_run(conclusion)
    idx += 1

    # Qualifications & Limitations
    if content.get('qualifications'):
        heading = ("Qualifications and Limitations"
                   if content.get('language') != 'ko' else "의견의 한계")
        add_section_heading(doc, section_num[idx], heading)
        add_body_paragraph(doc, content['qualifications'])
        idx += 1

    # Recommendations (optional)
    if content.get('recommendations'):
        heading = "Recommendations" if content.get('language') != 'ko' else "권고사항"
        add_section_heading(doc, section_num[idx], heading)
        add_body_paragraph(doc, content['recommendations'])
        idx += 1

    # Signature block
    if content.get('language') == 'ko':
        add_signature_block_ko(
            doc,
            config.get('firm_name', 'KP Legal Orchestrator'),
            config.get('attorney_name', '[스페셜리스트 이름]'),
            config.get('attorney_title', '[직위]'),
            config.get('bar_number'),
        )
    else:
        add_signature_block(
            doc,
            config.get('firm_name', 'KP Legal Orchestrator'),
            config.get('attorney_name', '[SPECIALIST NAME]'),
            config.get('attorney_title', '[TITLE]'),
            config.get('bar_number'),
        )

    # Disclaimer
    if content.get('disclaimer'):
        p = doc.add_paragraph(style='LODisclaimer')
        p.add_run(content['disclaimer'])

    return doc
```

---

## Usage Patterns

### Pattern 1: Agent provides structured content

The agent parses its generated legal opinion into the `content` dict structure and
passes it to `generate_legal_opinion()`. This is the ideal pattern.

### Pattern 2: Agent provides raw text

If the agent generates a legal opinion as unstructured text, parse it into sections
first. Look for these markers:
- Headings (numbered sections, Roman numerals)
- "Background", "Issue", "Analysis", "Conclusion" keywords
- Paragraph breaks

### Pattern 3: User provides existing text

Read the user's text from a file or input, then apply the formatting. The agent
should identify the document structure and map it to the content dict.

---

## Quality Checklist

Before saving the final .docx, verify:

- [ ] **Letterhead**: Firm name, contact info properly placed in header
- [ ] **Date format**: Correct for the document language
- [ ] **Recipient block**: Complete with name, title, organization
- [ ] **Reference line**: Clear subject matter description
- [ ] **Section numbering**: Consistent Roman numerals throughout
- [ ] **Sub-headings**: Consistent letter labels (A, B, C)
- [ ] **Font consistency**: Serif for body, sans-serif for letterhead only
- [ ] **Spacing**: 1.15 line spacing, 6pt paragraph spacing
- [ ] **Page numbers**: Present in footer
- [ ] **Signature block**: Complete with all fields
- [ ] **Confidential marking**: Present if applicable
- [ ] **No orphan headings**: `keep_with_next` set on all heading styles
- [ ] **Korean font fallback**: 맑은 고딕 set for East Asian text
- [ ] **Placeholders**: All organization-specific placeholders clearly marked with `[BRACKETS]`

---

## Adaptation Guide

### For Different Opinion Types

The base structure works for most legal opinions. Adapt by:

**Transaction opinions** (e.g., M&A, financing):
- Add "Assumptions" section after Background
- Add "Documents Reviewed" list
- Conclusions use "it is our opinion that..." formulation

**Regulatory opinions** (e.g., compliance, licensing):
- Expand "Applicable Law" section
- Add "Regulatory Framework" sub-section
- Include specific regulatory citations in block quotes

**IP opinions** (e.g., patentability, infringement, freedom-to-operate):
- Add "Claim Analysis" section
- Include claim charts as tables
- Use "Prior Art" section instead of "Background"

**Litigation risk assessment**:
- Replace "Conclusions" with "Risk Assessment"
- Add risk-level indicators (High/Medium/Low)
- Include "Litigation Strategy" recommendations

**Korean 법률의견서**:
- Use Korean section headings throughout
- Follow Korean legal citation format
- Include 강행규정 (mandatory law) references where applicable
- Use formal Korean register (합니다체)
