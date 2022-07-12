<script lang="ts">
	import { post } from "../discovery";
	import { model as m, filteredTable, settings } from "../../stores";
	import { columnHash } from "../../util";
	import { onMount, createEventDispatcher } from "svelte";
	import SelectionBar from "../../metadata/SelectionBar.svelte";
	const dispatch = createEventDispatcher();

	$: model = $m;
	let initView = "embedding projection";
	let pipeView = "filter->projection";
	let weakView = "region";
	let pipelineInitialized = false;
	let initProjectionOutput = [];
	let currentProjectionOutput = [];
	export let polygon = [];

	async function pipelinePost(name: string, payload: object) {
		return post(`api/pipeline/${name}`, payload);
	}

	async function clearPipeline(): Promise<object> {
		const output = await pipelinePost("clear", {});
		return output;
	}
	async function regionBasedLabeler(
		name: string = "default",
		polygon: number[][] = []
	): Promise<object> {
		const output = await pipelinePost("region-labeler", {
			name,
			polygon,
		});
		return output;
	}

	async function initPipeline(modelName: string): Promise<object> {
		const output = await pipelinePost("init", {
			model: modelName,
		});
		return output;
	}

	async function filterProjection(): Promise<object> {
		const body = {
			instance_ids: $filteredTable.columnArray(columnHash($settings.idColumn)),
		};
		const output = await pipelinePost("hard-filter", body);
		const output2 = await pipelinePost("embedding-projection", {
			n_epochs: 10,
		});
		return output2;
	}

	let mounted = false;
	onMount(() => {
		mounted = true;
	});
	let runOnceInit = false;
	$: {
		if (mounted && !runOnceInit) {
			initPipeline(model)
				.then((d) => {
					initProjectionOutput = d["data"];
					dispatch("init", initProjectionOutput);
					pipelineInitialized = true;
					console.log(pipelineInitialized, initProjectionOutput);
				})
				.catch((e) => {
					console.log(e);
				});
			runOnceInit = true;
		}
	}
</script>

<h3>Composition View</h3>
<div id="composer">
	<div id="init-view">
		<div>Init View</div>
		<button
			on:click={async () => {
				const output = await clearPipeline();
				dispatch("init", initProjectionOutput);
			}}>Go Back and clear</button>
		<div>
			{#if pipelineInitialized}
				{initView}
			{/if}
		</div>
	</div>

	<div id="pipe-view">
		<div>Pipe View</div>
		<button
			on:click={async () => {
				const output = await clearPipeline();
			}}>Clear Pipeline</button>
		<div style="display: flex; gap: 5px;">
			<div class="filter">
				filter
				<SelectionBar />
			</div>
			<div class="projection">projection</div>
		</div>
		<button
			on:click={async () => {
				const output = await filterProjection();
				console.log(output);
				dispatch("init", output["data"]);
			}}>Filter + Project</button>
	</div>

	<div id="weak-labeler-view">
		<div>Weak Labeler View</div>
		<div>
			{weakView}

			<button
				on:click={async () => {
					const output = await regionBasedLabeler("default", polygon);
					console.log(output);
				}}>Add Weak Add Region Labeler</button>
		</div>
	</div>
</div>

<style>
	#composer {
		border: solid 1px lightblue;
		height: 300px;
		width: 100%;
		display: flex;
	}
	#composer > * {
		border: 1px solid lightgrey;
	}
	#init-view {
		flex: 1;
	}
	#pipe-view {
		flex: 2;
	}
	#weak-labeler-view {
		flex: 1;
	}
</style>
