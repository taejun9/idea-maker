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

export interface IdeaReportResponse {
  overview: string;
  target_users: string[];
  strengths: string[];
  weaknesses: string[];
  domestic_competitors: Competitor[];
  overseas_competitors: Competitor[];
  source_references: SourceReference[];
  next_validation_steps: string[];
}
