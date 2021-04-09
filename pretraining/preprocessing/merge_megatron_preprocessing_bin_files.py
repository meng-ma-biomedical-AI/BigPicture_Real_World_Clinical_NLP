#! /bin/python

"""
script used to merge bin files generated by the Megatron-LM/tools/preprocessing.py

copy from https://github.com/NVIDIA/Megatron-LM/pull/84
ref: https://github.com/NVIDIA/Megatron-LM/issues/81

TO use this script, you need to modify Megatron-LM/megatron/data/indexed_dataset.py according to the PR-84
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.path.pardir)))
from megatron.data import indexed_dataset
from megatron.tokenizer import build_tokenizer
import argparse
from pathlib import Path


def main(args):
    args.rank = 0
    args.make_vocab_size_divisible_by = 128
    args.tensor_model_parallel_size = 1
    args.model_parallel_size = 1
    args.merge_file = None

    pin = Path(args.input)
    data_path_prefix = [str(each)[:-4] for each in pin.glob("*.bin")]

    pout = Path(args.output)
    pout.mkdir(parents=True, exist_ok=True)
    output_bin_files = pout / f"{args.output_prefix}.bin"
    output_idx_files = pout / f"{args.output_prefix}.idx"
    try:
        os.remove(output_bin_files)
        os.remove(output_idx_files)
    except:
        pass

    tokenizer = build_tokenizer(args)

    builders = indexed_dataset.make_builder(output_bin_files,  impl='mmap', vocab_size=tokenizer.vocab_size)
    for each in data_path_prefix:
        builders.merge_file_(each)

    builders.finalize(output_idx_files)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True,
                        help="input dir with all bin and idx files for merging")
    parser.add_argument("--output", type=str, required=True,
                        help="output merged file dir")
    parser.add_argument("--output_prefix", type=str, required=True,
                        help="the prefix file - file name ")
    parser.add_argument("--vocab_file", type=str, required=True,
                        help="vocab_file full path")
    parser.add_argument("--tokenizer_type", type=str, default="BertWordPieceCase",
                        help="tokenizer_type")
    global_args = parser.parse_args()
    main(global_args)