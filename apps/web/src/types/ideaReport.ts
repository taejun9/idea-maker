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

export interface IdeaReportResponse {
  overview: string;
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
}
