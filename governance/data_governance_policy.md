# Data Governance Policy

Purpose
-------
Define roles, responsibilities, controls, and operational cadence to ensure trustworthy, compliant, and well-governed data across the platform.

Scope
-----
All datasets, metadata, pipelines, and services housed in this repository and associated infrastructure (databases, catalogs, logs). Applies to all employees, contractors and third‑party processors.

## 1. Role definitions ✅
- **Data Owner (Accountable)** — business owner for a dataset; approves access, defines retention/SLA, and owns data quality outcomes.
- **Data Steward (Responsible)** — implements policies, defines schema/DDL, operates data quality checks and lineage.
- **Data Custodian / Platform Engineer (Responsible)** — maintains storage, access controls, backups, and infrastructure-level security.
- **Data Consumer (Informed/Consulted)** — authorized user of datasets; must follow usage policies and report anomalies.
- **Privacy Officer / Compliance (Consulted)** — approves processing of personal data, handles DSARs and regulatory obligations.
- **Security / IAM Team (Responsible)** — enforces identity controls, secrets management, and audit tooling.

## 2. Data ownership model 🧭
- Every dataset must have a named **Data Owner** and at least one **Data Steward** recorded in the data catalog.
- Ownership includes: classification (public/confidential/PII), retention policy, sensitivity label, and approved consumers.
- Changes to ownership or classification require an entry in the dataset’s catalog record and a brief review by Compliance.

## 3. Access review cadence 🔁
- **Quarterly reviews** for all privileged access (DBAs, SREs, Data Owners). Annual review for general dataset access.
- Automated access-report generation (IAM + DB role sync) — reviewers receive an access report 7 days before action due date.
- Review workflow: 1) Owner reviews list → 2) Revoke or re-authorize → 3) Apply changes via ticket/automation → 4) Evidence stored in audit log.
- Exceptions limited to documented, time-bound approvals (max 90 days) and must be captured in the audit trail.

## 4. Data quality checks ✔️
- Types of checks: schema validation, null/completeness, uniqueness, referential integrity, freshness/frequency, distributional/regression checks.
- Implement checks in CI/CD and production monitoring with thresholds and alerting (e.g., >5% nulls raises a P1 ticket).
- Hold SLA: data must meet DQ pass thresholds before downstream consumers are notified (use `status` table or pipeline gating).
- Remediation: auto-retry where safe; otherwise create incident, notify Data Owner + Steward, and tag dataset as `DQ-failed` in the catalog.

## 5. GDPR & privacy considerations (high level) ⚖️
- Record lawful basis for each processing activity in the dataset catalog (consent, contract, legal obligation, legitimate interest, etc.).
- Minimize stored personal data; prefer pseudonymization or anonymization when feasible.
- Implement DSAR handling: locate personal records, provide export, or delete within 30 days (or log legal justification for delays).
- Maintain Records of Processing Activities (RoPA) and perform DPIA for high-risk processing.
- Cross-border transfers must follow approved mechanisms (SCCs, adequacy, or explicit consent) — consult Privacy Officer.

## 6. Logging & audit design 🔍
- Log everything relevant for governance: authentication, authorization decisions, DDL changes, schema migrations, data access queries (high-risk), and admin actions.
- Centralize logs in immutable storage (SIEM / log archive) with RBAC; retain access logs for a minimum of 1 year (configurable per dataset/regulatory need).
- Include metadata in logs: timestamp, user, role, dataset, action, source IP, query-id/request-id.
- Regular audit checks: monthly automated scans for abnormal access patterns; quarterly manual audit by Compliance.
- Ensure logs used for DSARs and forensic investigations are searchable and exportable with proven integrity (hash or WORM storage).

## 7. Implementation checklist & owners 🔧
- [ ] Add/validate `owner` + `steward` metadata in catalog — Owner (business). 
- [ ] Configure access review automation and quarterly calendar — IAM/Security.
- [ ] Implement DQ checks and pipeline gates — Data Steward / Platform.
- [ ] Configure centralized logging, retention and alerting — Platform / Security.
- [ ] Publish policy, schedule training and first access review — Privacy & Data Governance Lead.

## 8. Metrics & SLAs 📊
- Data freshness SLA (example): Bronze < 15 min, Silver < 1 hour, Gold < 24 hours.
- Data quality SLA: 99.5% schema/pass rate for critical datasets; DQ incidents resolved within 72 hours.
- Access-review SLA: owner response within 7 days of review notification.

## 9. Exceptions & escalation
- All policy exceptions must be submitted as a documented request, approved by the Data Owner and Compliance, and logged with an expiration.
- Unresolved or recurring policy violations escalate to Data Governance Council.

---
Notes
- This policy is operational — consult Legal/Privacy for regulation-specific or legal interpretations. Update the document annually or when significant regulatory changes occur.

File: `governance/data_governance_policy.md`
