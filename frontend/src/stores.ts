import { derived, writable, type Readable, type Writable } from "svelte/store";
import { InternMap } from "internmap";
import { websocketStore } from "svelte-websocket-store";
import type ColumnTable from "arquero/dist/types/table/column-table";
import * as aq from "arquero";

export const settings: Writable<Settings> = writable({
  task: "",
  idColumn: "",
  labelColumn: "",
  metadata: [],
});
export const metrics = writable([]);
export const models = writable([]);
export const ready: Writable<boolean> = writable(false);

export const wsResponse: Writable<WSResponse> = websocketStore(
  `ws://localhost:${location.port}/api/status`,
  {
    status: "connecting",
    slices: [],
    columns: [],
  } as WSResponse
);

export const status: Readable<string> = derived(
  wsResponse,
  ($wsResponse) => $wsResponse.status,
  "connecting"
);

export const slices: Readable<Map<string, Slice>> = derived(
  wsResponse,
  ($wsResponse) => {
    if ($wsResponse.slices.length > 0) {
      const retMap = new Map<string, Slice>();
      $wsResponse.slices.forEach((s) => {
        retMap.set(s.name, s);
      });
      return retMap;
    } else {
      return new Map<string, Slice>();
    }
  }
);

export const table: Writable<ColumnTable> = writable(aq.table({}));

export const results: Writable<InternMap<ResultKey, number>> = writable(
  new InternMap([], (d) => d.slice + "." + d.metric + "." + d.model)
);
