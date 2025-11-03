#!/usr/bin/env python3
import argparse
import csv
import sys
from typing import Dict, Tuple


def extract_date_from_timestamp(value: str) -> str:
    """Return YYYY-MM-DD from a timestamp string.

    This function avoids timezone normalization by extracting the literal date
    portion as written in the string. It supports formats like:
    - "YYYY-MM-DD HH:MM:SS+00:00"
    - "YYYY-MM-DDTHH:MM:SS.ssssss"
    - "YYYY-MM-DD" (already date-only)
    """
    if not value:
        return ""
    value = value.strip()
    if len(value) >= 10:
        return value[:10]
    return ""


def load_acquisition_dates(tsv2_path: str) -> Dict[Tuple[str, str], str]:
    """Load acquisition dates from TSV2 keyed by (bblid, session).

    TSV2 columns: subject, session, acquisition_time
    - subject is like "sub-138950"; we normalize to "138950" to match TSV1 bblid
    - session is like "ses-1"
    - acquisition_time contains ISO-like datetime; we extract YYYY-MM-DD
    """
    key_to_date: Dict[Tuple[str, str], str] = {}
    with open(tsv2_path, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        required_cols = {"subject", "session", "acquisition_time"}
        missing = required_cols - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"{tsv2_path} is missing required columns: {', '.join(sorted(missing))}"
            )
        for row in reader:
            subject = row["subject"].strip()
            session = row["session"].strip()
            acquisition_time = row["acquisition_time"].strip()

            if subject.startswith("sub-"):
                bblid = subject[len("sub-") :]
            else:
                bblid = subject

            acq_date = extract_date_from_timestamp(acquisition_time)
            if not acq_date:
                continue
            key_to_date[(bblid, session)] = acq_date
    return key_to_date


def write_with_match_column(tsv1_path: str, tsv2_path: str, output_path: str) -> None:
    """Read TSV1, compare dates to TSV2 by (bblid, session), write TSV1 + date_match.

    TSV1 columns: bblid, scanid, session_id, timestamp
    Output: same columns plus a new 5th column: date_match (1 for match, 0 otherwise)
    """
    key_to_date = load_acquisition_dates(tsv2_path)

    with open(tsv1_path, newline="") as f_in:
        reader = csv.DictReader(f_in, delimiter="\t")
        required_cols = {"bblid", "scanid", "session_id", "timestamp"}
        missing = required_cols - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"{tsv1_path} is missing required columns: {', '.join(sorted(missing))}"
            )

        fieldnames = reader.fieldnames + ["date_match"]

        out_stream = (
            sys.stdout if output_path == "-" else open(output_path, "w", newline="")
        )
        try:
            writer = csv.DictWriter(out_stream, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()

            for row in reader:
                bblid = (row.get("bblid") or "").strip()
                session = (row.get("session_id") or "").strip()
                timestamp = (row.get("timestamp") or "").strip()

                ts_date = extract_date_from_timestamp(timestamp)
                acq_date = key_to_date.get((bblid, session), "")
                match = int(ts_date == acq_date and ts_date != "")

                out_row = dict(row)
                out_row["date_match"] = str(match)
                writer.writerow(out_row)
        finally:
            if out_stream is not sys.stdout:
                out_stream.close()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare date parts of TSV1 timestamp and TSV2 acquisition_time by subject/session.\n"
            "Writes TSV1 plus a new 'date_match' column (1 match, 0 mismatch)."
        )
    )
    parser.add_argument(
        "tsv1", help="Path to TSV1 (columns: bblid, scanid, session_id, timestamp)"
    )
    parser.add_argument(
        "tsv2", help="Path to TSV2 (columns: subject, session, acquisition_time)"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="-",
        help="Output path for augmented TSV1 (use '-' for stdout; default '-')",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    write_with_match_column(args.tsv1, args.tsv2, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
