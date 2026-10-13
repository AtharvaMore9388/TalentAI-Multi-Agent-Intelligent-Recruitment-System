"""
TalentAI — Test Suite

Tests for tools and core library components.
Run with: pytest tests/ -v
"""
import pytest
import sys
import os

# Ensure backend is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ─── Tool Tests ──────────────────────────────────────────────────────────────

class TestScoringTool:
    def setup_method(self):
        from tools.scoring_tool import ScoringTool
        self.tool = ScoringTool()

    def test_perfect_match(self):
        result = self.tool._run(
            candidate_skills="python, pytorch, fastapi, docker, nlp",
            candidate_experience_years=5.0,
            mandatory_requirements="python, pytorch, fastapi",
            preferred_requirements="docker, nlp",
        )
        assert "SCORE:" in result
        assert "PASS_MANDATORY: YES" in result

    def test_missing_mandatory(self):
        result = self.tool._run(
            candidate_skills="python, flask",
            candidate_experience_years=2.0,
            mandatory_requirements="pytorch, kubernetes, docker",
            preferred_requirements="nlp",
        )
        assert "PASS_MANDATORY: NO" in result
        assert "Missing mandatory:" in result

    def test_score_range(self):
        result = self.tool._run(
            candidate_skills="python",
            candidate_experience_years=3.0,
            mandatory_requirements="python",
            preferred_requirements="",
        )
        # Extract score
        import re
        m = re.search(r"SCORE:\s*([\d.]+)", result)
        assert m is not None
        score = float(m.group(1))
        assert 0.0 <= score <= 100.0

    def test_zero_experience(self):
        result = self.tool._run(
            candidate_skills="react, node",
            candidate_experience_years=0.0,
            mandatory_requirements="react",
            preferred_requirements="node",
        )
        assert "SCORE:" in result

    def test_empty_requirements(self):
        result = self.tool._run(
            candidate_skills="python",
            candidate_experience_years=2.0,
            mandatory_requirements="",
            preferred_requirements="",
        )
        assert "SCORE:" in result


# ─── Model Tests ─────────────────────────────────────────────────────────────

class TestModels:
    def test_candidate_model(self):
        from lib.models import Candidate
        c = Candidate(
            id="test-001",
            name="Test User",
            email="test@example.com",
            skills=["Python", "FastAPI"],
            experience_years=3.0,
            education="B.Tech CSE",
            summary="A test candidate",
        )
        assert c.name == "Test User"
        assert len(c.skills) == 2
        assert c.experience_years == 3.0

    def test_job_description_model(self):
        from lib.models import JobDescription
        jd = JobDescription(
            id="jd-001",
            title="ML Engineer",
            company="TestCo",
            mandatory_requirements=["Python", "PyTorch"],
            preferred_requirements=["Docker"],
            description="A test job",
        )
        assert jd.title == "ML Engineer"
        assert len(jd.mandatory_requirements) == 2

    def test_agent_message_model(self):
        from lib.models import AgentMessage
        msg = AgentMessage(
            agent="TestAgent",
            role="action",
            content="Test message",
        )
        assert msg.agent == "TestAgent"
        assert msg.role == "action"

    def test_recruitment_state_defaults(self):
        from lib.models import RecruitmentState
        state = RecruitmentState()
        assert state.status == "pending"
        assert state.replan_count == 0
        assert state.relaxed_requirements is False
        assert state.candidates == []


# ─── Data Loader Tests ───────────────────────────────────────────────────────

class TestDataLoader:
    def test_samples_load(self):
        import data_loader
        samples = data_loader.get_samples()
        assert "jobs" in samples
        assert "resumes" in samples
        assert len(samples["jobs"]) > 0
        assert len(samples["resumes"]) > 0

    def test_demo_trace_load(self):
        import data_loader
        trace = data_loader.get_demo_trace()
        assert isinstance(trace, list)
        assert len(trace) > 0
        agents_seen = {msg["agent"] for msg in trace}
        # Verify all 5 core agents appear
        assert "Orchestrator" in agents_seen
        assert "JobAnalysisAgent" in agents_seen
        assert "ResumeAnalysisAgent" in agents_seen
        assert "MatchingAgent" in agents_seen
        assert "EvaluationAgent" in agents_seen
        assert "CommunicationAgent" in agents_seen

    def test_demo_trace_has_conflict(self):
        import data_loader
        trace = data_loader.get_demo_trace()
        roles = [msg["role"] for msg in trace]
        assert "conflict" in roles  # EvaluationAgent rejection
        assert "replan" in roles    # Orchestrator replanning


# ─── ChromaDB Store Tests ────────────────────────────────────────────────────

class TestChromaStore:
    def setup_method(self):
        # Use temp directory for tests
        import tempfile
        self.tmpdir = tempfile.mkdtemp()
        from lib.chroma_store import ChromaStore
        self.store = ChromaStore(persist_dir=self.tmpdir)

    def test_add_and_count(self):
        from lib.models import Candidate
        c = Candidate(
            id="test-001",
            name="Alice Test",
            email="alice@test.com",
            skills=["Python", "FastAPI"],
            experience_years=3.0,
            education="B.Tech",
            summary="Python developer",
        )
        self.store.add_resume(c)
        assert self.store.count() == 1

    def test_semantic_search(self):
        from lib.models import Candidate
        c1 = Candidate(
            id="test-001",
            name="Python Dev",
            email="dev1@test.com",
            skills=["Python", "Machine Learning"],
            experience_years=4.0,
            education="M.Tech AI",
            summary="ML engineer specializing in Python",
        )
        c2 = Candidate(
            id="test-002",
            name="Frontend Dev",
            email="dev2@test.com",
            skills=["React", "JavaScript", "CSS"],
            experience_years=3.0,
            education="B.Tech IT",
            summary="Frontend web developer",
        )
        self.store.add_resumes_batch([c1, c2])
        results = self.store.semantic_search("machine learning python AI", n_results=2)
        assert len(results) >= 1
        # The Python/ML candidate should rank higher for ML query
        if len(results) >= 2:
            assert results[0]["similarity"] >= results[1]["similarity"]

    def test_clear(self):
        from lib.models import Candidate
        c = Candidate(
            id="test-001", name="Test", email="t@t.com",
            skills=["Python"], experience_years=1.0,
            education="B.Sc", summary="test"
        )
        self.store.add_resume(c)
        self.store.clear()
        assert self.store.count() == 0
