import argparse
import json
import os

from trainer import model

import tensorflow as tf

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--train_data_path",
        help="GCS location of training data",
        required=True
    )
    parser.add_argument(
        "--eval_data_path",
        help="GCS location of evaluation data",
        required=True
    )
    parser.add_argument(
        "--output_dir",
        help="GCS location to write checkpoints and export models",
        default = os.getenv("AIP_MODEL_DIR")
    )
    parser.add_argument(
        "--batch_size",
        help="Number of examples to compute gradient over.",
        type=int,
        default=512
    )
    parser.add_argument(
        "--nnsize",
        help="Hidden layer sizes for DNN -- provide space-separated layers",
        default="128 32 4"
    )
    parser.add_argument(
        "--nembeds",
        help="Embedding size of a cross of n key real-valued parameters",
        type=int,
        default=3
    )
    parser.add_argument(
        "--num_epochs",
        help="Number of epochs to train the model.",
        type=int,
        default=10
    )
    parser.add_argument(
        "--train_examples",
        help="""Number of examples (in thousands) to run the training job over.
        If this is more than actual # of examples available, it cycles through
        them. So specifying 1000 here when you have only 100k examples makes
        this 10 epochs.""",
        type=int,
        default=5000
    )
    parser.add_argument(
        "--eval_steps",
        help="""Positive number of steps for which to evaluate model. Default
        to None, which means to evaluate until input_fn raises an end-of-input
        exception""",
        type=int,
        default=None
    )

    # Parse all arguments
    args = parser.parse_args()
    arguments = args.__dict__

    # Modify some arguments
    arguments["train_examples"] *= 1000

    # Run the training job
    model.train_and_evaluate(arguments)