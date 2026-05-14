# Acme corpus — reference dataset

This directory contains **~4.7 MB of synthetic Acme material** across
24 documents. It is the reference corpus for Mission 2 (RAG service)
and the source-of-truth for the golden questions in `../quiz.json`.

All content is fictional. Any resemblance to real Acme policies,
real ASIC / AUSTRAC publications, or Tolkien's actual prose is
deliberate styling, not source material.

## What's in here

### Internal policies (~14 documents, ~2.6 MB)

| File | Purpose |
|---|---|
| `acme_lending_policy.md` | Loan product rules, clause structure, responsible-lending references |
| `acme_hardship_policy.md` | Hardship assessment, repayment-pause rules, escalation cadence |
| `acme_sla_handbook.md` | Ops SLAs, queue definitions, escalation cadence, business hours |
| `acme_product_info.md` | Loan ranges, fees, terms, comparison-rate examples |
| `acme_complaints_policy.md` | Complaint acknowledgement, AFCA referral procedure |
| `acme_aml_kyc_policy.md` | KYC standards, transaction monitoring, AUSTRAC reporting |
| `acme_privacy_policy.md` | Collection, retention, data-breach response |
| `acme_broker_accreditation.md` | Broker eligibility, NPS thresholds, conflict-of-interest |
| `acme_collections_policy.md` | Pre-default engagement, default notices, external referral |
| `acme_fraud_prevention.md` | Severity-based response, recovery, reporting |
| `acme_information_security.md` | Identity & access, crypto, incident response |
| `acme_business_continuity.md` | RTO/RPO, drill programme, crisis comms |
| `acme_vendor_management.md` | Vendor tiering, diligence, exit planning |
| `acme_marketing_terms.md` | Truth-in-advertising, comparison-rate disclosure |
| `acme_dispute_resolution.md` | Internal dispute lodgement, determinations |
| `acme_customer_communications.md` | Channel hierarchy, plain-language standards |

### Synthesised regulatory material (~2 documents, ~550 KB)

| File | Purpose |
|---|---|
| `asic_rg209_synthesis.md` | Working synthesis of ASIC RG 209's responsible-lending framework |
| `nccp_excerpt.md` | Selected sections of the NCCP Act (s.72, s.76, s.88, s.117, s.128) |

### Training material (~2 documents, ~400 KB)

| File | Purpose |
|---|---|
| `acme_training_module_credit.md` | Credit assessment training — bank-statement analysis, expense categorisation |
| `acme_training_module_ops.md` | Operations training — verification workflow, customer-channel etiquette |

### Strategic / narrative material (~5 documents, ~1.0 MB)

| File | Purpose |
|---|---|
| `acme_quarterly_strategy_q3_2025.md` | Q3 FY26 strategy memo — origination targets, channel mix |
| `acme_case_studies_collection.md` | Ten ops/credit case studies in narrative form |
| `acme_glossary_and_faq.md` | Cross-document glossary and frequently-asked questions |
| `silmaril_charter.md` | A long fictional narrative — used for paraphrase-trap and common-knowledge-contradiction questions |

## Trick-question coverage

The corpus is structured so that the four trick-question categories
described in the brief (specific figure / contradicts common knowledge
/ cross-document / near-miss paraphrase) all have natural anchor
points. Examples:

- **Specific figure** — clause 4.3(b) of the Lending Policy specifies
  the break-cost cap as 3× the most recent monthly interest charge.
- **Contradicts common knowledge** — the Silmaril Charter explicitly
  places the forging of the One Ring in Eregion in the year 1600 of
  the Second Age, contradicting the popular Mount Doom attribution.
- **Cross-document** — combining the Hardship Policy and the SLA
  Handbook to identify the day-7 escalation action.
- **Near-miss paraphrase** — the Silmaril Charter contains a verbatim
  Gandalf quote that retellings paraphrase loosely.

The golden questions in `../quiz.json` are anchored to specific
sections in these documents.

## Reproducing the corpus

The corpus is generated procedurally from a seeded Python script at
`../sample-solution/scripts/generate_corpus.py`. The generator embeds
~50 anchor facts at deterministic positions; re-running it produces
byte-identical output. To extend the corpus:

```bash
python sample-solution/scripts/generate_corpus.py
```

Adjust the `DOCS` list and the `ANCHORS` dictionary at the top of the
generator script to add new documents or new testable facts. Update
`quiz.json` whenever a new anchor fact is added that you want to
test.

## Caveats

- The corpus is markdown, not PDF. The Notion brief mentions "a
  couple of regulatory PDFs" — if you want to exercise PDF parsing
  too, render `asic_rg209_synthesis.md` and `nccp_excerpt.md` to PDF
  with `pandoc` before ingesting.
- The procedurally-generated paragraphs are realistic but not
  encyclopedic. They are designed to give the retriever enough
  surrounding context that the anchor facts are findable; they are
  not a substitute for real policy text.
- Document IDs and version numbers in the headers are fictional and
  do not correspond to any real Acme control number.
