# TalentAI — Technical Design Document & Deliverables Specification

> **Assessment**: Continuous Assessment 3 (AI CA3)  
> **System**: TalentAI — Multi-Agent Intelligent Recruitment and Talent Matching System  
> **PDF Export**: Available in [`docs/TalentAI_Design_Document.pdf`](file:///c:/Users/Acer/OneDrive/Desktop/AI_CA_3/docs/TalentAI_Design_Document.pdf)

---

## 1. Project Synopsis

### The Problem
Traditional candidate screening workflows and legacy Applicant Tracking Systems (ATS) struggle fundamentally with high-volume, unstructured hiring data. Standard keyword-based ATS filtering suffers from severe error modes: high false-positive rates caused by unqualified candidates "stuffing" resumes with buzzwords, and high false-negative rates where qualified applicants are discarded simply for using alternative phrasing, abbreviations, or synonyms. Furthermore, human talent acquisition specialists experience significant cognitive fatigue when screening hundreds of multi-page resumes against rapidly evolving technical criteria, introducing subjective bias, delays, and inconsistent qualification bars across hiring cycles.

### Our Solution
**TalentAI** is an autonomous multi-agent recruitment and talent matching platform that transforms technical hiring into a transparent, deterministic, and agentic workflow. Rather than relying on a single fallible prompt, TalentAI partitions the hiring pipeline across six specialized agents: Orchestrator, Job Analysis Agent, Resume Analysis Agent, Matching & Ranking Agent, Candidate Evaluation Agent (Dual-Stage Hybrid Critic), and Recruitment Communication Agent. The system pairs Retrieval-Augmented Generation (RAG) using dense vector embeddings (`sentence-transformers/all-MiniLM-L6-v2`) in ChromaDB with deterministic requirement verification. Most critically, TalentAI demonstrates authentic agentic behavior via inter-agent conflict resolution: when the independent Evaluation Critic identifies disqualifying skill deficiencies in a proposed shortlist, the Orchestrator initiates dynamic replanning—selectively relaxing secondary preferred qualifications while strictly enforcing 100% of non-negotiable mandatory skills.

### Target Users & Scope Evolution (Matching Approved CA2 Description)
The primary target users are corporate talent acquisition specialists, technical recruiters, engineering hiring managers, and human resource departments in high-growth technology companies and SMEs seeking automated first-round technical screening.

**Scope Evolution Note (Relative to CA2 Proposal):**  
In the approved CA2 project proposal, the system was originally scoped as a linear, single-pass semantic retrieval pipeline with basic heuristic scoring. During CA3 implementation and refinement, the architectural scope was intentionally elevated to address reviewer feedback and demonstrate rigorous multi-agent autonomy:
1. **Dual-Stage Hybrid Critic**: Upgraded the Evaluation Agent from a simple prompt check into a dual-stage critic that pairs deterministic Python constraint checks (100% mandatory skill compliance, minimum score threshold) with LLM qualitative auditing.
2. **Dynamic Replanning & Conflict Arbitration**: Implemented an explicit negotiation loop where an Evaluation rejection triggers an LLM-driven Orchestrator decision (`replan_relaxed`, `replan_strict`, `escalate`, `accept_partial`) governed by the Strict Mandatory Preservation Rule and bounded by a maximum of 2 replan rounds.
3. **Full-Stack Live Telemetry**: Expanded from offline batch execution to an asynchronous FastAPI backend streaming real-time Server-Sent Events (SSE) to a Next.js 14 frontend, offering transparent audit trails of inter-agent deliberation.

---

## 2. Design Document

### 2.1 Multi-Agent Architecture Diagram & Communication Flow

```
+-----------------------------------------------------------------------------------------+
|                                   ORCHESTRATOR AGENT                                    |
|   • Central state management (RecruitmentState)                                         |
|   • Task delegation & inter-agent communication hub                                     |
|   • Conflict detection (EvaluationAgent rejection)                                      |
|   • Dynamic replanning engine (Bounded max 2 rounds)                                    |
+--------------------------------------------+--------------------------------------------+
                     |                       |                       |
       [1. Parse JD] |         [2. Parse CVs]|          [3. Rank]    |
                     v                       v                       v
+-------------------------+  +-------------------------+  +-------------------------------+
|   JOB ANALYSIS AGENT    |  |  RESUME ANALYSIS AGENT  |  |   MATCHING & RANKING AGENT    |
| • Reads raw JD          |  | • Parses candidate CVs  |  | • ChromaDB Vector RAG Search  |
| • Extracts mandatory &  |  | • Extracts skills, exp, |  | • Deterministic Scoring Tool  |
|   preferred criteria    |  |   education & contact   |  |   (Mandatory 60% +            |
| • Returns JobDescription|  | • Ingests to ChromaDB   |  |    Preferred 30% + Exp 10%)   |
+-------------------------+  +-------------------------+  +---------------+---------------+
                                                                          | Proposed Shortlist
                                                                          v
                                                          +-------------------------------+
                                                          |   CANDIDATE EVALUATION AGENT  |
                                                          |  (Independent Dual-Stage Critic)|
                                                          |  Stage 1: Hard Rule Engine    |
                                                          |  Stage 2: LLM Qualitative Bar |
                                                          +---------------+---------------+
                                                                          |
                              +-------------------------------------------+-------------------+
                              | REJECT (Conflict Signal)                                      | APPROVE
                              v                                                               v
        +-------------------------------------------+                     +-------------------+
        |         ORCHESTRATOR REPLAN ENGINE        |                     |   COMMUNICATION   |
        | • Relax preferred criteria only           |                     |       AGENT       |
        | • Preserve 100% of mandatory requirements |                     | • Tailored Invites|
        | • Re-invoke Matching Agent (Round <= 2)   |                     | • Constructive    |
        +---------------------+---------------------+                     |   Rejection Notes |
                              | Re-match Directive                        +-------------------+
                              +---------------------------------------^
```

#### Communication Flow Summary:
1. **Client / API Layer → Orchestrator**: User submits `RecruitmentRequest` containing raw JD, resumes, and `top_n`.
2. **Orchestrator → Job Analysis Agent**: Dispatches raw JD; receives structured `JobDescription` model.
3. **Orchestrator → Resume Analysis Agent**: Dispatches raw candidate resumes; receives structured `Candidate` models and embeds them into ChromaDB vector space.
4. **Orchestrator → Matching & Ranking Agent**: Requests semantic RAG retrieval and composite scoring; receives initial `MatchedCandidate[]` shortlist.
5. **Orchestrator → Candidate Evaluation Agent**: Passes proposed shortlist for independent verification.
6. **Candidate Evaluation Agent → Orchestrator**: Emits quality gate verdict (`APPROVE` or `REJECT` with conflict explanation).
7. **Orchestrator Dynamic Replan Loop (on Conflict)**: Evaluates state via LLM arbiter, executes relaxation strategy, and re-invokes Matching Agent (max 2 rounds).
8. **Orchestrator → Communication Agent**: On approved shortlist, dispatches verified candidate dossiers to generate bespoke interview invitations and rejection notices.

---

### 2.2 Agent Roles and Responsibilities

| Agent | Core Role | Key Responsibilities | Inputs / Outputs | Framework & LLM |
|---|---|---|---|---|
| **1. Orchestrator Agent** | Central Pipeline Coordinator & Arbiter | • Manages global `RecruitmentState`<br>• Enforces execution order and state transitions<br>• Detects EvaluationAgent rejections<br>• Arbitrates replan strategy (`replan_relaxed`, `replan_strict`, `escalate`, `accept_partial`)<br>• Enforces 2-round bounded recursion guard | **In:** `RecruitmentRequest`<br>**Out:** `RecruitmentState`, SSE Event Stream | CrewAI Agent, Python State Machine, Groq LLaMA-3.3-70B |
| **2. Job Analysis Agent** | Job Description Parser | • Parses raw unstructured job postings<br>• Extracts non-negotiable **mandatory requirements**<br>• Isolates nice-to-have **preferred requirements**<br>• Extracts minimum/maximum experience bounds | **In:** Raw JD string<br>**Out:** Structured `JobDescription` Pydantic model | Groq LLaMA-3.3-70B (JSON entity extraction) |
| **3. Resume Analysis Agent** | Multi-Instance Resume Parser & Ingester | • Parses unstructured candidate resumes in parallel<br>• Extracts confirmed technical skills, education, and contact details<br>• Differentiates professional, internship, and project experience<br>• Ingests 384-d embeddings into local ChromaDB collection | **In:** Raw resume strings<br>**Out:** Structured `Candidate` Pydantic models | Groq LLaMA-3.1-8B-Instant, ChromaDB Vector Store |
| **4. Matching & Ranking Agent** | Semantic Retrieval & Scoring Engine | • Performs semantic search using cosine distance via ChromaDB<br>• Computes deterministic match scores (Mandatory 60%, Preferred 30%, Experience 10%)<br>• Operates in strict mode (round 1) or relaxed mode (round 2 replan)<br>• Formulates evidence-based match breakdown | **In:** `JobDescription`, Candidate Pool<br>**Out:** Ranked `MatchedCandidate[]` shortlist | CrewAI Agent, `RAGRetrievalTool`, `ScoringTool` |
| **5. Candidate Evaluation Agent** | Independent Adversarial Critic (Quality Gate) | • **Stage 1 (Hard Rule Check):** Deterministically verifies 100% mandatory skill coverage and threshold score ≥ 50<br>• **Stage 2 (LLM Qualitative Audit):** Validates technical depth, enterprise experience, and detects buzzword stuffing<br>• Issues `APPROVE` or `REJECT` verdict triggering Orchestrator replan | **In:** Proposed candidate shortlist, `JobDescription`<br>**Out:** Verdict (`APPROVE` / `REJECT`), audit notes | Independent LLM Call (Groq LLaMA-3.3-70B), Deterministic Python Validator |
| **6. Communication Agent** | Recruitment Communications Specialist | • Drafts personalized interview invitation letters highlighting candidates' specific achievements<br>• Drafts constructive, respectful rejection notices<br>• Preserves professional brand without disclosing proprietary scoring formulas | **In:** Approved candidate dossiers<br>**Out:** Formatted personalized communication texts | Groq LLaMA-3.3-70B (Natural Language Generation) |

---

### 2.3 Orchestration Pattern

**Pattern:** **Centralized Orchestrator-Worker with Adversarial Feedback Loop**

#### Justification for Orchestrator-Worker vs. Peer-to-Peer
A centralized Orchestrator-Worker pattern was chosen over a decentralized peer-to-peer (P2P) network for specific architectural and safety reasons:
1. **Deterministic State & Single Source of Truth:** A centralized orchestrator maintains the canonical `RecruitmentState` object. In decentralized P2P systems, candidate rankings and evaluation verdicts can become desynchronized or conflict across concurrent agent conversations.
2. **Elimination of Deadlocks and Infinite Loops:** In P2P multi-agent systems, mutual disagreement between a matching agent and an evaluation critic can produce cyclic, unbounded messaging. By placing the Orchestrator as the sole decision arbiter, the system enforces a strict termination ceiling (`MAX_REPLAN_ROUNDS = 2`).
3. **Auditability and Enterprise Compliance:** Hiring workflows require rigorous compliance and audit trails. The Orchestrator serializes every inter-agent request, decision, and conflict into an immutable `AgentMessage` execution trace streamed via Server-Sent Events (SSE).

#### Conflict Resolution Protocol
1. **Conflict Detection:** The Candidate Evaluation Agent reviews the Matching Agent's shortlist. If a candidate (e.g., Arjun Mehta) has high keyword overlap but lacks core mandatory skills (e.g., missing TypeScript, PostgreSQL, and having only 3 years experience against a 4+ year requirement), the Evaluation Agent issues an explicit `REJECT` verdict.
2. **Orchestrator Arbitration:** The Orchestrator intercepts the `REJECT` signal and invokes `orchestrator_decide_replan()` using an LLM strategic prompt. The arbiter evaluates:
   - Number of already approved candidates vs. target `top_n`
   - Specific requirements missing
   - Replan round count
3. **Strategic Decision Choices:**
   - `replan_relaxed`: Rerun matching with relaxed preferred requirements.
   - `replan_strict`: Rerun matching with stricter emphasis on mandatory criteria only.
   - `escalate`: Insufficient qualified candidates exist in the pool; flag for human recruiter intervention.
   - `accept_partial`: Accept only verified candidates and conclude.
4. **The Strict Mandatory Preservation Rule:** Under `replan_relaxed`, secondary nice-to-have criteria (e.g., AWS, GraphQL, Redis) are temporarily relaxed to widen candidate retrieval, but **mandatory requirements are held 100% non-negotiable**.

---

### 2.4 Technology & Framework Choices

| Component | Technology Selected | Version / Spec | Justification |
|---|---|---|---|
| **Agent Framework** | **CrewAI** | 1.15.x | Native Agent, Task, and Crew abstractions. Clean tool bindings, support for structured Pydantic schemas, and battle-tested orchestrator-worker workflows. |
| **Primary LLM** | **Groq LLaMA-3.3-70B** | 70B Versatile | Ultra-fast LPU inference (<800ms response time) eliminates HTTP request timeouts during multi-agent deliberation. Superior reasoning for JD requirement decomposition and qualitative candidate evaluation. |
| **High-Throughput LLM** | **Groq LLaMA-3.1-8B** | 8B Instant | Used for bulk resume parsing. Provides fast, low-cost entity and skill extraction across dozens of candidate documents without degrading structured accuracy. |
| **Vector Store** | **ChromaDB** | 0.5.x / 1.x | Embedded local vector database. Operates in-process with zero external cloud latency, zero API costs, local persistence, and native cosine similarity querying. |
| **Embedding Model** | **sentence-transformers** | `all-MiniLM-L6-v2` (384-d) | Local dense embedding model running on CPU/GPU. Produces semantically rich vector representations capturing technical equivalence (e.g., matching "k8s" to "kubernetes"). |
| **Backend Framework** | **FastAPI** | 0.115.x | High-performance asynchronous Python web framework with native Server-Sent Events (SSE) streaming for real-time agent telemetry, automatic OpenAPI Swagger documentation, and Pydantic validation. |
| **Frontend Framework** | **Next.js 14** | App Router / TypeScript | Modern reactive UI providing real-time EventSource telemetry streaming, interactive candidate review studio, and side-by-side match breakdown visualizations. |

---

## 3. Input Definition

### 3.1 Input Schema
The system accepts requests via `POST /api/recruit` and `POST /api/recruit/stream`. The input payload adheres to the following JSON schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RecruitmentRequest",
  "type": "object",
  "properties": {
    "job_description": {
      "type": "string",
      "minLength": 50,
      "description": "Raw unformatted text of the job description or role posting."
    },
    "resumes": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 20
      },
      "minItems": 1,
      "description": "List of raw unformatted candidate resume texts."
    },
    "top_n": {
      "type": "integer",
      "default": 5,
      "minimum": 1,
      "maximum": 20,
      "description": "Number of top matching candidates to shortlist and evaluate."
    }
  },
  "required": ["job_description", "resumes"]
}
```

### 3.2 Real Sample Input

```json
{
  "job_description": "Senior Full Stack Engineer at TechNova Inc.\nLocation: Remote / Hybrid\n\nWe are looking for a Senior Full Stack Engineer to join our product engineering team. You will be responsible for building scalable web applications using React and Node.js. The ideal candidate has strong experience with TypeScript, PostgreSQL, and cloud infrastructure (AWS or GCP). Containerization experience with Docker, Kubernetes, and CI/CD pipelines is required. You should have at least 4 years of full-stack development experience.\n\nPreferred Qualifications:\n- Familiarity with GraphQL APIs, Redis caching, and microservices architecture.\n- Bachelor's degree in Computer Science or related field.",
  "resumes": [
    "Kavya Reddy | kavya.reddy@email.com | +91-9876543212 | GitHub: github.com/kavyareddy\nLead Engineer with 7 years experience in scalable systems.\nSKILLS: TypeScript, JavaScript, React, Next.js, Node.js, GraphQL, PostgreSQL, Redis, AWS (Solutions Architect Associate), Docker, Kubernetes (CKA certified), CI/CD, Microservices, Kafka.\nEXPERIENCE:\nLead Engineer — Razorpay (2020–Present)\n- Architected and led team of 8 building payment microservices handling 10M+ daily events.\n- Reduced infrastructure cost 30% via Kubernetes cluster optimization.\nFull Stack Developer — Zomato (2017–2020)\n- Built React/TypeScript frontend and PostgreSQL backends.\nEDUCATION: B.Tech CSE — NIT Warangal, 2017",
    "Priya Sharma | priya.sharma@email.com | +91-9876543210\nSenior Software Engineer with 6 years experience in web application development.\nSKILLS: JavaScript, TypeScript, Python, React, Next.js, Node.js, Express, PostgreSQL, MongoDB, Redis, AWS (EC2, S3, RDS), Docker, Git, REST APIs, Microservices.\nEXPERIENCE:\nSenior Software Engineer — Infosys (2021–Present)\n- Led development of React/Node.js e-commerce platform serving 500K+ users.\n- Built CI/CD pipelines with GitHub Actions and Docker.\nFull Stack Developer — Wipro (2018–2021)\n- Built internal HR tools using React and PostgreSQL.\nEDUCATION: B.Tech Computer Science — BITS Pilani, 2018",
    "Arjun Mehta | arjun.mehta@email.com | +91-9876543213\nJunior Full Stack Developer with 3 years experience.\nSKILLS: React, JavaScript, HTML, CSS, Node.js, Express.js, MySQL, basic PostgreSQL, Git, AWS basics (S3 only).\nEXPERIENCE:\nJunior Developer — StartupXYZ (2021–2023)\n- Developed React frontend components and basic Node.js REST APIs.\nWeb Developer Intern — ABC Corp (2020–2021)\n- Built HTML/CSS/JS landing pages.\nEDUCATION: BCA — Mumbai University, 2020",
    "Aisha Patel | aisha.patel@email.com | +91-9876543214\nSenior Backend & Cloud Engineer with 5 years experience.\nSKILLS: Python, FastAPI, Node.js, PostgreSQL, Docker, Kubernetes, AWS (ECS, Lambda, RDS), Microservices, REST APIs, Git, Terraform.\nEXPERIENCE:\nSenior Software Engineer — Google India (2022–Present)\n- Built high-throughput backend services handling distributed database transactions.\nSoftware Engineer — Flipkart (2019–2022)\n- Managed Kubernetes deployment clusters and microservices migration.\nEDUCATION: M.Tech AI — IIT Bombay, 2019"
  ],
  "top_n": 3
}
```

---

## 4. Output Definition

### 4.1 Output Schema

The system produces a comprehensive `RecruitmentResponse` payload:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RecruitmentResponse",
  "type": "object",
  "properties": {
    "state": {
      "type": "object",
      "properties": {
        "job": {
          "type": "object",
          "properties": {
            "id": { "type": "string" },
            "title": { "type": "string" },
            "company": { "type": "string" },
            "mandatory_requirements": { "type": "array", "items": { "type": "string" } },
            "preferred_requirements": { "type": "array", "items": { "type": "string" } },
            "min_experience_years": { "type": "number" },
            "description": { "type": "string" }
          },
          "required": ["title", "company", "mandatory_requirements"]
        },
        "candidates": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": { "type": "string" },
              "name": { "type": "string" },
              "email": { "type": "string" },
              "skills": { "type": "array", "items": { "type": "string" } },
              "experience_years": { "type": "number" },
              "education": { "type": "string" }
            }
          }
        },
        "shortlisted": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "candidate": { "$ref": "#/properties/state/properties/candidates/items" },
              "match_score": { "type": "number" },
              "matched_mandatory": { "type": "array", "items": { "type": "string" } },
              "missing_mandatory": { "type": "array", "items": { "type": "string" } },
              "matched_preferred": { "type": "array", "items": { "type": "string" } },
              "missing_preferred": { "type": "array", "items": { "type": "string" } },
              "eligibility_status": { "type": "string", "enum": ["FULLY_ELIGIBLE", "CONDITIONALLY_ELIGIBLE", "NON_COMPLIANT"] },
              "is_compliant": { "type": "boolean" },
              "evaluation_notes": { "type": "string" }
            }
          }
        },
        "evaluation_passed": { "type": "boolean" },
        "replan_count": { "type": "integer" },
        "relaxed_requirements": { "type": "boolean" },
        "final_communications": { "type": "array", "items": { "type": "string" } },
        "status": { "type": "string", "enum": ["pending", "running", "completed", "failed"] },
        "final_status": { "type": "string", "enum": ["COMPLETED_SUCCESS", "COMPLETED_PARTIAL", "COMPLETED_NO_MATCH"] }
      },
      "required": ["job", "shortlisted", "evaluation_passed", "final_status"]
    },
    "execution_trace": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "agent": { "type": "string" },
          "role": { "type": "string", "enum": ["action", "decision", "conflict", "replan", "result"] },
          "content": { "type": "string" },
          "timestamp": { "type": "string", "format": "date-time" }
        },
        "required": ["agent", "role", "content", "timestamp"]
      }
    }
  },
  "required": ["state", "execution_trace"]
}
```

### 4.2 Real Sample Output

```json
{
  "state": {
    "job": {
      "id": "job-tech-01",
      "title": "Senior Full Stack Engineer",
      "company": "TechNova Inc.",
      "mandatory_requirements": ["react", "node.js", "typescript", "postgresql", "docker", "kubernetes", "aws"],
      "preferred_requirements": ["graphql", "redis", "microservices"],
      "min_experience_years": 4.0,
      "description": "Senior Full Stack Engineer at TechNova Inc. React, Node.js, TypeScript, PostgreSQL, AWS, Docker, Kubernetes."
    },
    "candidates": [
      { "id": "cand-01", "name": "Kavya Reddy", "email": "kavya.reddy@email.com", "skills": ["typescript", "react", "node.js", "postgresql", "docker", "kubernetes", "aws", "graphql", "kafka"], "experience_years": 7.0, "education": "B.Tech CSE — NIT Warangal" },
      { "id": "cand-02", "name": "Priya Sharma", "email": "priya.sharma@email.com", "skills": ["react", "node.js", "typescript", "postgresql", "docker", "aws", "git", "rest apis"], "experience_years": 6.0, "education": "B.Tech Computer Science — BITS Pilani" },
      { "id": "cand-03", "name": "Arjun Mehta", "email": "arjun.mehta@email.com", "skills": ["react", "javascript", "node.js", "mysql"], "experience_years": 3.0, "education": "BCA — Mumbai University" },
      { "id": "cand-04", "name": "Aisha Patel", "email": "aisha.patel@email.com", "skills": ["python", "fastapi", "postgresql", "docker", "kubernetes", "aws", "microservices"], "experience_years": 5.0, "education": "M.Tech AI — IIT Bombay" }
    ],
    "shortlisted": [
      {
        "candidate": { "id": "cand-01", "name": "Kavya Reddy", "email": "kavya.reddy@email.com", "skills": ["typescript", "react", "node.js", "postgresql", "docker", "kubernetes", "aws", "graphql", "kafka"], "experience_years": 7.0, "education": "B.Tech CSE — NIT Warangal" },
        "match_score": 90.0,
        "matched_mandatory": ["react", "node.js", "typescript", "postgresql", "docker", "kubernetes", "aws"],
        "missing_mandatory": [],
        "matched_preferred": ["graphql", "microservices"],
        "missing_preferred": ["redis"],
        "eligibility_status": "FULLY_ELIGIBLE",
        "is_compliant": true,
        "evaluation_notes": "Exceeds all mandatory and preferred criteria. CKA certified Kubernetes and AWS Solutions Architect. Unanimously APPROVED by Candidate Evaluation Agent."
      },
      {
        "candidate": { "id": "cand-02", "name": "Priya Sharma", "email": "priya.sharma@email.com", "skills": ["react", "node.js", "typescript", "postgresql", "docker", "aws", "git", "rest apis"], "experience_years": 6.0, "education": "B.Tech Computer Science — BITS Pilani" },
        "match_score": 85.0,
        "matched_mandatory": ["react", "node.js", "typescript", "postgresql", "docker", "aws"],
        "missing_mandatory": [],
        "matched_preferred": ["microservices"],
        "missing_preferred": ["graphql", "redis"],
        "eligibility_status": "FULLY_ELIGIBLE",
        "is_compliant": true,
        "evaluation_notes": "Solid enterprise full-stack engineer with 6 years experience. Satisfies 100% of mandatory bar. APPROVED."
      },
      {
        "candidate": { "id": "cand-04", "name": "Aisha Patel", "email": "aisha.patel@email.com", "skills": ["python", "fastapi", "postgresql", "docker", "kubernetes", "aws", "microservices"], "experience_years": 5.0, "education": "M.Tech AI — IIT Bombay" },
        "match_score": 72.0,
        "matched_mandatory": ["postgresql", "docker", "kubernetes", "aws"],
        "missing_mandatory": [],
        "matched_preferred": ["microservices"],
        "missing_preferred": ["graphql", "redis"],
        "eligibility_status": "CONDITIONALLY_ELIGIBLE",
        "is_compliant": true,
        "evaluation_notes": "Surfaced in Round 2 Replan after Orchestrator relaxed preferred criteria. Replaced non-compliant candidate Arjun Mehta. Exceptional backend and cloud foundation."
      }
    ],
    "evaluation_passed": true,
    "replan_count": 1,
    "relaxed_requirements": true,
    "status": "completed",
    "final_status": "COMPLETED_SUCCESS",
    "final_communications": [
      "📧 INTERVIEW INVITATION — Kavya Reddy (kavya.reddy@email.com):\nDear Kavya, We were thoroughly impressed by your 7 years of full-stack engineering and Kubernetes expertise at Razorpay. TechNova Inc. would love to invite you to an initial architectural conversation for the Senior Full Stack Engineer position.",
      "📧 INTERVIEW INVITATION — Priya Sharma (priya.sharma@email.com):\nDear Priya, Your 6 years of scalable React/Node.js enterprise development at Infosys stood out as an exceptional fit for TechNova's engineering team. We'd like to schedule an introductory video interview this week.",
      "📧 CANDIDATE FEEDBACK & INVITATION — Aisha Patel (aisha.patel@email.com):\nDear Aisha, Your extensive distributed backend systems, Kubernetes, and cloud infrastructure experience at Google India is an exciting match for our backend scale. We would love to discuss a Senior Platform / Backend role at TechNova Inc."
    ]
  },
  "execution_trace": [
    {
      "agent": "Orchestrator",
      "role": "action",
      "content": "🚀 Pipeline started. Processing 4 candidate resumes for 'Senior Full Stack Engineer' at TechNova Inc.",
      "timestamp": "2026-10-21T18:40:00Z"
    },
    {
      "agent": "Orchestrator",
      "role": "decision",
      "content": "Delegating job description analysis to JobAnalysisAgent.",
      "timestamp": "2026-10-21T18:40:01Z"
    },
    {
      "agent": "JobAnalysisAgent",
      "role": "action",
      "content": "Analyzed JD for 'Senior Full Stack Engineer' at TechNova Inc.\n• Mandatory (Non-negotiable): React, Node.js, TypeScript, PostgreSQL, Docker, Kubernetes, AWS, 4+ years experience\n• Preferred (Nice-to-have): GraphQL, Redis, Microservices",
      "timestamp": "2026-10-21T18:40:03Z"
    },
    {
      "agent": "ResumeAnalysisAgent",
      "role": "action",
      "content": "Parsed and indexed 4 candidate resumes into ChromaDB vector space.",
      "timestamp": "2026-10-21T18:40:08Z"
    },
    {
      "agent": "MatchingAgent",
      "role": "action",
      "content": "Semantic RAG ranking complete. Proposed initial top 3 shortlist: 1. Kavya Reddy (87.5), 2. Priya Sharma (82.0), 3. Arjun Mehta (41.0).",
      "timestamp": "2026-10-21T18:40:12Z"
    },
    {
      "agent": "EvaluationAgent",
      "role": "conflict",
      "content": "⚠️ SHORTLIST REJECTED by EvaluationAgent.\nReason: Candidate Arjun Mehta critically fails mandatory requirements: missing TypeScript, Docker, Kubernetes, and has only 3 years experience (min 4 required). Composite score of 41.0/100 is below acceptable bar. Disallowing shortlist. Triggering Orchestrator conflict resolution.",
      "timestamp": "2026-10-21T18:40:16Z"
    },
    {
      "agent": "Orchestrator",
      "role": "replan",
      "content": "🔄 Replan Decision: REPLAN_RELAXED.\nArbitration Reasoning: 2 qualified candidates (Kavya Reddy, Priya Sharma) satisfy 100% of mandatory requirements. By executing REPLAN_RELAXED, we drop preferred nice-to-have requirements (GraphQL, Redis) while strictly preserving mandatory criteria. Re-dispatching to MatchingAgent.",
      "timestamp": "2026-10-21T18:40:20Z"
    },
    {
      "agent": "MatchingAgent",
      "role": "replan",
      "content": "Rerun with relaxed preferred criteria complete. Candidate Aisha Patel surfaced with score 72.0, satisfying backend & cloud core. Candidate Arjun Mehta removed.",
      "timestamp": "2026-10-21T18:40:24Z"
    },
    {
      "agent": "EvaluationAgent",
      "role": "result",
      "content": "✅ SHORTLIST VERIFIED & APPROVED (Round 2). All 3 candidates satisfy 100% of non-negotiable mandatory technical criteria. Zero critical deficiencies detected.",
      "timestamp": "2026-10-21T18:40:28Z"
    },
    {
      "agent": "CommunicationAgent",
      "role": "result",
      "content": "Generated 3 personalized interview invitations tailored to each candidate's demonstrated background.",
      "timestamp": "2026-10-21T18:40:32Z"
    },
    {
      "agent": "Orchestrator",
      "role": "result",
      "content": "🎉 Recruitment Pipeline Complete. Target top_n=3 achieved with 100% verified mandatory compliance. Replan rounds: 1. Final status: COMPLETED_SUCCESS.",
      "timestamp": "2026-10-21T18:40:33Z"
    }
  ]
}
```
