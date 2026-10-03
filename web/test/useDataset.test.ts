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
    ["noaa-cpc-oni", "anomaly"],
    ["limites-inei-ign", "version"],
    ["noaa-cpc-outlook", "categories"],
    ["open-meteo-glofas", "river_discharge"],
    ["enfen-communique", "status"],
    ["noaa-oisst", "lat"],
    ["noaa-ersst", "nino3_anomaly"],
  ] as [Exclude<DatasetId, "noaa-cpc-nino-weekly">, string][])(
    "rejects a malformed kind-specific record in %s",
    (id, field) => {
      const malformed = JSON.parse(JSON.stringify(useDataset(id))) as {
        records: Array<Record<string, unknown>>;
      };
      delete malformed.records[0]![field];

      expect(() => validateDataset(id, malformed)).toThrow(
        `[useDataset] data/${id}.json is invalid:`,
      );
    },
  );

  it("documents the weekly dataset schema gap without adding a validator", () => {
    const malformed = JSON.parse(JSON.stringify(useDataset("noaa-cpc-nino-weekly"))) as {
      records: Array<Record<string, unknown>>;
    };
    delete malformed.records[0]!.nino_1_2_sst;

    expect(() => validateDataset("noaa-cpc-nino-weekly", malformed)).not.toThrow();
  });
});
