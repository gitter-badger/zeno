import { MetadataType } from "./../globals";
import type ColumnTable from "arquero/dist/types/table/column-table";

import * as aq from "arquero";
import { get } from "svelte/store";
import {
	filteredTable,
	folders,
	metadataSelections,
	model,
	sliceSelections,
	tab,
	transforms,
	metrics,
	models,
	ready,
	results,
	settings,
	slices,
	table,
	metric,
	reports,
	rowsPerPage,
} from "../stores";
import { ZenoColumnType } from "../globals";

const PREDICATE_MAP = {
	"": "",
	AND: "&&",
	OR: "||",
};

export function initialFetch() {
	fetch("/api/settings")
		.then((r) => r.json())
		.then((s) => {
			settings.set(s);
			rowsPerPage.set(s.samples);
			fetch("/api/initialize")
				.then((r) => r.json())
				.then((r) => {
					models.set(r.models);
					metrics.set(r.metrics);
					transforms.set(r.transforms);
					folders.set(r.folders);

					model.set(r.models[r.models.length - 1]);
					metric.set(r.metrics[0]);

					ready.set(true);
				});
		});
}

export async function getSlicesAndReports(t) {
	const slicesRes = await fetch("/api/slices").then((d) => d.json());
	const slis = JSON.parse(slicesRes) as Slice[];
	slis.forEach((s: Slice) => {
		if (s.filterPredicates) {
			s.idxs = t
				.filter("(d) => " + getFilterFromPredicates(s.filterPredicates))
				.array(columnHash(get(settings).idColumn));
		}
	});
	const sliMap = new Map();
	slis.forEach((e) => sliMap.set(e.sliceName, e));
	slices.set(sliMap);

	const reportsRes = await fetch("/api/reports").then((d) => d.json());
	const localReports = JSON.parse(reportsRes) as Report[];
	reports.set(localReports);
}

export function updateTab(t: string) {
	if (t === "home") {
		window.location.hash = "";
	} else {
		window.location.hash = "#/" + t + "/";
	}
	tab.set(t);
}

export async function getMetricsForSlices(metricKeys: MetricKey[]) {
	if (metricKeys[0].metric === undefined) {
		return null;
	}
	const returnValues = metricKeys.map((k) => {
		if (k.sli.sliceName === "overall" || k.sli.sliceName === "") {
			return undefined;
		}
		return get(results).get(k);
	});
	const requiredIndices = returnValues.reduce((arr, curr, i) => {
		if (curr === undefined) {
			arr.push(i);
		}
		return arr;
	}, []);

	if (requiredIndices.length > 0) {
		let res = await fetch("/api/results", {
			method: "POST",
			headers: {
				"Content-type": "application/json",
			},
			body: JSON.stringify(requiredIndices.map((i) => metricKeys[i])),
		}).then((d) => d.json());
		res = JSON.parse(res);
		results.update((resmap) => {
			res.forEach((r, i) => resmap.set(metricKeys[i], r));
			return resmap;
		});
		requiredIndices.forEach((r, i) => (returnValues[r] = res[i]));
	}
	return returnValues;
}

export function updateSliceIdxs() {
	slices.update((slis) => {
		slis.forEach((sli) => {
			sli.idxs = get(table)
				.filter("(d) => " + getFilterFromPredicates(sli.filterPredicates))
				.array(columnHash(get(settings).idColumn));
			slis.set(sli.sliceName, sli);
		});
		return slis;
	});
}

export function getFilterFromPredicates(
	predicateGroup: FilterPredicateGroup,
	groupIndex = 0
) {
	if (predicateGroup.predicates.length === 0) {
		return "true";
	}

	let ret = (groupIndex > 0 ? PREDICATE_MAP[predicateGroup.join] : "") + " (";

	predicateGroup.predicates.forEach(
		(p: FilterPredicate | FilterPredicateGroup, predicateIndex) => {
			if ("predicates" in p) {
				ret += getFilterFromPredicates(p, groupIndex + predicateIndex);
				return;
			}

			if (p.column.columnType === ZenoColumnType.POSTDISTILL) {
				p.column.model = get(model);
			}

			const hash = columnHash(p.column);

			if (p.join === "") {
				ret +=
					` (d["${hash}"]` +
					" " +
					p.operation +
					" " +
					(isNaN(parseFloat(p.value)) ? `"${p.value}"` : p.value) +
					") ";
			} else {
				let join = "";
				if (predicateIndex !== 0) {
					join = PREDICATE_MAP[p.join];
				}
				ret +=
					join +
					" (" +
					`d["${hash}"]` +
					" " +
					p.operation +
					" " +
					(isNaN(parseFloat(p.value)) ? `"${p.value}"` : p.value) +
					") ";
			}
		}
	);

	ret += ") ";
	return ret;
}

export function updateTableColumns(w: WSResponse) {
	let t = get(table);

	const tableColumns = t.columnNames();
	const missingColumns = w.completeColumns.filter(
		(c) => !tableColumns.includes(columnHash(c))
	);
	if (missingColumns.length > 0) {
		fetch("/api/table", {
			method: "POST",
			headers: {
				"Content-type": "application/json",
			},
			body: JSON.stringify(missingColumns),
		})
			.then((d: Response) => d.arrayBuffer())
			.then((d) => {
				if (t.size === 0) {
					t = aq.fromArrow(d);
				} else {
					t = t.assign(aq.fromArrow(d));
				}
				table.set(t);

				// TODO: move somewhere more logical.
				if (get(slices).size === 0 && w.doneProcessing) {
					getSlicesAndReports(t);
				}
			});
	}
}

export function columnHash(col: ZenoColumn) {
	return (
		col.columnType +
		col.name +
		(col.model ? col.model : "") +
		(col.transform ? col.transform : "")
	);
}

function arrayEquals(a, b) {
	return (
		Array.isArray(a) &&
		Array.isArray(b) &&
		a.length === b.length &&
		a.every((val, index) => val === b[index])
	);
}

export function updateFilteredTable(t: ColumnTable) {
	if (!get(ready) || t.size === 0) {
		return;
	}
	let tempTable = t;

	// Filter with slices.
	get(sliceSelections).forEach((s) => {
		const filt = getFilterFromPredicates(get(slices).get(s).filterPredicates);
		tempTable = tempTable.filter(`(d) => ${filt}`);
	});

	// Filter with metadata selections.
	[...get(metadataSelections).entries()].forEach((e) => {
		const [hash, entry] = e;
		const metadataType = entry.column.metadataType;
		if (metadataType === MetadataType.CONTINUOUS) {
			tempTable = tempTable.filter(
				`(r) => r["${hash}"] > ${entry.values[0]} && r["${hash}"] < ${entry.values[1]}`
			);
		} else if (metadataType === MetadataType.BOOLEAN) {
			if (entry.values[0] === "is") {
				tempTable = tempTable.filter(`(r) => r["${hash}"] == 1`);
			} else {
				tempTable = tempTable.filter(`(r) => r["${hash}"] == 0`);
			}
		} else if (metadataType === MetadataType.DATETIME) {
			tempTable = tempTable.filter(
				aq.escape(
					(r) =>
						(entry.values[0] ? new Date(r[hash]) > entry.values[0] : true) &&
						(entry.values[1] ? new Date(r[hash]) < entry.values[1] : true)
				)
			);
		} else if (metadataType === MetadataType.NOMINAL) {
			tempTable = tempTable.filter(
				aq.escape((r) => aq.op.includes(entry.values, r[hash], 0))
			);
		} else {
			tempTable = tempTable.filter(
				`(r) => op.match(r["${hash}"], "${entry.values[0]}")`
			);
		}
	});

	const idCol = columnHash(get(settings).idColumn);
	if (arrayEquals(tempTable.array(idCol), get(filteredTable).array(idCol))) {
		return;
	}
	if (
		arrayEquals(tempTable.array(idCol), t.array(idCol)) &&
		arrayEquals(tempTable.array(idCol), get(filteredTable).array(idCol))
	) {
		return;
	}

	filteredTable.set(tempTable);
}

export function enforce({ rule, name }: { rule: boolean; name: string }) {
	if (rule !== true) {
		throw new Error(`Violated: ${name}`);
	}
}

export function extentXY<T>(
	data: T[],
	xGetter = (d: T) => d[0],
	yGetter = (d: T) => d[1]
) {
	const firstPoint = data[0];
	const xExtent = { min: xGetter(firstPoint), max: xGetter(firstPoint) };
	const yExtent = { min: yGetter(firstPoint), max: yGetter(firstPoint) };
	for (let i = 1; i < data.length; i++) {
		const value = data[i];
		const xValue = xGetter(value),
			yValue = yGetter(value);
		// mins
		if (xValue < xExtent.min) {
			xExtent.min = xValue;
		}
		if (yValue < yExtent.min) {
			yExtent.min = yValue;
		}
		// maxs
		if (xValue > xExtent.max) {
			xExtent.max = xValue;
		}
		if (yValue > yExtent.max) {
			yExtent.max = yValue;
		}
	}
	return { xExtent, yExtent };
}
