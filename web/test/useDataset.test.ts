import { describe, expect, it } from "vitest";
import { useDataset, validateDataset } from "~/composables/useDataset";
import type { DatasetId } from "~/types/datasets";
import { geometryFixture } from "./fixtures/geometry";

describe("useDataset", () => {
  it("loads the ONI dataset with its narrowed record fields", () => {
    const oni = useDataset("noaa-cpc-oni");
    expect(oni.id).toBe("noaa-cpc-oni");
    expect(oni.records[0]?.anomaly).toEqual(expect.any(Number));
  });

  it("loads the production geometry dataset with its narrowed record fields", () => {
    const geometry = useDataset("limites-inei-ign");
    expect(geometry.records[0]?.departamentos.type).toBe("FeatureCollection");
    expect(validateDataset("limites-inei-ign", geometryFixture).records[0]?.version).toBe("v01");
  });

  it("reports invalid datasets with the file id", () => {
    expect(() => validateDataset("noaa-cpc-oni", { id: "wrong" })).toThrow(
      "[useDataset] data/noaa-cpc-oni.json is invalid:",
    );
  });

  it.each([
    "noaa-cpc-oni",
    "limites-inei-ign",
    "noaa-cpc-outlook",
    "open-meteo-glofas",
    "enfen-communique",
    "noaa-oisst",
    "noaa-ersst",
    "noaa-cpc-nino-weekly",
  ] as DatasetId[])("rejects a malformed record in %s", (id) => {
    const malformed = JSON.parse(JSON.stringify(useDataset(id))) as {
      records: Array<Record<string, unknown>>;
    };
    delete malformed.records[0]!.start;

    expect(() => validateDataset(id, malformed)).toThrow(
      `[useDataset] data/${id}.json is invalid:`,
    );
  });
});
