<script lang="ts">
	import Legend from "../legend/Legend.svelte";
	import AutoscaledRegl from "./AutoscaledRegl.svelte";
	import { schemeCategory10 } from "d3-scale-chromatic";
	import { createEventDispatcher } from "svelte";
	const dispatch = createEventDispatcher();

	const defaultColors = schemeCategory10 as string[];
	export let width = 800;
	export let height = 800;
	export let points = new Array(10_000).fill(0).map((_, i) => ({
		color: Math.random(),
		opacity: 0.65,
		x: (Math.PI * i) / 2,
		y: Math.sin(i),
	}));
	export let legend = defaultColors.map((c, i) => ({
		color: c,
		value: `${i}`,
	}));
	$: colorRange = legend.map((item) => item.color);
	let mousePos = [0, 0];
	let conversion;
</script>

<div id="legendary" style:width="{width}px" style:height="{height}px">
	{#if points.length > 0}
		<div
			id="bottom-scatter"
			on:mousemove={(e) => {
				mousePos[0] = e.offsetX;
				mousePos[1] = e.offsetY;
				dispatch("mousemove", {
					mousePos,
					screenPos: conversion.screenSpaceToPointSpace(mousePos),
				});
			}}>
			<AutoscaledRegl
				{width}
				{height}
				{colorRange}
				{points}
				on:view={(e) => {
					conversion = e.detail;
				}}
				on:create
				on:draw
				on:select
				on:deselect />
		</div>
	{/if}
	<div id="top-legend">
		<Legend gap={5} data={legend} squareWidth={25} />
	</div>
	<!-- <div style="position: absolute; left: {mousePos[0]}px; top: {mousePos[1]}px;">
		mouse here
	</div> -->
</div>

<style lang="scss">
	#legendary {
		position: relative;
		// border: 1px solid lightgray;
		#top-legend {
			position: absolute;
			left: 11px;
			top: 11px;
		}
	}
</style>
