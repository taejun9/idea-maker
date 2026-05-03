export type SourceConfidence = "low" | "medium" | "high";

export interface Competitor {
  name: string;
  market: "domestic_kr" | "overseas";
  summary: string;
  strengths: string[];
  weaknesses: string[];
  source_url: string | null;
  observed_date: string;
  confidence: SourceConfidence;
}

export interface SourceReference {
  source_name: string;
  source_url: string;
  observed_date: string;
  note: string;
  confidence: SourceConfidence;
}

export interface IdeaReportRequest {
  idea: string;
  locale?: string;
  research?: boolean;
}

export interface IdeaRecommendationRequest {
  keyword: string;
  locale?: string;
}

export interface IdeaRecommendation {
  title: string;
  summary: string;
  rationale: string;
  report_seed: string;
}

export interface IdeaRecommendationResponse {
  keyword: string;
  recommendations: IdeaRecommendation[];
}

export interface ResearchStatus {
  requested: boolean;
  search_provider: "gemini_cli" | "fallback" | "not_requested";
  search_status: "success" | "fallback" | "skipped";
  organization_provider: "gemma4" | "fallback" | "not_requested";
  organization_status: "success" | "fallback" | "skipped";
  notes: string[];
}

export interface IdeaIntakeQuestion {
  code: "Q1" | "Q2" | "Q3" | "Q4" | "Q5";
  prompt: string;
  requirement: string;
  photo_guidance: string | null;
  options: string[];
}

export interface IdeaReportResponse {
  id: string;
  idea: string;
  locale: string;
  created_at: string;
  overview: string;
  idea_intake_questions: IdeaIntakeQuestion[];
  clarified_concept: string;
  target_users: string[];
  core_use_cases: string[];
  strengths: string[];
  weaknesses: string[];
  differentiation_opportunities: string[];
  key_risks: string[];
  build_complexity: string;
  recommended_mvp_scope: string[];
  domestic_competitors: Competitor[];
  overseas_competitors: Competitor[];
  source_references: SourceReference[];
  next_validation_steps: string[];
  research_status: ResearchStatus;
}

export interface IdeaReportSummary {
  id: string;
  idea: string;
  created_at: string;
  overview: string;
  research_requested: boolean;
  domestic_competitor_count: number;
  overseas_competitor_count: number;
  source_reference_count: number;
}

export interface IdeaReportListResponse {
  reports: IdeaReportSummary[];
}
