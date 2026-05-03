import { mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../src/App.vue";

const sampleReport = {
  overview: "'동네 소상공인을 위한 AI 리뷰 분석 도구' 아이디어를 초기 검증 가능한 제품 개념으로 구체화합니다.",
  target_users: ["초기 창업자", "소규모 제품팀"],
  strengths: ["짧은 입력으로 구조화된 보고서를 생성"],
  weaknesses: ["초기 버전은 외부 소스 실시간 수집이 제한적"],
  domestic_competitors: [
    {
      name: "[TODO 국내 경쟁사]",
      market: "domestic_kr",
      summary: "국내 경쟁사는 실제 source collector 도입 후 채운다.",
      strengths: ["현지 시장 이해"],
      weaknesses: ["현재는 placeholder"],
      source_url: null,
      observed_date: "2026-05-03",
      confidence: "low",
    },
  ],
  overseas_competitors: [
    {
      name: "[TODO overseas competitor]",
      market: "overseas",
      summary: "해외 경쟁사는 Product Hunt, PitchWall, BetaList 등으로 보강한다.",
      strengths: ["글로벌 reference 확보"],
      weaknesses: ["현재는 placeholder"],
      source_url: null,
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
    expect(wrapper.find('[data-testid="report-summary"]').text()).toContain("Product Hunt");
  });
});
