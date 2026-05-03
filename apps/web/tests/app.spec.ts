import { mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../src/App.vue";

const expectedApiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000").replace(
  /\/$/,
  "",
);

function apiUrl(path: string) {
  return `${expectedApiBaseUrl}${path}`;
}

const sampleReport = {
  overview: "'동네 소상공인을 위한 AI 리뷰 분석 도구' 아이디어를 초기 검증 가능한 제품 개념으로 구체화합니다.",
  clarified_concept:
    "동네 소상공인을 위한 AI 리뷰 분석 도구를 반복 업무를 줄이는 SaaS로 정의합니다.",
  target_users: ["초기 창업자", "소규모 제품팀"],
  core_use_cases: ["짧은 아이디어를 검증 가능한 제품 콘셉트로 정리한다."],
  strengths: ["짧은 입력으로 구조화된 보고서를 생성"],
  weaknesses: ["초기 버전은 외부 소스 실시간 수집이 제한적"],
  differentiation_opportunities: ["국내 사용자 업무 맥락을 우선 반영한다."],
  key_risks: ["fixture-backed 소스는 현재 시장 사실로 주장할 수 없다."],
  build_complexity: "중간: 최신 소스 검증과 신뢰도 관리가 필요합니다.",
  recommended_mvp_scope: ["아이디어 입력과 구체화된 콘셉트 생성"],
  domestic_competitors: [
    {
      name: "국내 리뷰 분석 SaaS 후보군",
      market: "domestic_kr",
      summary: "fixture-backed collector record입니다.",
      strengths: ["현지 시장 이해"],
      weaknesses: ["실제 경쟁사 사실은 다음 collector 단계에서 검증 필요"],
      source_url: "https://www.google.com/search?q=review",
      observed_date: "2026-05-03",
      confidence: "low",
    },
  ],
  overseas_competitors: [
    {
      name: "Product Hunt review-insights reference",
      market: "overseas",
      summary: "해외 경쟁사는 Product Hunt, PitchWall, BetaList 등으로 보강한다.",
      strengths: ["글로벌 reference 확보"],
      weaknesses: ["현재 launch 사실은 live collector 또는 browsing으로 확인 필요"],
      source_url: "https://www.producthunt.com/",
      observed_date: "2026-05-03",
      confidence: "low",
    },
  ],
  source_references: [
    {
      source_name: "Product Hunt",
      source_url: "https://www.producthunt.com/",
      observed_date: "2026-05-03",
      note: "Current facts require browsing or an approved collector before use.",
      confidence: "low",
    },
  ],
  next_validation_steps: ["핵심 사용자 5명을 인터뷰한다."],
  research_status: {
    requested: false,
    search_provider: "not_requested",
    search_status: "skipped",
    organization_provider: "not_requested",
    organization_status: "skipped",
    notes: [],
  },
};

const sampleResearchedReport = {
  ...sampleReport,
  research_status: {
    requested: true,
    search_provider: "fallback",
    search_status: "fallback",
    organization_provider: "fallback",
    organization_status: "fallback",
    notes: ["Using deterministic source collectors instead of Gemini CLI search."],
  },
};

const sampleRecommendations = {
  keyword: "리뷰",
  recommendations: [
    {
      title: "리뷰 고객 반응 분석 도구",
      summary: "리뷰 관련 리뷰, 문의, 피드백을 모아 반복 이슈를 보여주는 운영 도구",
      rationale: "고객 목소리를 구조화하면 초기 MVP 문제 정의와 경쟁 분석이 쉬워집니다.",
      report_seed: "리뷰 관련 고객 리뷰와 문의를 자동으로 분석해 개선 우선순위를 제안하는 SaaS",
    },
    {
      title: "리뷰 업무 자동화 체크리스트",
      summary: "리뷰 업무를 단계별 체크리스트와 자동 알림으로 관리하는 팀 생산성 도구",
      rationale: "한 단어 아이디어를 반복 업무 절감이라는 명확한 가치로 확장합니다.",
      report_seed: "리뷰 업무를 체크리스트와 자동 알림으로 표준화하는 팀 생산성 서비스",
    },
  ],
};

const longerIdea =
  "지역 기반 소상공인 리뷰와 고객 문의를 분석하고 매장 운영 개선 과제를 자동으로 정리하는 B2B SaaS 플랫폼";

describe("App", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the idea report entry workflow", () => {
    const wrapper = mount(App);
    const ideaInput = wrapper.find('[data-testid="idea-input"]');
    const submitButton = wrapper.find('[data-testid="generate-report"]');

    expect(ideaInput.exists()).toBe(true);
    expect((ideaInput.element as HTMLTextAreaElement).value).toBe("");
    expect(ideaInput.attributes("aria-describedby")).toContain("idea-help");
    expect(ideaInput.attributes("aria-invalid")).toBe("false");
    expect(wrapper.findAll('[data-testid="idea-example"]')).toHaveLength(3);
    expect(wrapper.find('[data-testid="idea-count"]').text()).toContain("0 / 2000자");
    expect(submitButton.exists()).toBe(true);
    expect(submitButton.attributes("disabled")).toBeDefined();
    expect(wrapper.find('[data-testid="report-empty"]').text()).toContain("생성된 보고서");
  });

  it("fills the idea input from a quick example", async () => {
    const wrapper = mount(App);
    const ideaInput = wrapper.find('[data-testid="idea-input"]');

    await wrapper.findAll('[data-testid="idea-example"]')[0].trigger("click");

    expect((ideaInput.element as HTMLTextAreaElement).value).toBe(
      "동네 소상공인을 위한 AI 리뷰 분석 도구",
    );
    expect(wrapper.find('[data-testid="idea-count"]').text()).toContain("관련 아이템");
    expect(wrapper.find('[data-testid="generate-report"]').attributes("disabled")).toBeUndefined();
  });

  it("announces an accessible validation error for empty ideas", async () => {
    const wrapper = mount(App);

    await wrapper.find("form").trigger("submit");

    expect(wrapper.find("#idea-error").attributes("role")).toBe("alert");
    expect(wrapper.find('[data-testid="idea-input"]').attributes("aria-invalid")).toBe("true");
    expect(wrapper.find("#idea-error").text()).toContain("아이디어를");
  });

  it("recommends related items before reporting for single-word input", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(sampleRecommendations),
    });
    vi.stubGlobal("fetch", fetchMock);
    const wrapper = mount(App);

    await wrapper.find('[data-testid="idea-input"]').setValue("리뷰");
    await wrapper.find("form").trigger("submit");
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="recommendation-list"]').exists()).toBe(true);
    });

    expect(fetchMock).toHaveBeenCalledWith(
      apiUrl("/api/idea-recommendations"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          keyword: "리뷰",
          locale: "ko-KR",
        }),
      }),
    );
    expect(wrapper.find('[data-testid="recommendation-list"]').text()).toContain(
      "리뷰 고객 반응 분석 도구",
    );
    expect(wrapper.find('[data-testid="report-summary"]').exists()).toBe(false);
  });

  it("recommends related items before reporting for short sentence input", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ ...sampleRecommendations, keyword: "리뷰 분석" }),
    });
    vi.stubGlobal("fetch", fetchMock);
    const wrapper = mount(App);

    await wrapper.find('[data-testid="idea-input"]').setValue("리뷰 분석");
    await wrapper.find("form").trigger("submit");
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="recommendation-list"]').exists()).toBe(true);
    });

    expect(fetchMock).toHaveBeenCalledWith(
      apiUrl("/api/idea-recommendations"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          keyword: "리뷰 분석",
          locale: "ko-KR",
        }),
      }),
    );
  });

  it("creates a researched report from the selected recommendation", async () => {
    const fetchMock = vi.fn((input: string | URL | Request) => {
      const url = String(input);
      if (url.endsWith("/api/idea-recommendations")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(sampleRecommendations),
        });
      }

      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(sampleResearchedReport),
      });
    });
    vi.stubGlobal("fetch", fetchMock);
    const wrapper = mount(App);

    await wrapper.find('[data-testid="idea-input"]').setValue("리뷰");
    await wrapper.find("form").trigger("submit");
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="recommendation-list"]').exists()).toBe(true);
    });
    await wrapper.findAll('[data-testid="recommendation-report"]')[0].trigger("click");
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="report-summary"]').exists()).toBe(true);
    });

    expect(fetchMock).toHaveBeenLastCalledWith(
      apiUrl("/api/idea-reports"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          idea: "리뷰 관련 고객 리뷰와 문의를 자동으로 분석해 개선 우선순위를 제안하는 SaaS",
          locale: "ko-KR",
          research: true,
        }),
      }),
    );
    expect(wrapper.find('[data-testid="report-summary"]').text()).toContain("국내 경쟁 서비스");
    expect(wrapper.find('[data-testid="research-status"]').text()).toContain("fallback");
  });

  it("submits a longer idea directly and renders the structured report", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(sampleReport),
    });
    vi.stubGlobal("fetch", fetchMock);
    const wrapper = mount(App);

    await wrapper
      .find('[data-testid="idea-input"]')
      .setValue(longerIdea);
    await wrapper.find("form").trigger("submit");
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="report-summary"]').exists()).toBe(true);
    });

    expect(fetchMock).toHaveBeenCalledWith(
      apiUrl("/api/idea-reports"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          idea: longerIdea,
          locale: "ko-KR",
          research: false,
        }),
      }),
    );
    expect(wrapper.find('[data-testid="report-summary"]').text()).toContain("국내 경쟁 서비스");
    expect(wrapper.find('[data-testid="clarified-concept"]').text()).toContain("SaaS");
    expect(wrapper.find('[data-testid="core-use-cases"]').text()).toContain("제품 콘셉트");
    expect(wrapper.find('[data-testid="key-risks"]').text()).toContain("fixture-backed");
    expect(wrapper.find('[data-testid="recommended-mvp-scope"]').text()).toContain("아이디어 입력");
    expect(wrapper.find('[data-testid="report-summary"]').text()).toContain("Product Hunt");
  });
});
