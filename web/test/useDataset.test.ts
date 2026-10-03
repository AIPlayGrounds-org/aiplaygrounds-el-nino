import { describe, expect, it } from "vitest";
import { useDataset, validateDataset } from "~/composables/useDataset";

describe("useDataset", () => {
  it("loads the ONI dataset with its narrowed record fields", () => {
    const oni = useDataset("noaa-cpc-oni");
    expect(oni.id).toBe("noaa-cpc-oni");
    expect(oni.records[0]?.anomaly).toEqual(expect.any(Number));
  });

  it("reports invalid datasets with the file id", () => {
    expect(() => validateDataset("noaa-cpc-oni", { id: "wrong" })).toThrow(
      "[useDataset] data/noaa-cpc-oni.json is invalid: missing required field source",
    );
  });
});
