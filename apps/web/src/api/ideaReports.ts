import type {
  IdeaRecommendationRequest,
  IdeaRecommendationResponse,
  IdeaReportRequest,
  IdeaReportResponse,
} from "../types/ideaReport";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000").replace(
  /\/$/,
  "",
);

export async function createIdeaReport(
  payload: IdeaReportRequest,
): Promise<IdeaReportResponse> {
  const response = await fetch(`${API_BASE_URL}/api/idea-reports`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`보고서 생성 실패: HTTP ${response.status}`);
  }

  return (await response.json()) as IdeaReportResponse;
}

export async function createIdeaRecommendations(
  payload: IdeaRecommendationRequest,
): Promise<IdeaRecommendationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/idea-recommendations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`추천 아이템 생성 실패: HTTP ${response.status}`);
  }

  return (await response.json()) as IdeaRecommendationResponse;
}
