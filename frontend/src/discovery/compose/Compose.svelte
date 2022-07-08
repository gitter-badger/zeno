<script lang="ts">
	import { post } from "../discovery";
	import { model as m } from "../../stores";
	import { onMount, createEventDispatcher } from "svelte";
	const dispatch = createEventDispatcher();

	$: model = $m;
	let initView = "embedding projection";
	let pipeView = "filter->projection";
	let weakView = "region";
	let pipelineInitialized = false;
	let initProjectionOutput = [];

	async function initPipeline(modelName: string): Promise<object> {
		const output = await post("api/init-pipeline", {
			model: modelName,
		});
		return output;
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
		<div>
			{#if pipelineInitialized}
				{initView}
			{/if}
		</div>
	</div>

	<div id="pipe-view">
		<div>Pipe View</div>
		<div>
			{pipeView}
		</div>
	</div>

	<div id="weak-labeler-view">
		<div>Weak Labeler View</div>
		<div>
			{weakView}
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
