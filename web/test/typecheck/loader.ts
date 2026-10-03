import { useDataset } from "~/composables/useDataset";

const oni = await useDataset("noaa-cpc-oni");
const anomaly: number = oni.records[0]!.anomaly;
void anomaly;

const geometry = await useDataset("limites-inei-ign");
void geometry.records[0]!.departamentos.features[0]!.geometry;

// @ts-expect-error An ONI record does not expose river discharge.
const wrongField: number = oni.records[0]!.river_discharge;
void wrongField;

// @ts-expect-error Dataset ids are restricted to the static catalog.
useDataset("not-a-dataset");
