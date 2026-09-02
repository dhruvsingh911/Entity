import os
import json
import re

# =========================================================
# ENTITY KNOWLEDGE BUILDER
# RAW JSON / JSONL -> CLEAN CHUNKS -> knowledge.json
# =========================================================


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

KNOWLEDGE_DIR = os.path.join(
    BASE_DIR,
    "knowledge",
)

RAW_DIR = os.path.join(
    KNOWLEDGE_DIR,
    "raw",
)

OUTPUT_FILE = os.path.join(
    KNOWLEDGE_DIR,
    "knowledge.json",
)


CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


# =========================================================
# CLEAN TEXT
# =========================================================


def clean_text(text):

    if not text:
        return ""

    text = str(text)

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# =========================================================
# GET RECORD TEXT
# =========================================================


def get_record_text(record):

    if not isinstance(record, dict):
        return ""

    parts = []

    fields = [
        "title",
        "Title",
        "content",
        "Content",
        "text",
        "Text",
        "question",
        "Question",
        "answer",
        "Answer",
        "explanation",
        "Explanation",
        "description",
        "Description",
    ]

    for field in fields:

        value = record.get(
            field,
            "",
        )

        value = clean_text(value)

        if value:

            parts.append(value)

    return " ".join(parts).strip()


# =========================================================
# GET RECORD TITLE
# =========================================================


def get_record_title(record):

    if not isinstance(record, dict):
        return "ENTITY Knowledge"

    possible_titles = [
        "title",
        "Title",
        "question",
        "Question",
    ]

    for field in possible_titles:

        title = clean_text(
            record.get(
                field,
                "",
            )
        )

        if title:

            return title

    return "ENTITY Knowledge"


# =========================================================
# SPLIT TEXT INTO CHUNKS
# =========================================================


def split_into_chunks(text):

    text = clean_text(text)

    if not text:
        return []

    if len(text) <= CHUNK_SIZE:

        return [text]

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + CHUNK_SIZE

        chunk = text[start:end]

        if end < text_length:

            last_break = max(
                chunk.rfind(". "),
                chunk.rfind("? "),
                chunk.rfind("! "),
                chunk.rfind(" "),
            )

            if last_break > (CHUNK_SIZE * 0.6):

                chunk = chunk[: last_break + 1]

                end = start + len(chunk)

        chunk = clean_text(chunk)

        if chunk:

            chunks.append(chunk)

        if end >= text_length:

            break

        start = max(
            end - CHUNK_OVERLAP,
            start + 1,
        )

    return chunks


# =========================================================
# READ NORMAL JSON FILE
# =========================================================


def read_json_file(file_path):

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if isinstance(data, list):

            for record in data:

                yield record

        elif isinstance(data, dict):

            yield data

    except Exception as error:

        print(
            "Error reading JSON:",
            file_path,
        )

        print(error)


# =========================================================
# READ JSONL FILE
# =========================================================


def read_jsonl_file(file_path):

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:

            for line_number, line in enumerate(
                file,
                start=1,
            ):

                line = line.strip()

                if not line:

                    continue

                try:

                    record = json.loads(line)

                    yield record

                except json.JSONDecodeError:

                    print(
                        "Skipping invalid JSONL line:",
                        line_number,
                    )

    except Exception as error:

        print(
            "Error reading JSONL:",
            file_path,
        )

        print(error)


# =========================================================
# GET RAW FILES
# =========================================================


def get_raw_files():

    if not os.path.exists(RAW_DIR):

        os.makedirs(
            RAW_DIR,
            exist_ok=True,
        )

        print("Raw knowledge folder created:")

        print(RAW_DIR)

        return []

    raw_files = []

    for file_name in sorted(os.listdir(RAW_DIR)):

        file_path = os.path.join(
            RAW_DIR,
            file_name,
        )

        if not os.path.isfile(file_path):

            continue

        if file_name.lower().endswith(".json") or file_name.lower().endswith(".jsonl"):

            raw_files.append(file_path)

    return raw_files


# =========================================================
# BUILD KNOWLEDGE
# =========================================================


def build_knowledge():

    raw_files = get_raw_files()

    if not raw_files:

        print("\nNo raw knowledge files found.")

        print("\nPut JSON or JSONL files inside:")

        print(RAW_DIR)

        return

    print("\n=================================")

    print("ENTITY KNOWLEDGE BUILD STARTED")

    print("=================================")

    print(
        "\nRaw files found:",
        len(raw_files),
    )

    final_knowledge = []

    knowledge_id = 1

    raw_record_count = 0

    # =============================================
    # PROCESS EVERY FILE
    # =============================================

    for file_path in raw_files:

        file_name = os.path.basename(file_path)

        print(
            "\nReading:",
            file_name,
        )

        if file_name.lower().endswith(".jsonl"):

            records = read_jsonl_file(file_path)

        else:

            records = read_json_file(file_path)

        # =========================================
        # PROCESS RECORDS
        # =========================================

        file_record_count = 0

        for record in records:

            raw_record_count += 1

            file_record_count += 1

            text = get_record_text(record)

            if not text:

                continue

            title = get_record_title(record)

            chunks = split_into_chunks(text)

            for chunk_number, chunk in enumerate(
                chunks,
                start=1,
            ):

                chunk_title = title

                if len(chunks) > 1:

                    chunk_title = f"{title} " f"Part {chunk_number}"

                final_knowledge.append(
                    {
                        "id": knowledge_id,
                        "title": chunk_title,
                        "content": chunk,
                    }
                )

                knowledge_id += 1

            if file_record_count % 1000 == 0:

                print(f"Processed " f"{file_name}: " f"{file_record_count} records")

        print(f"Finished {file_name}: " f"{file_record_count} records")

    # =================================================
    # SAVE FINAL KNOWLEDGE
    # =================================================

    print("\nSaving knowledge database...")

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            final_knowledge,
            file,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        )

    # =================================================
    # COMPLETE
    # =================================================

    print("\n=================================")

    print("ENTITY KNOWLEDGE BUILD COMPLETE")

    print("=================================")

    print(f"Raw records: " f"{raw_record_count}")

    print(f"Knowledge chunks: " f"{len(final_knowledge)}")

    print("\nOutput:")

    print(OUTPUT_FILE)


# =========================================================
# RUN
# =========================================================


if __name__ == "__main__":

    build_knowledge()
