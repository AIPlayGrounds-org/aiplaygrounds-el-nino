import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { afterEach, describe, expect, it, vi } from "vitest";
import ChartShell from "~/components/ChartShell.vue";
import { messages } from "~/messages";
import { geometryFixture } from "./fixtures/geometry";
import { gridFixture } from "./fixtures/grid";
import { timeSeriesFixture } from "./fixtures/time-series";

describe("ChartShell", () => {
  afterEach(() => vi.useRealTimers());

  it.each([
    ["time series", timeSeriesFixture],
    ["grid", gridFixture],
    ["geometry", geometryFixture],
  ])("renders provenance for a %s fixture", async (_kind, dataset) => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-10-03T00:00:00Z"));
    const wrapper = mount(ChartShell, {
      props: { dataset, summary: "Resumen accesible de prueba" },
      slots: { default: "<div data-chart>chart</div>" },
    });
    await nextTick();

    expect(wrapper.find("[data-chart]").exists()).toBe(true);
    expect(wrapper.text()).toContain(dataset.variable);
    expect(wrapper.text()).toContain(dataset.unit);
    expect(wrapper.text()).toContain(dataset.temporal_resolution);
    expect(wrapper.text()).toContain(messages.dataType[dataset.data_type]);
    expect(wrapper.text()).toContain(dataset.source.institution);
    const first = dataset.records[0]!;
    const last = dataset.records.at(-1)!;
    const coverage = first.start === last.end ? first.start : `${first.start}–${last.end}`;
    expect(wrapper.text()).toContain(coverage);
    expect(wrapper.text()).toContain("hace 2 días");
    expect(wrapper.text()).toContain("Resumen accesible de prueba");
  });

  it.each([
    ["update", 40],
    ["update", 41],
    ["record", 90],
    ["record", 91],
  ])("shows the stale notice at and past the %s threshold", async (kind, days) => {
    vi.useFakeTimers();
    const now = new Date("2026-10-03T00:00:00Z");
    vi.setSystemTime(now);
    const dataset = JSON.parse(JSON.stringify(timeSeriesFixture)) as typeof timeSeriesFixture;
    const date = new Date(now.getTime() - days * 86_400_000).toISOString().slice(0, 10);
    if (kind === "update") dataset.ingestion_time = `${date}T00:00:00Z`;
    else dataset.records.at(-1)!.end = date;

    const wrapper = mount(ChartShell, {
      props: { dataset, summary: "Resumen accesible de prueba" },
      slots: { default: "<div data-chart>chart</div>" },
    });
    await nextTick();

    expect(wrapper.get(".stale-notice").text()).toContain(messages.provenance.staleSource);
  });
});
