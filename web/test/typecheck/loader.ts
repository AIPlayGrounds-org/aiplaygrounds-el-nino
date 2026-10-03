import { useDataset } from "~/composables/useDataset";

const oni = useDataset("noaa-cpc-oni");
const anomaly: number = oni.records[0]!.anomaly;
void anomaly;

// @ts-expect-error An ONI record does not expose river discharge.
const wrongField: number = oni.records[0]!.river_discharge;
void wrongField;

// @ts-expect-error Dataset ids are restricted to the static catalog.
useDataset("not-a-dataset");
