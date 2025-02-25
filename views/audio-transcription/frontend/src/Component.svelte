<script lang="ts">
  import { mdiPause, mdiPlay } from "@mdi/js";
  import { Svg } from "@smui/common/elements";
  import IconButton, { Icon } from "@smui/icon-button";
  import WaveSurfer from "wavesurfer.js/dist/wavesurfer.js";
  import SpectrogramPlugin from "wavesurfer.js/dist/plugin/wavesurfer.spectrogram.js";
  import colormap from "colormap";

  // List of objects with keys corresponding to the following props.
  export let table;
  // Key for model outputs.
  export let modelColumn;
  // Key for groundtruth labels.
  export let labelColumn;
  // Key for the input data.
  export let dataColumn;
  // Key for the transformed data (current transform).
  export let transformColumn;
  // Key for unique identifier of each item.
  export let idColumn;

  const colors = colormap({
    colormap: "density",
    nshades: 256,
    format: "float",
  });

  let divs = [];
  let specDivs = [];

  $: waves = divs.map((d, i) => {
    if (d) {
      d.innerHTML = "";
      let w;
      w = WaveSurfer.create({
        container: d,
        waveColor: "#6a1b9a",
        progressColor: "#6a1b9a",
        mediaControls: true,
        height: 50,
        plugins: [
          SpectrogramPlugin.create({
            container: specDivs[i],
            labels: false,
            height: 50,
            frequencyMax: 4410,
            colorMap: colors,
          }),
        ],
      });
      if (!transformColumn) {
        w.load(`/data/${table[i][idColumn]}`);
      } else {
        w.load(`/cache/${transformColumn}/${table[i][transformColumn]}`);
      }
      return w;
    }
  });
</script>

<div id="container">
  {#each table as row, i}
    <div class="box">
      <div style:display="flex">
        <IconButton
          on:click={() => {
            waves[i].isPlaying() ? waves[i].pause() : waves[i].play();
          }}
        >
          <Icon component={Svg} viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d={waves[i] && waves[i].isPlaying() ? mdiPause : mdiPlay}
            />
          </Icon>
        </IconButton>
        <div
          style:width="150px"
          style:height="50px"
          bind:this={divs[i]}
          id={"wave_" + row[idColumn]}
        />
      </div>
      <div class="spec" bind:this={specDivs[i]} />
      <span class="label">label: </span><span class="value">
        {row[labelColumn]}
      </span>
      {#if modelColumn && row[modelColumn] !== undefined}
        <br />
        <span class="label">output: </span>
        <span class="value">{row[modelColumn]} </span>
      {/if}
    </div>
  {/each}
</div>

<style>
  .spec {
    height: 75px;
    width: 150px;
    margin-left: 48px;
  }
  .label {
    font-size: 12px;
    color: rgba(0, 0, 0, 0.5);
    font-variant: small-caps;
  }
  .value {
    font-size: 12px;
  }
  .box {
    padding: 10px;
    margin: 10px;
    border: 0.5px solid rgb(224, 224, 224);
  }
  #container {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
  }

  :global(spectrogram canvas) {
    z-index: 0 !important;
  }
  :global(wave canvas) {
    z-index: 0 !important;
  }
  :global(wave) {
    z-index: 0 !important;
  }
</style>
