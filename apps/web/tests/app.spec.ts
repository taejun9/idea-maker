import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import App from "../src/App.vue";

describe("App", () => {
  it("renders the idea report entry workflow", () => {
    const wrapper = mount(App);

    expect(wrapper.find('[data-testid="idea-input"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="generate-report"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="report-summary"]').text()).toContain("MVP");
  });
});

