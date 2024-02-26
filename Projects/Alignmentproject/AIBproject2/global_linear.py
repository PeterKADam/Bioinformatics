from AIBP2 import *
import argparse
import os
import files

# these are not the matchscores youre looking for


def main():
    parser = argparse.ArgumentParser(description="Process some sequences.")
    parser.add_argument(
        "--seq1", help="First sequence or path to the file containing it"
    )
    parser.add_argument(
        "--seq2", help="Second sequence or path to the file containing it"
    )
    parser.add_argument(
        "--multifile", help="Path to the file containing both sequences"
    )
    parser.add_argument("--matchscore", required=True, help="Match score")
    parser.add_argument("--gapcost", type=int, required=True, help="Gap cost")
    # parser.add_argument('--gapopen', type=int, required=True, help='Gap open cost')

    args = parser.parse_args()

    seq1 = args.seq1
    seq2 = args.seq2
    gapcost = args.gapcost
    # gapopen = args.gapopen

    # If multifile is provided, read the sequences from the file
    if args.multifile:
        seq1, seq2 = files.load_sequences(args.multifile)

    # If seq1 and seq2 are file paths, read the sequences from the files
    elif os.path.isfile(seq1):
        seq1 = files.load_sequences(args.multifile)

        if seq2 and os.path.isfile(seq2):
            seq2 = files.load_sequences(args.multifile)
    else:
        print(
            "Error: u did something dumdum, or we did. but probably u, but might be us, but are the sequences ok?"
        )

    matchscore = files.load_match_scores(args.matchscore)

    Alignments = LinearGlobalAlignment(seq1, seq2, matchscore, gapcost).alignments

    # print(Alignments)
    # Save the computed alignments in .fasta format
    files.SaveAlignments(Alignments, "global_linear")

    print("Alignments saved in .fasta format. hopefully correctly.")


if __name__ == "__main__":
    main()
