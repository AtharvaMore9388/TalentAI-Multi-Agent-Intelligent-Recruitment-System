// TalentAI — Shared TypeScript types

export interface AgentMessage {
  agent: string
  role: 'action' | 'decision' | 'conflict' | 'replan' | 'result'
  content: string
  timestamp?: string
}

export interface Candidate {
  id: string
  name: string
  email: string
  phone?: string
  skills: string[]
  experience_years: number
  education: string
  summary: string
  raw_resume: string
}

export interface JobDescription {
  id: string
  title: string
  company: string
  mandatory_requirements: string[]
  preferred_requirements: string[]
  description: string
  raw_jd: string
}

export interface MatchedCandidate {
  candidate: Candidate
  match_score: number
  matched_mandatory: string[]
  matched_preferred: string[]
  missing_mandatory: string[]
  missing_preferred: string[]
  evaluation_notes: string
}

export interface RecruitmentState {
  job?: JobDescription
  candidates: Candidate[]
  shortlisted: MatchedCandidate[]
  evaluation_passed: boolean
  replan_count: number
  relaxed_requirements: boolean
  messages: AgentMessage[]
  final_communications: string[]
  status: 'pending' | 'running' | 'completed' | 'failed'
}

export interface SampleJob {
  id: string
  title: string
  company: string
  raw_jd: string
}

export interface SampleResume {
  name: string
  email: string
  raw_resume: string
}

export interface SamplesResponse {
  jobs: SampleJob[]
  resumes: SampleResume[]
}

export type AgentName =
  | 'Orchestrator'
  | 'JobAnalysisAgent'
  | 'ResumeAnalysisAgent'
  | 'MatchingAgent'
  | 'EvaluationAgent'
  | 'CommunicationAgent'
  | 'System'

export const AGENT_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  Orchestrator: { label: 'Orchestrator', color: '#6366f1', icon: '🧠' },
  JobAnalysisAgent: { label: 'Job Analysis', color: '#06b6d4', icon: '📋' },
  ResumeAnalysisAgent: { label: 'Resume Analysis', color: '#8b5cf6', icon: '📄' },
  MatchingAgent: { label: 'Matching & Ranking', color: '#f59e0b', icon: '🔍' },
  EvaluationAgent: { label: 'Evaluation', color: '#ef4444', icon: '⚖️' },
  CommunicationAgent: { label: 'Communication', color: '#10b981', icon: '📧' },
  System: { label: 'System', color: '#94a3b8', icon: '⚙️' },
}

export const ROLE_LABELS: Record<string, string> = {
  action: 'Action',
  decision: 'Decision',
  conflict: 'Conflict',
  replan: 'Replan',
  result: 'Result',
}
