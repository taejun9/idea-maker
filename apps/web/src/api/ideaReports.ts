import type {
  IdeaReportListResponse,
  IdeaRecommendationRequest,
  IdeaRecommendationResponse,
  IdeaReportRequest,
  IdeaReportResponse,
  QuickIdeaExampleResponse,
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

export async function listIdeaReports(): Promise<IdeaReportListResponse> {
  const response = await fetch(`${API_BASE_URL}/api/idea-reports`);

  if (!response.ok) {
    throw new Error(`보고서 목록 조회 실패: HTTP ${response.status}`);
  }

  return (await response.json()) as IdeaReportListResponse;
}

export async function getIdeaReport(reportId: string): Promise<IdeaReportResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/idea-reports/${encodeURIComponent(reportId)}`,
  );

  if (!response.ok) {
    throw new Error(`보고서 상세 조회 실패: HTTP ${response.status}`);
  }

  return (await response.json()) as IdeaReportResponse;
}

export async function deleteIdeaReport(reportId: string): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/idea-reports/${encodeURIComponent(reportId)}`,
    {
      method: "DELETE",
    },
  );

  if (!response.ok) {
    throw new Error(`보고서 삭제 실패: HTTP ${response.status}`);
  }
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

export async function listQuickIdeaExamples(): Promise<QuickIdeaExampleResponse> {
  const response = await fetch(`${API_BASE_URL}/api/quick-idea-examples`);

  if (!response.ok) {
    throw new Error(`빠른 예시 조회 실패: HTTP ${response.status}`);
  }

  return (await response.json()) as QuickIdeaExampleResponse;
}
