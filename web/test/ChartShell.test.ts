import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import ChartShell from "~/components/ChartShell.vue";
import { messages } from "~/messages";
import { geometryFixture } from "./fixtures/geometry";
import { gridFixture } from "./fixtures/grid";
import { timeSeriesFixture } from "./fixtures/time-series";

describe("ChartShell", () => {
  it.each([
    ["time series", timeSeriesFixture],
    ["grid", gridFixture],
    ["geometry", geometryFixture],
  ])("renders provenance for a %s fixture", (_kind, dataset) => {
    const wrapper = mount(ChartShell, {
      props: { dataset, summary: "Resumen accesible de prueba" },
      slots: { default: "<div data-chart>chart</div>" },
    });

    expect(wrapper.find("[data-chart]").exists()).toBe(true);
    expect(wrapper.text()).toContain(dataset.variable);
    expect(wrapper.text()).toContain(dataset.unit);
    expect(wrapper.text()).toContain(dataset.temporal_resolution);
    expect(wrapper.text()).toContain(messages.dataType[dataset.data_type]);
    expect(wrapper.text()).toContain(dataset.source.institution);
    expect(wrapper.text()).toContain("hace");
    expect(wrapper.text()).toContain("Resumen accesible de prueba");
  });
});
