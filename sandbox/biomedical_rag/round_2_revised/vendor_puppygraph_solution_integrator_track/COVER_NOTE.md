# PuppyGraph + Quark Labs: revised Stage 2 submission (Solution Integrator track)

| Field | Value |
| --- | --- |
| Vendor name | PuppyGraph + Quark Labs |
| Vendor track | Solution Integrator |
| Opt-in declaration | I am opting into the Solution Integrator track |
| Submission round | Round 2 (Blind), revised per the Stage 2 v1 feedback |

This revision follows the Recommended Submission Specification: one JSON file per claim under
`DRG/`, `APC/`, `SNF/` and `Readmission/`, plus `submission_manifest.json`. All 60 claims are
included (DRG 30, APC 10, SNF 10, Readmission 10), each with its full run record under `traces/`. `review_flags.json` lists, for every claim, its
confidence and where the system would call a human reviewer, and why; it sits outside the claim
files, which follow the specification only.

## How to read each file

- `determination` is "Finding" or "No Finding" only. Where the system could not support a
  determination or a correction, it reports No Finding and sends the claim to human review with
  the reason (see `review_flags.json` and `reasoning_trace`).
- `evidence[]`: one object per quote. `quote` is copied verbatim from the cited page; `page_ref` is
  the physical PDF page. A small share of quotes sit in multi-page notes where the source data
  narrows the page to two; those read "25 or 26" with `page_confirmed: false`.
- `policy_citations[]` carry `document_version_hash` (sha256 of the policy file used).
- Beyond the specification's schema, each claim file also carries the outputs the assessment
  requires (§2.2, §3): the declaration fields (`vendor_name`, `vendor_track`, `submission_round`),
  `system_note` (every claim), `rationale_letter` (Finding claims; null on No Finding), and
  `metrics` with the claim's end-to-end processing cost and time (`total_cost_per_claim_usd` adds
  the one-time data build, apportioned per claim).
- `docs/` holds the security and PHI handling and the integration API surface documents (§2.2),
  unchanged since Sept 22.
- `reasoning_trace[]` lists the actual retrieval and model calls made, in order. The full record of
  each claim's run is in `traces/<review type>/<claim_id>.trace.json`: every model and tool call
  verbatim, with the queries run, the rows they returned, the judge's input and output, the
  citation checks, token counts and timings. Patient identifiers appear there as the placeholder
  tokens the models saw. The judge is a hosted reasoning model, so its internal deliberation is not
  included; nothing is reconstructed.
- DRG: `corrected_coding_set` is the full corrected diagnosis set with POA and role;
  `corrected_procedure_set` the full procedure set; `code_actions` each change with the evidence it
  rests on, and `rationale` the reason the system gave for that change. An action with no
  evidence is reported as such, not backfilled.
- Readmission: `criteria_evaluated` is the path actually taken through the payer guideline, in
  order, stopping at the first criterion met; each evidence object carries `record_leg` (index or
  readmission).
- SNF: `revenue_corrections` and `adjusted_dates_of_service` come from a day-by-day comparison of
  the billed revenue lines with each day's documented level of care; each correction's
  `rationale` states that comparison.

## Assumptions we made where the data was ambiguous

1. **Add-on sections copied across DRG records** (raised by John Caito on Oct 6). In MR_02-MR_30,
   the EMS report, Hospital Problem List, Billing & Coding Summary, Physician Orders and CDI
   queries repeat MR_01's content with only the dates shifted, and often contradict the patient's
   own chart. Following your guidance that findings rest on the patient's authentic documentation,
   our coding decisions and citations do not rely on these sections.
2. **Contradictions inside a record.** Following the same guidance, where a record contradicts
   itself or the claim (for example a billing statement printed in an SNF record that the daily
   notes and the claim contradict), we rely on the patient's own clinical documentation. Where the
   documentation contradicts a billed code but the corrected code is not settled, the claim is
   flagged for review and names the conflict.
3. **SNF documented level per day.** Where no payer-specific threshold is on file, the documented
   level for a day is the per-diem level stated in that day's skilled nursing progress note, which
   matches the day's therapy minutes. Where two revenue lines share a date range, units are
   compared by count, since the claim does not assign dates to lines.
4. **Principal diagnosis.** We change the billed principal diagnosis to a different condition only
   where the patient's own documentation independently contradicts it. Otherwise the billed
   principal is kept, the alternative the review proposed is listed as a secondary diagnosis, and
   the claim is flagged for a reviewer to confirm.
5. **Codes judged by their official meaning.** Some claims print a description that doesn't match
   the code (for example B95.62, which ICD-10-CM defines as MRSA, printed as MSSA), and some bill
   codes that aren't valid on a claim on the discharge date (category headings such as E11.6, or
   codes that don't exist, such as G41.0). We check every code against the official ICD-10-CM /
   PCS release in effect on the discharge date (FY2026, its April 1 update, or FY2027), and no code
   we propose is outside it. Where two independent reviews of the record chose the same specific
   code within the billed code's subcategory (for example K80.2 to K80.20, or B95.62 to B95.61 where
   the cultures grew MSSA), we recode it. Otherwise the billed code is kept and the claim is flagged
   for review naming it (`review_flags.json`); we don't guess the specific code.
6. **Acute pancreatitis codes.** The Acute Necrotizing Pancreatitis policy prints K85 subcodes one
   step off ICD-10-CM: K85.11 as biliary pancreatitis without necrosis, K85.12 with uninfected
   necrosis and K85.13 with infected necrosis, where ICD-10-CM has K85.10, K85.11 and K85.12 and no
   K85.13. The claims and the charts follow ICD-10-CM. Where the corrected pancreatitis code depends
   on which numbering applies, we keep the billed code and flag the claim for review. Please let us
   know whether the policy's numbering is intended.
7. **Records that share one clinical case.** MR_09, MR_17 and MR_25 carry the same clinical record
   as MR_01 (admission history and physical, microbiology, consultations and discharge summary),
   with the dates shifted. Unlike the copied add-on sections, these are each patient's whole chart,
   so each claim is reviewed against it.
8. **Human review.** As requested, the system runs without a human. `review_flags.json` reports
   each claim's confidence and, where the system would have called a reviewer, each reason.

Contact: Danfeng Xu (dan@puppygraph.com), John Caito (john@puppygraph.com).
