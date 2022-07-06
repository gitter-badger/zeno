<script lang="ts">
	import MetadataBar from "../metadata/MetadataPanel.svelte";
	import SelectionBar from "../metadata/SelectionBar.svelte";
	import LegendaryScatter from "./scatter/LegendaryScatter.svelte";
	import Select, { Option } from "@smui/select";
	import Samples from "../samples/Samples.svelte";
	import SampleOptions from "../samples/SampleOptions.svelte";
	import * as d3chromatic from "d3-scale-chromatic";
	import * as aq from "arquero";
	import {
		projectEmbeddings2D,
		reformatAPI,
		interpolateColorToArray,
		indexTable,
		binContinuous,
		getDataRange as uniqueOutputs,
	} from "./discovery";
	import {
		filteredTable,
		model,
		settings,
		table as globalTable,
	} from "../stores";
	import { columnHash } from "../util";

	import type { dataType } from "./discovery";
	import type {
		LegendaryScatterPoint,
		LegendaryLegendEntry,
	} from "./scatter/scatter";
	import type ColumnTable from "arquero/dist/types/table/column-table";
	import { onMount } from "svelte";

	// props
	export let scatterWidth = 900;
	export let scatterHeight = 700;
	export let colorsCategorical = d3chromatic.schemeCategory10 as string[];
	export let colorsContinuous = d3chromatic.interpolateBuPu;

	let projection2D: object[] = [];
	let colorValues: number[] = [];
	let opacityValues: number[] = [];
	let colorBy: string = "0label";
	// eslint-disable-next-line
	let dataType: dataType = "categorical";
	let colorRange: string[] = colorsCategorical;
	let lassoSelectTable = null;

	// stuff that gets updated (reactive)
	$: metadataExists =
		$settings.metadataColumns.length > 0 || $filteredTable._names.length > 0;

	$: pointsExist = projection2D.length > 0;
	$: filteredTableEmpty = $filteredTable._nrows === 0;
	$: tableEmpty = $globalTable._nrows === 0;

	let ranOnce = false;
	let mounted = false;
	onMount(() => {
		mounted = true;
	});

	$: {
		if (!filteredTableEmpty && !tableEmpty && !ranOnce && mounted) {
			updateColors({ colorBy, table: $globalTable });
			const colorColumn = aq.table({ color: colorValues });
			globalTable.set($globalTable.assign(colorColumn));
			console.log($globalTable);
			ranOnce = true;
		}
	}
	$: {
		if (metadataExists && pointsExist && $filteredTable) {
			const curr_ids = $filteredTable.columnArray(
				columnHash($settings.idColumn)
			);
			const filtered_proj = projection2D.filter((proj) =>
				curr_ids.includes(proj["instance_id"])
			);
			const coordinates = filtered_proj.map((projObj) => projObj["projection"]);

			opacityValues = new Array(coordinates.length).fill(1.0);

			updateLegendaryScatter({
				projection2D: coordinates,
				colorRange,
				colorValues: $filteredTable.columnArray("color"),
				dataRange,
				opacityValues,
			});
		}
	}

	// functions
	function scatterSelectEmpty(table: ColumnTable) {
		return table === null;
	}
	function saveIds() {
		if ($filteredTable) {
			return $filteredTable.columnArray(
				columnHash($settings.idColumn)
			) as unknown[];
		} else {
			return [];
		}
	}
	function getMetadata(table: ColumnTable, colorBy: string) {
		return table.columnArray(colorBy) as Array<unknown>;
	}

	let selectedMetadataOutputs,
		dataRange,
		legendaryScatterLegend: LegendaryLegendEntry[],
		legendaryScatterPoints: LegendaryScatterPoint[];

	function inferOutputsType(
		colorBy: string,
		table: ColumnTable = $filteredTable
	) {
		// get the range and type of data
		const metadata = getMetadata(table, colorBy); // get columns for selected metadata
		const { range, type } = uniqueOutputs(metadata); // return the unique categorical or continuous range
		return { metadata, range, type };
	}
	function selectColorsForRange(
		type: dataType,
		metadata: unknown[],
		range: unknown[]
	) {
		// based on datatype inferred color differently
		let colorRange, colorValues;
		if (type === "categorical") {
			colorValues = metadata.map((md) => range.indexOf(md));
			colorRange = colorsCategorical;
		} else if (type === "continuous") {
			const binAssignments = binContinuous(metadata);
			colorValues = binAssignments.map((ass) => range[ass]);
			colorRange = interpolateColorToArray(colorsContinuous, range.length);
		}
		return { colorRange, colorValues };
	}
	function updateColors({ colorBy = "label", table = $filteredTable } = {}) {
		// compute coloring stuff
		const { metadata, range, type } = inferOutputsType(colorBy, table);
		const { colorRange: cRange, colorValues: cValues } = selectColorsForRange(
			type,
			metadata,
			range
		);

		// save globally
		selectedMetadataOutputs = metadata;
		dataRange = range;
		// eslint-disable-next-line
		dataType = type;
		colorRange = cRange;
		colorValues = cValues;
	}

	function packageLegendaryScatterPoints({
		colorRange,
		dataRange,
		projection2D,
		colorValues,
		opacityValues,
	}) {
		const legend = reformatAPI.legendaryScatter.legend(colorRange, dataRange);
		const scatter = reformatAPI.legendaryScatter.points(
			projection2D,
			colorValues,
			opacityValues
		);
		return { scatter, legend };
	}
	function updateLegendaryScatter({
		colorRange,
		colorValues,
		dataRange,
		opacityValues,
		projection2D,
	}) {
		const { legend, scatter } = packageLegendaryScatterPoints({
			colorRange,
			colorValues,
			dataRange,
			opacityValues,
			projection2D,
		});
		// update global variables for rendering
		legendaryScatterLegend = legend;
		legendaryScatterPoints = scatter;
	}
	$: metadataWithModelOptions = $settings.metadataColumns.filter(
		(metadata) => metadata.model === $model || metadata.model === ""
	);
	let regionMode = false;
</script>

<div id="main">
	<MetadataBar />
	<div>
		<!-- Color Dropdown -->
		<div id="color-by">
			{#if metadataExists}
				<Select bind:value={colorBy} label={"Color Points By"}>
					{#each metadataWithModelOptions as metadata, i}
						<Option value={columnHash(metadata)}>{metadata.name}</Option>
					{/each}
				</Select>
			{/if}
		</div>

		<!-- Scatter View -->
		<div id="scatter-view" style:margin-top="10px">
			<div
				class="paper"
				style:width="{scatterWidth}px"
				style:height="{scatterHeight}px"
				style:position="relative">
				<LegendaryScatter
					width={scatterWidth}
					height={scatterHeight}
					legend={legendaryScatterLegend}
					points={legendaryScatterPoints}
					on:deselect={() => {
						lassoSelectTable = null;
					}}
					on:select={({ detail }) => {
						const indexInstances = detail.map(({ index }) => index);
						lassoSelectTable = indexTable($filteredTable, indexInstances);
					}}
					on:mousemove={(e) => {
						// console.log(e.detail);
					}}
					{regionMode} />
			</div>
			<div>
				<p>{$filteredTable.size} instances</p>
				<SelectionBar />
			</div>
		</div>
		<div>
			<button
				on:click={() => {
					regionMode = !regionMode;
				}}
				>Region mode
			</button>
			<button
				on:click={async () => {
					if ($filteredTable) {
						const filteredIds = $filteredTable.columnArray(
							columnHash($settings.idColumn)
						);
						const projection_result = await projectEmbeddings2D(
							$model,
							filteredIds
						);
						projection2D = projection_result["data"];
						console.log(projection2D);
					}
				}}
				>Compute projection
			</button>
		</div>
	</div>

	<!-- Instances view -->
	<div id="instance-view">
		<SampleOptions />
		<Samples
			table={scatterSelectEmpty(lassoSelectTable)
				? $filteredTable
				: lassoSelectTable} />
	</div>
</div>

<style>
	#main {
		display: flex;
		flex-direction: row;
	}
	.paper {
		box-shadow: 0px 0px 3px 3px hsla(0, 0%, 0%, 0.1);
	}
</style>
