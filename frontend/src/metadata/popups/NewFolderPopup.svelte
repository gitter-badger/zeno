<script lang="ts">
	import Button from "@smui/button";
	import Paper, { Content } from "@smui/paper";
	import Textfield from "@smui/textfield";

	import { folders, slices } from "../../stores";
	import { clickOutside } from "../../util/clickOutside";

	export let edit = false;
	export let showNewFolder;
	export let folderName = "";

	let originalFolderName = folderName;

	let input;

	$: invalidName =
		($folders.includes(folderName) && folderName !== originalFolderName) ||
		folderName.length === 0;

	function createFolder() {
		if (edit) {
			folders.update((f) => {
				f.splice(f.indexOf(originalFolderName), 1);
				f.push(folderName);
				slices.update((slis) => {
					[...slis.keys()].forEach((sliKey) => {
						let s = slis.get(sliKey);
						if (s.folder === originalFolderName) {
							s.folder = folderName;
							slis.set(sliKey, s);
						}
					});
					return slis;
				});
				return f;
			});
		} else {
			folders.update((f) => {
				f.push(folderName);
				folderName = "";
				return [...f];
			});
		}
		showNewFolder = false;
	}

	function submit(e) {
		if (showNewFolder && e.key === "Enter") {
			createFolder();
		}
	}

	$: if (showNewFolder && input) {
		input.getElement().focus();
	}
</script>

<svelte:window on:keydown={submit} />

<div
	id="paper-container"
	use:clickOutside
	on:click_outside={() => (showNewFolder = false)}>
	<Paper elevation={7}>
		<Content style="display: flex; align-items: center;">
			<Textfield
				bind:value={folderName}
				label="Folder Name"
				bind:this={input} />
			<Button
				style="margin-left: 20px;"
				variant="outlined"
				disabled={invalidName}
				on:click={() => createFolder()}>{edit ? "Update" : "Create"}</Button>
		</Content>
		{#if invalidName && folderName.length > 0}
			<p style:margin-right="10px" style:color="#B71C1C">
				folder already exists
			</p>
		{/if}
	</Paper>
</div>

<style>
	#paper-container {
		position: absolute;
		z-index: 9999;
		margin-top: 10px;
	}
</style>
