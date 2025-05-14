

import argparse
from .model import CustomModel


def main():
    """main"""
    parser4model = argparse.ArgumentParser()
    parser4train = argparse.ArgumentParser()

    parser4train.add_argument(
        "--batch_size",
        help="Batch size for training steps",
        type=int,
        default=32,
    )
    parser4train.add_argument(
        "--eval_data_path",
        help="GCS location pattern of eval files",
        required=True,
    )
    parser4model.add_argument(
        "--nnsize",
        help="Hidden layer sizes (provide space-separated sizes)",
        default="32 8",
    )
    parser4model.add_argument(
        "--nbuckets",
        help="Number of buckets to divide lat and lon with",
        type=int,
        default=10,
    )
    parser4train.add_argument(
        "--lr", help="learning rate for optimizer", type=float, default=0.001
    )
    parser4train.add_argument(
        "--num_evals",
        help="Number of times to evaluate model on eval data training.",
        type=int,
        default=5,
    )
    parser4train.add_argument(
        "--num_examples_to_train_on",
        help="Number of examples to train on.",
        type=int,
        default=100,
    )
    parser4train.add_argument(
        "--output_dir",
        help="GCS location to write checkpoints and export models",
        required=True,
    )
    parser4train.add_argument(
        "--train_data_path",
        help="GCS location pattern of train files containing eval URLs",
        required=True,
    )
    model_kwargs = parser4model.parse_args().__dict__
    model_kwargs["nnsize"] = [int(s) for s in model_kwargs["nnsize"].split()]
    train_kwargs = parser4train.parse_args().__dict__

    CustomModel(**model_kwargs).train_and_evaluate(**train_kwargs)


if __name__ == "__main__":
    main()
