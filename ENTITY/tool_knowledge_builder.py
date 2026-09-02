import os
import json

# =========================================================
# ENTITY TOOL KNOWLEDGE BUILDER
# JSONL -> TOOL EXAMPLES DATABASE
# =========================================================


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")

TOOLS_DIR = os.path.join(KNOWLEDGE_DIR, "tools")

OUTPUT_FILE = os.path.join(KNOWLEDGE_DIR, "tool_examples.json")


def clean_text(value):
    """Convert any value into clean text."""

    if value is None:
        return ""

    return str(value).strip()


def extract_messages(record):
    """Extract conversation messages safely."""

    messages = record.get("messages", [])

    if not isinstance(messages, list):
        return []

    clean_messages = []

    for message in messages:

        if not isinstance(message, dict):
            continue

        role = clean_text(message.get("role"))

        content = message.get("content")

        if isinstance(content, str):
            content = content.strip()

        if not role:
            continue

        clean_messages.append({"role": role, "content": content})

    return clean_messages


def extract_tools(record):
    """Extract available tool definitions."""

    tools = record.get("tools", [])

    if not isinstance(tools, list):
        return []

    return tools


def read_jsonl_file(file_path):

    records = []

    try:

        with open(file_path, "r", encoding="utf-8") as file:

            for line_number, line in enumerate(file, start=1):

                line = line.strip()

                if not line:
                    continue

                try:

                    record = json.loads(line)

                    if isinstance(record, dict):
                        records.append(record)

                except json.JSONDecodeError:

                    print(f"Skipping invalid line: " f"{line_number}")

    except Exception as error:

        print("\nError reading file:")
        print(file_path)
        print(error)

    return records


def load_tool_datasets():

    all_records = []

    if not os.path.exists(TOOLS_DIR):

        os.makedirs(TOOLS_DIR, exist_ok=True)

        print("Tools folder created:")
        print(TOOLS_DIR)

        return []

    for file_name in os.listdir(TOOLS_DIR):

        if not file_name.lower().endswith(".jsonl"):
            continue

        file_path = os.path.join(TOOLS_DIR, file_name)

        print("\nReading:")
        print(file_name)

        records = read_jsonl_file(file_path)

        print(f"Loaded {len(records)} records")

        all_records.extend(records)

    return all_records


def build_tool_examples():

    raw_records = load_tool_datasets()

    if not raw_records:

        print("\nNo tool dataset found.")

        print("\nPut .jsonl files inside:")
        print(TOOLS_DIR)

        return

    final_examples = []

    total_records = len(raw_records)

    print(f"\nProcessing " f"{total_records} tool records...")

    for record_number, record in enumerate(raw_records, start=1):

        messages = extract_messages(record)

        tools = extract_tools(record)

        if not messages:
            continue

        final_examples.append(
            {"id": record_number, "messages": messages, "tools": tools}
        )

        if record_number % 1000 == 0 or record_number == total_records:

            print(f"Processed: " f"{record_number}/" f"{total_records}")

    print("\nSaving tool examples database...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

        json.dump(final_examples, file, ensure_ascii=False, separators=(",", ":"))

    print("\n=================================")
    print("ENTITY TOOL BUILD COMPLETE")
    print("=================================")

    print(f"Raw records: " f"{total_records}")

    print(f"Tool examples: " f"{len(final_examples)}")

    print("\nOutput:")

    print(OUTPUT_FILE)


if __name__ == "__main__":

    build_tool_examples()
