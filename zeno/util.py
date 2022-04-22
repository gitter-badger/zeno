import os
from importlib import util
from inspect import signature
from multiprocessing.connection import Connection
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from tqdm import tqdm, trange  # type: ignore

# import pyarrow as pa  # type: ignore

from .classes import DataLoader, ModelLoader, Preprocessor, Slice, Slicer


def get_arrow_bytes(df, id_col):
    # df_arrow = pa.Table.from_pandas(df)
    # buf = pa.BufferOutputStream()
    # with pa.ipc.new_file(buf, df_arrow.schema) as writer:
    #     writer.write_table(df_arrow)
    # return bytes(buf.getvalue())
    df[id_col] = df.index
    js = df.to_json()
    return js


def get_function(file_name, function_name):
    spec = util.spec_from_file_location("module.name", file_name)
    test_module = util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(test_module)  # type: ignore
    return getattr(test_module, function_name)  # type: ignore


def preprocess_data(
    conn: Connection,
    preprocessors: List[Preprocessor],
    data_path: str,
    cache_path: str,
    df: pd.DataFrame,
    data_loader: DataLoader,
    batch_size: int,
):
    data_loader_fn = get_function(data_loader.file_name, data_loader.name)

    for preprocessor in tqdm(preprocessors, desc="preprocessors"):
        preprocessor_fn = get_function(preprocessor.file_name, preprocessor.name)

        conn.send(("Running preprocessor " + preprocessor.name, None))
        save_path = Path(
            cache_path,
            "zenopreprocess_" + preprocessor.name + ".pickle",
        )

        try:
            col = pd.read_pickle(save_path)
        except FileNotFoundError:
            col = pd.Series([pd.NA] * df.shape[0], index=df.index)
        to_predict_indices = col.loc[pd.isna(col)].index

        if len(to_predict_indices) > 0:
            if len(to_predict_indices) < batch_size:
                data = data_loader_fn(df.loc[to_predict_indices], data_path)
                out = preprocessor_fn(data)
                col.loc[to_predict_indices] = out
                col.to_pickle(save_path)
            else:
                for i in trange(
                    0, len(to_predict_indices), batch_size, desc="preprocessing batches"
                ):
                    conn.send(
                        (
                            "Running preprocessor "
                            + preprocessor.name
                            + " ( "
                            + str(i / batch_size)
                            + "/"
                            + str(round(len(to_predict_indices) / batch_size))
                            + " )",
                            None,
                        )
                    )
                    data = data_loader_fn(
                        df.loc[to_predict_indices[i : i + batch_size]],
                        data_path,
                    )
                    out = preprocessor_fn(data)
                    col.loc[to_predict_indices[i : i + batch_size]] = out
                    col.to_pickle(save_path)

        conn.send(("Finished preprocessor " + preprocessor.name, col))
    conn.send(("Done", None))


def run_inference(
    conn: Connection,
    model_paths: List[str],
    data_path: str,
    cache_path: str,
    df: pd.DataFrame,
    data_loader: DataLoader,
    model_loader: ModelLoader,
    batch_size: int,
):
    data_loader_fn = get_function(data_loader.file_name, data_loader.name)
    model_loader_fn = get_function(model_loader.file_name, model_loader.name)

    for model_path in tqdm(model_paths, desc="models"):
        model_name = os.path.basename(model_path).split(".")[0]

        conn.send(("Running inference for " + model_name, None))
        inference_save_path = Path(
            cache_path,
            "zenomodel_" + model_name + ".pickle",
        )
        embedding_save_path = Path(
            cache_path,
            "zenoembedding_" + model_name + ".pickle",
        )

        try:
            inference_col = pd.read_pickle(inference_save_path)
        except FileNotFoundError:
            inference_col = pd.Series([pd.NA] * df.shape[0], index=df.index)
        try:
            embedding_col = pd.read_pickle(embedding_save_path)
        except FileNotFoundError:
            embedding_col = pd.Series([pd.NA] * df.shape[0], index=df.index)

        to_predict_indices = inference_col.loc[pd.isna(inference_col)].index

        if len(to_predict_indices) > 0:
            fn = model_loader_fn(model_path)
            if len(to_predict_indices) < batch_size:
                data = data_loader_fn(df.loc[to_predict_indices], data_path)
                out = fn(data)

                # Check if we also get embedding
                if type(out) == tuple and len(out) == 2:
                    for i, idx in enumerate(to_predict_indices):
                        inference_col.at[idx] = out[0][i]
                        embedding_col.at[idx] = out[1][i]
                    embedding_col.to_pickle(embedding_save_path)
                    out = out[0]
                else:
                    inference_col[to_predict_indices] = out
                inference_col.to_pickle(inference_save_path)
            else:
                for i in trange(
                    0, len(to_predict_indices), batch_size, desc="batch inference"
                ):
                    conn.send(
                        (
                            "Running inference for "
                            + model_name
                            + " ( "
                            + str(i / batch_size)
                            + "/"
                            + str(round(len(to_predict_indices) / batch_size))
                            + " )",
                            None,
                        )
                    )

                    data = data_loader_fn(
                        df.loc[to_predict_indices[i : i + batch_size]], data_path
                    )
                    out = fn(data)

                    # Check if we also get embedding
                    if type(out) == tuple and len(out) == 2:
                        for i, idx in enumerate(to_predict_indices[i : i + batch_size]):
                            inference_col.at[idx] = out[0][i]
                            embedding_col.at[idx] = out[1][i]
                        embedding_col.to_pickle(embedding_save_path)
                        out = out[0]
                    else:
                        inference_col[to_predict_indices[i : i + batch_size]] = out
                    inference_col.to_pickle(inference_save_path)
        conn.send(
            ("Finished inference for " + model_name, inference_col, embedding_col)
        )
    conn.send(("Done", None))


def slice_data(metadata: pd.DataFrame, slicer: Slicer, label_column: str):
    if len(signature(slicer.func).parameters) == 2:
        slicer_output = slicer.func(metadata, label_column)
    else:
        slicer_output = slicer.func(metadata)

    if isinstance(slicer_output, pd.DataFrame):
        slicer_output = slicer_output.index

    slices = {}
    # Can either be of the from [index list] or [(name, index list)..]
    if isinstance(slicer_output, pd.Index) and len(slicer_output) == 0:
        metadata.loc[:, "zenoslice_" + ".".join(slicer.name_list)] = pd.Series(
            np.zeros(len(metadata), dtype=int), dtype=int
        )
        slices[".".join(slicer.name_list)] = Slice(
            ".".join(slicer.name_list), "programmatic", slicer_output
        )
    elif (
        isinstance(slicer_output[0], tuple) or isinstance(slicer_output[0], list)
    ) and len(slicer_output) > 0:
        for output_slice in slicer_output:
            indices = output_slice[1]
            name_list = [*slicer.name_list, output_slice[0]]
            metadata.loc[:, "zenoslice_" + ".".join(name_list)] = pd.Series(
                np.zeros(len(metadata), dtype=int), dtype=int
            )
            metadata.loc[indices, "zenoslice_" + ".".join(name_list)] = 1
            slices[".".join(name_list)] = Slice(
                ".".join(name_list), "programmatic", indices
            )
    else:
        metadata.loc[:, "zenoslice_" + ".".join(slicer.name_list)] = pd.Series(
            np.zeros(len(metadata), dtype=int), dtype=int
        )
        metadata.loc[slicer_output, "zenoslice_" + ".".join(slicer.name_list)] = 1
        slices[".".join(slicer.name_list)] = Slice(
            ".".join(slicer.name_list), "programmatic", slicer_output
        )
    return slices
