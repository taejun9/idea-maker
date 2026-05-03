import { mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../src/App.vue";

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
};

describe("App", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the idea report entry workflow", () => {
    const wrapper = mount(App);

    expect(wrapper.find('[data-testid="idea-input"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="generate-report"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="report-empty"]').text()).toContain("생성된 보고서");
  });

  it("submits an idea and renders the structured report", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(sampleReport),
    });
    vi.stubGlobal("fetch", fetchMock);
    const wrapper = mount(App);

    await wrapper
      .find('[data-testid="idea-input"]')
      .setValue("동네 소상공인을 위한 AI 리뷰 분석 도구");
    await wrapper.find("form").trigger("submit");
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="report-summary"]').exists()).toBe(true);
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/idea-reports",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          idea: "동네 소상공인을 위한 AI 리뷰 분석 도구",
          locale: "ko-KR",
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
