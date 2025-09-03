# pylint: skip-file

import logging
import os

import keras
import numpy as np
import tensorflow as tf
from keras import callbacks
from keras.layers import (
    Concatenate,
    Dense,
    Discretization,
    Embedding,
    Flatten,
    HashedCrossing,
    Input,
    Lambda,
)


def parse_csv(row):
    ds = tf.strings.split(row, ",")
    label = tf.strings.to_number(ds[0])
    feature = tf.strings.to_number(ds[2:6])  # use some features only
    return (feature[0], feature[1], feature[2], feature[3]), label


def create_dataset(pattern, batch_size, num_repeat, mode="eval"):
    ds = tf.data.Dataset.list_files(pattern)
    ds = ds.flat_map(tf.data.TextLineDataset)
    ds = ds.map(parse_csv)
    if mode == "train":
        ds = ds.shuffle(buffer_size=1000)
    ds = ds.repeat(num_repeat).batch(batch_size, drop_remainder=True)
    return ds


def lat_lon_parser(row, pick_lat):
    ds = tf.strings.split(row, ",")
    # latitude idx: 3 and 5, longitude idx: 2 and 4
    idx = [3, 5] if pick_lat else [2, 4]
    return tf.strings.to_number(tf.gather(ds, idx))


def adapt_normalize(train_data_path):
    ds = tf.data.Dataset.list_files(train_data_path)
    ds = ds.flat_map(tf.data.TextLineDataset)
    lat_values = ds.map(lambda x: lat_lon_parser(x, True)).batch(10000)
    lon_values = ds.map(lambda x: lat_lon_parser(x, False)).batch(10000)

    lat_scaler = keras.layers.Normalization(axis=None)
    lon_scaler = keras.layers.Normalization(axis=None)
    lat_scaler.adapt(lat_values)
    lon_scaler.adapt(lon_values)

    print("Computed statistics for latitude:")
    print(f"mean: {lat_scaler.mean}, variance: {lat_scaler.variance}")
    print("+++++")
    print("Computed statistics for longitude:")
    print(f"mean: {lon_scaler.mean}, variance: {lon_scaler.variance}")

    return lat_scaler, lon_scaler


def euclidean(params):
    lon1, lat1, lon2, lat2 = params
    londiff = lon2 - lon1
    latdiff = lat2 - lat1
    return tf.sqrt(londiff * londiff + latdiff * latdiff)


def transform(inputs, nbuckets, normalizers):
    lat_scaler, lon_scaler = normalizers

    # Normalize longitude
    scaled_plon = lon_scaler(inputs["pickup_longitude"])
    scaled_dlon = lon_scaler(inputs["dropoff_longitude"])

    # Normalize latitude
    scaled_plat = lat_scaler(inputs["pickup_latitude"])
    scaled_dlat = lat_scaler(inputs["dropoff_latitude"])

    # Lambda layer for the custom euclidean function
    euclidean_distance = Lambda(euclidean, name="euclidean")(
        [scaled_plon, scaled_plat, scaled_dlon, scaled_dlat]
    )

    # Discretization
    latbuckets = np.linspace(start=-5, stop=5, num=nbuckets).tolist()
    lonbuckets = np.linspace(start=-5, stop=5, num=nbuckets).tolist()

    plon = Discretization(lonbuckets, name="plon_bkt")(scaled_plon)
    plat = Discretization(latbuckets, name="plat_bkt")(scaled_plat)
    dlon = Discretization(lonbuckets, name="dlon_bkt")(scaled_dlon)
    dlat = Discretization(latbuckets, name="dlat_bkt")(scaled_dlat)

    # Feature Cross with HashedCrossing layer
    p_fc = HashedCrossing(num_bins=(nbuckets + 1) ** 2, name="p_fc")(
        (plon, plat)
    )
    d_fc = HashedCrossing(num_bins=(nbuckets + 1) ** 2, name="d_fc")(
        (dlon, dlat)
    )
    pd_fc = HashedCrossing(num_bins=(nbuckets + 1) ** 4, name="pd_fc")(
        (p_fc, d_fc)
    )

    # Embedding with Embedding layer
    pd_embed = Flatten()(
        Embedding(
            input_dim=(nbuckets + 1) ** 4, output_dim=10, name="pd_embed"
        )(pd_fc)
    )

    transformed = Concatenate()(
        [
            scaled_plon,
            scaled_dlon,
            scaled_plat,
            scaled_dlat,
            euclidean_distance,
            pd_embed,
        ]
    )

    return transformed


def rmse(y_true, y_pred):
    squared_error = tf.keras.ops.square(y_pred[:, 0] - y_true)
    return tf.keras.ops.sqrt(tf.keras.ops.mean(squared_error))


def build_dnn_model(nbuckets, nnsize, lr, normalizers):
    INPUT_COLS = [
        "pickup_longitude",
        "pickup_latitude",
        "dropoff_longitude",
        "dropoff_latitude",
    ]

    inputs = {
        colname: Input(name=colname, shape=(1,), dtype="float32")
        for colname in INPUT_COLS
    }

    # transforms
    x = transform(inputs, nbuckets, normalizers)

    for layer, nodes in enumerate(nnsize):
        x = Dense(nodes, activation="relu", name=f"h{layer}")(x)
    output = Dense(1, name="fare")(x)

    model = keras.Model(inputs=list(inputs.values()), outputs=output)
    # TODO 1a
    lr_optimizer = keras.optimizers.Adam(learning_rate=lr)
    model.compile(optimizer=lr_optimizer, loss="mse", metrics=[rmse, "mse"])

    return model


def train_and_evaluate(hparams):
    # TODO 1b
    batch_size = hparams["batch_size"]
    nbuckets = hparams["nbuckets"]
    lr = hparams["lr"]
    nnsize = [int(s) for s in hparams["nnsize"].split()]
    eval_data_path = hparams["eval_data_path"]
    num_evals = hparams["num_evals"]
    num_examples_to_train_on = hparams["num_examples_to_train_on"]
    output_dir = hparams["output_dir"]
    train_data_path = hparams["train_data_path"]

    model_export_path = os.path.join(output_dir, "model.keras")
    serving_model_export_path = os.path.join(output_dir, "savedmodel")
    checkpoint_path = os.path.join(output_dir, "checkpoint.keras")
    tensorboard_path = os.path.join(output_dir, "tensorboard")

    if tf.io.gfile.exists(output_dir):
        tf.io.gfile.rmtree(output_dir)

    normalizers = adapt_normalize(eval_data_path)

    model = build_dnn_model(nbuckets, nnsize, lr, normalizers)
    logging.info(model.summary())

    trainds = create_dataset(
        pattern=train_data_path,
        batch_size=batch_size,
        num_repeat=None,
        mode="train",
    )

    evalds = create_dataset(
        pattern=eval_data_path, batch_size=batch_size, num_repeat=1, mode="eval"
    )

    steps_per_epoch = num_examples_to_train_on // (batch_size * num_evals)

    checkpoint_cb = callbacks.ModelCheckpoint(checkpoint_path, verbose=1)
    tensorboard_cb = callbacks.TensorBoard(tensorboard_path, histogram_freq=1)

    history = model.fit(
        trainds,
        validation_data=evalds,
        epochs=num_evals,
        steps_per_epoch=max(1, steps_per_epoch),
        verbose=2,  # 0=silent, 1=progress bar, 2=one line per epoch
        callbacks=[checkpoint_cb, tensorboard_cb],
    )

    # Save the Keras model file.
    model.save(model_export_path)
    # Exporting the model in savedmodel for serving.
    model.export(serving_model_export_path)
    return history
