from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    Response,
    stream_with_context,
)

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import re

try:
    from datasets import load_dataset
except Exception:
    load_dataset = None

# =========================================================
# ENTITY APP
# =========================================================

app = Flask(__name__)

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")


# =========================================================
# CONFIGURATION
# =========================================================

OLLAMA_URL = "http://127.0.0.1:11434"

DEFAULT_MODEL = "qwen3:4b"

AVAILABLE_MODELS = [
    "qwen3:1.7b",
    "qwen2.5:3b",
    "qwen3:4b",
]

WIKIPEDIA_URL = "https://en.wikipedia.org/w/api.php"


# Login Page


# =========================================================
# HOME / COWORK
# =========================================================


@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# PROJECTS
# =========================================================


@app.route("/projects")
def projects():
    return render_template("projects.html")


# =========================================================
# CUSTOMIZE
# =========================================================


@app.route("/customize")
def customize():
    return render_template("customize.html")


# =========================================================
# CODE
# =========================================================


@app.route("/code")
def code():
    return render_template("index.html")


# =========================================================
# HEALTH CHECK
# =========================================================


@app.route("/api/health")
def health():
    ollama_connected = False

    try:
        response = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=5,
        )

        ollama_connected = response.status_code == 200

    except requests.RequestException:
        ollama_connected = False

    return jsonify(
        {
            "status": "ok",
            "ollama": ollama_connected,
            "models": AVAILABLE_MODELS,
        }
    )


# =========================================================
# MODELS
# =========================================================


@app.route("/api/models")
def models():
    """
    Return models available to ENTITY.

    We keep the known local models as the frontend
    fallback, while also checking Ollama for the
    currently installed models.
    """

    installed_models = []

    try:
        response = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=5,
        )

        if response.ok:
            data = response.json()

            for model in data.get(
                "models",
                [],
            ):
                name = model.get("name")

                if name:
                    installed_models.append(name)

    except requests.RequestException:
        pass

    # Keep the known models first.
    final_models = []

    for model in AVAILABLE_MODELS:
        if model not in final_models:
            final_models.append(model)

    for model in installed_models:
        if model not in final_models:
            final_models.append(model)

    return jsonify(
        {
            "default": DEFAULT_MODEL,
            "models": final_models,
        }
    )


# =========================================================
# OLLAMA CHAT STREAM
# =========================================================


@app.route(
    "/api/chat",
    methods=["POST"],
)
def chat():

    data = request.get_json(silent=True) or {}

    message = (
        data.get(
            "message",
            "",
        )
        or ""
    ).strip()

    model = (
        data.get(
            "model",
            DEFAULT_MODEL,
        )
        or DEFAULT_MODEL
    ).strip()

    history = data.get(
        "history",
        [],
    )

    # -----------------------------------------------------
    # ENTITY EFFORT
    # -----------------------------------------------------
    effort = (
        data.get(
            "effort",
            "Medium",
        )
        or "Medium"
    ).strip()

    effort_options = {
        "Low": {
            "num_ctx": 2048,
            "temperature": 0.4,
        },
        "Medium": {
            "num_ctx": 4096,
            "temperature": 0.6,
        },
        "High": {
            "num_ctx": 8192,
            "temperature": 0.7,
        },
        "Max": {
            "num_ctx": 16384,
            "temperature": 0.8,
        },
    }

    ollama_options = effort_options.get(
        effort,
        effort_options["Medium"],
    )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not message:

        return jsonify({"error": "Message is empty."}), 400

    if not isinstance(
        history,
        list,
    ):

        history = []

    # -----------------------------------------------------
    # MODEL VALIDATION
    # -----------------------------------------------------

    if not model:

        model = DEFAULT_MODEL

    # -----------------------------------------------------
    # BUILD CONVERSATION
    # -----------------------------------------------------

    conversation_messages = []

    for item in history[-20:]:

        if not isinstance(
            item,
            dict,
        ):
            continue

        role = item.get("role")

        content = item.get("content")

        if role not in (
            "user",
            "assistant",
        ):
            continue

        if not isinstance(
            content,
            str,
        ):
            continue

        content = content.strip()

        if not content:
            continue

        conversation_messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    # -----------------------------------------------------
    # CURRENT USER MESSAGE
    # -----------------------------------------------------

    if not (
        conversation_messages
        and conversation_messages[-1]["role"] == "user"
        and conversation_messages[-1]["content"] == message
    ):

        conversation_messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

    # -----------------------------------------------------
    # OLLAMA STREAM
    # -----------------------------------------------------

    def generate():

        try:

            ollama_response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": model,
                    "messages": conversation_messages,
                    "stream": True,
                    "options": ollama_options,
                },
                stream=True,
                timeout=300,
            )

            # -----------------------------------------
            # HTTP ERROR
            # -----------------------------------------

            if not ollama_response.ok:

                error_text = ollama_response.text or "Ollama request failed."

                yield ("\n[ENTITY ERROR] " + error_text)

                return

            # -----------------------------------------
            # STREAM CHUNKS
            # -----------------------------------------

            for line in ollama_response.iter_lines(decode_unicode=True):

                if not line:
                    continue

                try:

                    chunk = json.loads(line)

                except json.JSONDecodeError:

                    continue

                content = chunk.get(
                    "message",
                    {},
                ).get(
                    "content",
                    "",
                )

                if content:

                    yield content

                if chunk.get("done"):

                    break

        except requests.exceptions.ConnectionError:

            yield ("\n[ENTITY ERROR] " "Ollama is not running.")

        except requests.exceptions.Timeout:

            yield ("\n[ENTITY ERROR] " "Ollama timed out.")

        except requests.exceptions.RequestException as error:

            yield ("\n[ENTITY ERROR] " f"{error}")

        except Exception as error:

            yield ("\n[ENTITY ERROR] " f"{error}")

    return Response(
        stream_with_context(generate()),
        content_type=("text/plain; " "charset=utf-8"),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
            "X-Entity-Model": model,
            "X-Entity-Effort": effort,
        },
    )


# =========================================================
# DUCKDUCKGO INSTANT ANSWER
# =========================================================

DUCKDUCKGO_URL = "https://api.duckduckgo.com/"


@app.route(
    "/api/duckduckgo",
    methods=["GET"],
)
def duckduckgo():

    query = (
        request.args.get(
            "q",
            "",
        )
        or ""
    ).strip()

    if not query:
        return jsonify({"error": "Search query is empty."}), 400

    try:

        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "no_redirect": 1,
            "skip_disambig": 0,
        }

        response = requests.get(
            DUCKDUCKGO_URL,
            params=params,
            timeout=15,
            headers={"User-Agent": "Entity AI Assistant/1.0"},
        )

        response.raise_for_status()

        data = response.json()

        related_topics = []

        for item in data.get(
            "RelatedTopics",
            [],
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            text = item.get(
                "Text",
                "",
            )

            first_url = item.get(
                "FirstURL",
                "",
            )

            if text:

                related_topics.append(
                    {
                        "text": text,
                        "url": first_url,
                    }
                )

        return jsonify(
            {
                "query": query,
                "heading": data.get(
                    "Heading",
                    "",
                ),
                "abstract": data.get(
                    "AbstractText",
                    "",
                ),
                "abstract_source": data.get(
                    "AbstractSource",
                    "",
                ),
                "abstract_url": data.get(
                    "AbstractURL",
                    "",
                ),
                "image": data.get(
                    "Image",
                    "",
                ),
                "answer": data.get(
                    "Answer",
                    "",
                ),
                "answer_type": data.get(
                    "AnswerType",
                    "",
                ),
                "related_topics": related_topics[:10],
            }
        )

    except requests.RequestException as error:

        return jsonify({"error": f"DuckDuckGo request failed: {error}"}), 502

    except Exception as error:

        return jsonify({"error": str(error)}), 500


# =========================================================
# WIKIPEDIA SEARCH
# =========================================================


@app.route(
    "/api/wikipedia",
    methods=["GET"],
)
def wikipedia():

    query = (
        request.args.get(
            "q",
            "",
        )
        or ""
    ).strip()

    if not query:

        return jsonify({"error": "Search query is empty."}), 400

    try:

        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "list": "search",
            "srsearch": query,
            "srlimit": 5,
            "utf8": 1,
        }

        response = requests.get(
            WIKIPEDIA_URL,
            params=params,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get("query", {}).get("search", []):

            title = item.get(
                "title",
                "",
            )

            snippet = item.get(
                "snippet",
                "",
            )

            results.append(
                {
                    "title": title,
                    "snippet": snippet,
                    "url": (
                        "https://en.wikipedia.org/wiki/"
                        + title.replace(
                            " ",
                            "_",
                        )
                    ),
                }
            )

        return jsonify(
            {
                "query": query,
                "results": results,
            }
        )

    except requests.RequestException as error:

        return jsonify({"error": f"Wikipedia request failed: {error}"}), 502

    except Exception as error:

        return jsonify({"error": str(error)}), 500


# =========================================================
# WIKIPEDIA PAGE SUMMARY
# =========================================================


@app.route(
    "/api/wikipedia/summary",
    methods=["GET"],
)
def wikipedia_summary():

    title = (
        request.args.get(
            "title",
            "",
        )
        or ""
    ).strip()

    if not title:

        return jsonify({"error": "Wikipedia title is empty."}), 400

    try:

        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "prop": "extracts|info",
            "exintro": 1,
            "explaintext": 1,
            "inprop": "url",
            "titles": title,
        }

        response = requests.get(
            WIKIPEDIA_URL,
            params=params,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        pages = data.get("query", {}).get("pages", [])

        if not pages:

            return jsonify({"error": "Wikipedia page not found."}), 404

        page = pages[0]

        return jsonify(
            {
                "title": page.get(
                    "title",
                    title,
                ),
                "extract": page.get(
                    "extract",
                    "",
                ),
                "url": page.get(
                    "fullurl",
                    "",
                ),
            }
        )

    except requests.RequestException as error:

        return jsonify({"error": f"Wikipedia request failed: {error}"}), 502

    except Exception as error:

        return jsonify({"error": str(error)}), 500


# =========================================================
# PROJECT API
# =========================================================


@app.route(
    "/api/projects",
    methods=["GET"],
)
def get_projects():

    # Temporary in-memory project store.
    # Persistent storage can be added later without
    # changing the frontend API.

    return jsonify({"projects": []})


@app.route(
    "/api/projects",
    methods=["POST"],
)
def create_project():

    data = request.get_json(silent=True) or {}

    name = (
        data.get(
            "name",
            "",
        )
        or ""
    ).strip()

    description = (
        data.get(
            "description",
            "",
        )
        or ""
    ).strip()

    if not name:

        return jsonify({"error": "Project name is required."}), 400

    project = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "name": name,
        "description": description,
        "created_at": datetime.now().isoformat(),
    }

    return jsonify({"project": project}), 201


# =========================================================
# ENTITY HOME / LOGIN PAGE
# =========================================================


@app.route("/")
def home_page():
    return render_template("index.html")


# =========================================================
# FALLBACK
# =========================================================


@app.errorhandler(404)
def not_found(error):

    return jsonify({"error": "ENTITY route not found."}), 404


@app.errorhandler(500)
def internal_error(error):

    return jsonify({"error": "ENTITY internal server error."}), 500


# =========================================================
# ENTITY CHAT PAGE
# =========================================================


@app.route("/chat")
def chat_page():
    return render_template("index2.html")


# =========================================================
# ENTITY SMART WEB ROUTER
# DUCKDUCKGO -> OLLAMA
# =========================================================


def entity_should_search_web(message):
    """
    Decide whether the current question should use
    DuckDuckGo before Ollama.
    """

    text = (message or "").strip().lower()

    if not text:
        return False

    web_keywords = [
        "latest",
        "today",
        "current",
        "recent",
        "news",
        "search",
        "google",
        "internet",
        "web",
        "online",
        "find",
        "who is",
        "what is",
        "what are",
        "when is",
        "where is",
        "how much",
        "price",
        "cost",
        "release",
        "released",
        "version",
        "update",
        "updates",
        "2026",
    ]

    return any(keyword in text for keyword in web_keywords)


def entity_duckduckgo_search(query):
    """Get useful context from DuckDuckGo Instant Answer API."""

    def perform_search(search_query):
        try:
            response = requests.get(
                DUCKDUCKGO_URL,
                params={
                    "q": search_query,
                    "format": "json",
                    "no_html": 1,
                    "no_redirect": 1,
                    "skip_disambig": 0,
                },
                headers={"User-Agent": "Entity AI Assistant/1.0"},
                timeout=20,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            print("ENTITY DuckDuckGo request error:", error)
            return None
        except ValueError as error:
            print("ENTITY DuckDuckGo JSON error:", error)
            return None

    def build_context(data):
        if not isinstance(data, dict):
            return ""

        parts = []

        answer = (data.get("Answer", "") or "").strip()
        if answer:
            parts.append("Direct Answer:\n" + answer)

        heading = (data.get("Heading", "") or "").strip()
        abstract = (data.get("AbstractText", "") or "").strip()
        source = (data.get("AbstractSource", "") or "").strip()
        source_url = (data.get("AbstractURL", "") or "").strip()

        if abstract:
            parts.append((heading or "Topic") + ":\n" + abstract)
            if source:
                parts.append("Source: " + source)
            if source_url:
                parts.append("Source URL: " + source_url)

        count = 0
        for item in data.get("RelatedTopics", []):
            if count >= 8 or not isinstance(item, dict):
                continue

            nested = item.get("Topics")
            items = nested if isinstance(nested, list) else [item]

            for result_item in items:
                if count >= 8 or not isinstance(result_item, dict):
                    break

                result_text = (result_item.get("Text", "") or "").strip()
                result_url = (result_item.get("FirstURL", "") or "").strip()

                if not result_text:
                    continue

                result = "Related Result: " + result_text
                if result_url:
                    result += "\nURL: " + result_url

                parts.append(result)
                count += 1

        return "\n\n".join(parts).strip()

    query = (query or "").strip()
    if not query:
        return ""

    print("ENTITY DuckDuckGo query:", query)

    data = perform_search(query)
    context = build_context(data) if data else ""

    if context:
        print(f"ENTITY DuckDuckGo returned {len(context)} characters.")
        return context

    simplified = re.sub(
        r"^(what is|what are|who is|who are|tell me about|explain)\s+",
        "",
        query,
        flags=re.IGNORECASE,
    ).strip(" ?.!")

    if simplified and simplified.lower() != query.lower().strip(" ?.!"):
        print("ENTITY DuckDuckGo simplified query:", simplified)
        data = perform_search(simplified)
        context = build_context(data) if data else ""
        if context:
            print(
                "ENTITY DuckDuckGo returned "
                f"{len(context)} characters from simplified query."
            )
            return context

    print("ENTITY DuckDuckGo returned no useful context.")
    return ""


# =========================================================
# REPLACE CHAT VIEW WITH SMART ROUTER
# =========================================================

_entity_original_chat = app.view_functions.get("chat")


def entity_smart_chat():
    data = request.get_json(silent=True) or {}

    message = (data.get("message", "") or "").strip()

    model = (data.get("model", DEFAULT_MODEL) or DEFAULT_MODEL).strip()

    history = data.get("history", [])

    effort = (data.get("effort", "Medium") or "Medium").strip()

    effort_options = {
        "Low": {"num_ctx": 2048, "temperature": 0.4},
        "Medium": {"num_ctx": 4096, "temperature": 0.6},
        "High": {"num_ctx": 8192, "temperature": 0.7},
        "Max": {"num_ctx": 16384, "temperature": 0.8},
    }

    ollama_options = effort_options.get(
        effort,
        effort_options["Medium"],
    )

    if not message:
        return jsonify({"error": "Message is empty."}), 400

    if not isinstance(history, list):
        history = []

    if not model:
        model = DEFAULT_MODEL

    if not entity_should_search_web(message):
        return _entity_original_chat()

    print("ENTITY Web search:", message)
    web_context = entity_duckduckgo_search(message)

    if not web_context:
        print("ENTITY Web search returned no useful data.")
        return _entity_original_chat()

    conversation_messages = [
        {
            "role": "system",
            "content": (
                "You are Entity, a helpful AI assistant.\n\n"
                "Fresh information was retrieved from DuckDuckGo "
                "for the user's current question.\n\n"
                "Use the retrieved information when relevant. "
                "Answer naturally and directly. "
                "Do not mention the internal web-search process "
                "unless the user asks about it. "
                "Do not invent facts that are not supported by "
                "the retrieved information.\n\n"
                "WEB INFORMATION:\n" + web_context
            ),
        }
    ]

    for item in history[-20:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in ("user", "assistant"):
            continue
        if not isinstance(content, str):
            continue
        content = content.strip()
        if not content:
            continue
        conversation_messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    if not (
        conversation_messages
        and conversation_messages[-1].get("role") == "user"
        and conversation_messages[-1].get("content") == message
    ):
        conversation_messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

    def generate():
        try:
            ollama_response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": model,
                    "messages": conversation_messages,
                    "stream": True,
                    "options": ollama_options,
                },
                stream=True,
                timeout=300,
            )

            if not ollama_response.ok:
                yield (
                    "\n[ENTITY ERROR] "
                    + (ollama_response.text or "Ollama request failed.")
                )
                return

            for line in ollama_response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue

                content = chunk.get("message", {}).get("content", "")

                if content:
                    yield content

                if chunk.get("done"):
                    break

        except requests.exceptions.ConnectionError:
            yield "\n[ENTITY ERROR] Ollama is not running."
        except requests.exceptions.Timeout:
            yield "\n[ENTITY ERROR] Ollama timed out."
        except requests.RequestException as error:
            yield "\n[ENTITY ERROR] " + str(error)
        except Exception as error:
            yield "\n[ENTITY ERROR] " + str(error)

    return Response(
        stream_with_context(generate()),
        content_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
            "X-Entity-Model": model,
            "X-Entity-Effort": effort,
            "X-Entity-Web-Search": "duckduckgo",
        },
    )


# =========================================================
# ENTITY OPEN-METEO WEATHER
# =========================================================

OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

OPEN_METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def entity_is_weather_question(message):
    """
    Detect weather-related questions.
    """

    text = (message or "").strip().lower()

    weather_words = [
        "weather",
        "temperature",
        "temp",
        "forecast",
        "humidity",
        "rain",
        "raining",
        "wind",
        "climate",
        "mausam",
        "baarish",
        "barish",
        "garmi",
        "thand",
        "tapman",
        "temperature kitna",
        "mausam kaisa",
    ]

    return any(word in text for word in weather_words)


def entity_extract_weather_city(message):
    """
    Extract a city from natural-language weather questions.
    """

    text = (message or "").strip()
    if not text:
        return ""

    stop_words = {
        "batao",
        "bata",
        "batana",
        "please",
        "plz",
        "weather",
        "mausam",
        "temperature",
        "temp",
        "forecast",
        "humidity",
        "rain",
        "raining",
        "wind",
        "climate",
        "baarish",
        "barish",
        "garmi",
        "thand",
        "tapman",
        "aaj",
        "abhi",
        "today",
        "now",
        "current",
        "kya",
        "hai",
        "hain",
        "mujhe",
        "mein",
        "me",
        "par",
        "pe",
        "ka",
        "ki",
        "ke",
    }

    def clean_city(value):
        value = (value or "").strip(" .,!?;:'\"")

        value = re.sub(
            r"\s+(?:batao|bata|batana|please|plz|abhi|aaj|" r"today|now|kya|hai|hain)$",
            "",
            value,
            flags=re.IGNORECASE,
        ).strip(" .,!?;:'\"")

        value = re.sub(
            r"\s+(?:ka|ki|ke|mein|me|par|pe)$",
            "",
            value,
            flags=re.IGNORECASE,
        ).strip(" .,!?;:'\"")

        words = []
        for word in value.split():
            clean_word = word.strip(" .,!?;:'\"").lower()
            if clean_word and clean_word not in stop_words:
                words.append(word.strip(" .,!?;:'\""))

        return " ".join(words).strip()

    patterns = [
        # Delhi ka weather batao
        r"^\s*(.+?)\s+(?:ka|ki|ke)\s+"
        r"(?:weather|mausam|temperature|temp|forecast)"
        r"(?:\s+.*)?$",
        # Delhi mein weather batao
        r"^\s*(.+?)\s+(?:mein|me)\s+"
        r"(?:weather|mausam|temperature|temp|forecast)"
        r"(?:\s+.*)?$",
        # weather in Delhi / temperature of Mumbai
        r"(?:weather|temperature|temp|forecast|mausam)"
        r"\s+(?:of|in|at|for)\s+(.+?)"
        r"(?:\s+(?:ka|ki|ke)\s+.*)?$",
        # Delhi weather / Mumbai temperature
        r"^\s*(.+?)\s+" r"(?:weather|mausam|temperature|temp|forecast)" r"(?:\s+.*)?$",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
        if match:
            city = clean_city(match.group(1))
            if city:
                return city

    # Safe fallback for phrases such as:
    # "what is the weather in Delhi today?"
    fallback = re.sub(
        r"\b(?:what|is|the|weather|temperature|temp|forecast|"
        r"humidity|rain|raining|wind|climate|mausam|baarish|"
        r"barish|garmi|thand|tapman|batao|bata|batana|please|"
        r"plz|today|aaj|abhi|now|current|kya|hai|hain|mujhe|"
        r"mein|me|ka|ki|ke|par|pe|of|in|at|for)\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    city = clean_city(re.sub(r"\s+", " ", fallback).strip())

    return city


def entity_get_weather(city):
    """
    Resolve city -> coordinates -> current weather.
    """

    try:

        # -----------------------------------------
        # CITY -> LATITUDE / LONGITUDE
        # -----------------------------------------

        geo_response = requests.get(
            OPEN_METEO_GEOCODING_URL,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            headers={"User-Agent": "Entity AI Assistant/1.0"},
            timeout=15,
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        results = (
            geo_data.get(
                "results",
                [],
            )
            or []
        )

        if not results:
            print(
                "ENTITY Weather: city not found:",
                city,
            )

            return None

        location = results[0]

        latitude = location.get("latitude")

        longitude = location.get("longitude")

        location_name = (
            location.get(
                "name",
                city,
            )
            or city
        )

        country = (
            location.get(
                "country",
                "",
            )
            or ""
        )

        timezone = (
            location.get(
                "timezone",
                "",
            )
            or ""
        )

        if latitude is None or longitude is None:

            return None

        # -----------------------------------------
        # CURRENT WEATHER
        # -----------------------------------------

        weather_response = requests.get(
            OPEN_METEO_WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": (timezone or "auto"),
            },
            headers={"User-Agent": "Entity AI Assistant/1.0"},
            timeout=15,
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        current = (
            weather_data.get(
                "current",
                {},
            )
            or {}
        )

        units = (
            weather_data.get(
                "current_units",
                {},
            )
            or {}
        )

        if not current:
            return None

        weather_code = current.get("weather_code")

        # -----------------------------------------
        # WEATHER CODE -> HUMAN TEXT
        # -----------------------------------------

        weather_descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snowfall",
            73: "Moderate snowfall",
            75: "Heavy snowfall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail",
        }

        weather_description = weather_descriptions.get(
            weather_code,
            "Unknown weather conditions",
        )

        return {
            "city": location_name,
            "country": country,
            "timezone": timezone,
            "temperature": current.get("temperature_2m"),
            "temperature_unit": units.get(
                "temperature_2m",
                "°C",
            ),
            "humidity": current.get("relative_humidity_2m"),
            "humidity_unit": units.get(
                "relative_humidity_2m",
                "%",
            ),
            "apparent_temperature": current.get("apparent_temperature"),
            "apparent_temperature_unit": units.get(
                "apparent_temperature",
                "°C",
            ),
            "wind_speed": current.get("wind_speed_10m"),
            "wind_speed_unit": units.get(
                "wind_speed_10m",
                "km/h",
            ),
            "weather_code": weather_code,
            "description": weather_description,
            "time": current.get(
                "time",
                "",
            ),
        }

    except requests.RequestException as error:

        print(
            "ENTITY Weather request error:",
            error,
        )

        return None

    except Exception as error:

        print(
            "ENTITY Weather error:",
            error,
        )

        return None


# =========================================================
# WEATHER API TEST ENDPOINT
# =========================================================


@app.route(
    "/api/weather",
    methods=["GET"],
)
def entity_weather_api():

    city = (
        request.args.get(
            "city",
            "",
        )
        or ""
    ).strip()

    if not city:

        return jsonify({"error": "City is required."}), 400

    weather = entity_get_weather(city)

    if not weather:

        return jsonify({"error": f"Weather not found for {city}."}), 404

    return jsonify(weather)


# =========================================================
# WEATHER -> OLLAMA
# =========================================================


def entity_weather_ollama_response(
    message,
    weather,
    model,
    history,
    effort,
):
    """
    Send live Open-Meteo data to Ollama and
    return the normal Entity streaming response.
    """

    effort_options = {
        "Low": {
            "num_ctx": 2048,
            "temperature": 0.4,
        },
        "Medium": {
            "num_ctx": 4096,
            "temperature": 0.6,
        },
        "High": {
            "num_ctx": 8192,
            "temperature": 0.7,
        },
        "Max": {
            "num_ctx": 16384,
            "temperature": 0.8,
        },
    }

    ollama_options = effort_options.get(
        effort,
        effort_options["Medium"],
    )

    weather_context = f"""
LIVE WEATHER DATA

Location:
{weather["city"]}, {weather["country"]}

Temperature:
{weather["temperature"]}{weather["temperature_unit"]}

Feels like:
{weather["apparent_temperature"]}{weather["apparent_temperature_unit"]}

Humidity:
{weather["humidity"]}{weather["humidity_unit"]}

Wind:
{weather["wind_speed"]}{weather["wind_speed_unit"]}

Condition:
{weather["description"]}

Weather time:
{weather["time"]}

Timezone:
{weather["timezone"]}
"""

    messages = [
        {
            "role": "system",
            "content": (
                "You are Entity, a helpful AI assistant.\n\n"
                "The user is asking about weather.\n"
                "Use the LIVE WEATHER DATA below to answer.\n"
                "Do not invent weather values.\n"
                "Answer naturally and concisely.\n"
                "If the user asks for weather, include "
                "the important current values.\n\n" + weather_context
            ),
        }
    ]

    if isinstance(
        history,
        list,
    ):

        for item in history[-20:]:

            if not isinstance(
                item,
                dict,
            ):
                continue

            role = item.get("role")

            content = item.get("content")

            if role not in (
                "user",
                "assistant",
            ):
                continue

            if not isinstance(
                content,
                str,
            ):
                continue

            content = content.strip()

            if not content:
                continue

            messages.append(
                {
                    "role": role,
                    "content": content,
                }
            )

    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    def generate():

        try:

            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    "options": ollama_options,
                },
                stream=True,
                timeout=300,
            )

            if not response.ok:
                yield (
                    "\n[ENTITY ERROR] " + (response.text or "Ollama request failed.")
                )
                return

            for line in response.iter_lines(decode_unicode=True):

                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue

                content = chunk.get(
                    "message",
                    {},
                ).get(
                    "content",
                    "",
                )

                if content:
                    yield content

                if chunk.get("done"):
                    break

        except requests.exceptions.ConnectionError:
            yield ("\n[ENTITY ERROR] " "Ollama is not running.")

        except requests.exceptions.Timeout:
            yield ("\n[ENTITY ERROR] " "Ollama timed out.")

        except requests.RequestException as error:
            yield ("\n[ENTITY ERROR] " + str(error))

        except Exception as error:
            yield ("\n[ENTITY ERROR] " + str(error))

    return Response(
        stream_with_context(generate()),
        content_type=("text/plain; charset=utf-8"),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
            "X-Entity-Model": model,
            "X-Entity-Effort": effort,
            "X-Entity-Weather": "open-meteo",
        },
    )


# =========================================================
# ENTITY CURRENCY API
# =========================================================

FRANKFURTER_URL = "https://api.frankfurter.app/latest"


def entity_is_currency_question(message):

    text = (message or "").strip().lower()

    currency_words = [
        "currency",
        "convert",
        "conversion",
        "exchange rate",
        "exchange",
        "usd",
        "inr",
        "eur",
        "gbp",
        "jpy",
        "cad",
        "aud",
        "chf",
        "dollar",
        "dollars",
        "rupee",
        "rupees",
        "euro",
        "euros",
        "pound",
        "pounds",
        "yen",
        "dirham",
        "aed",
        "qar",
        "sar",
        "₹",
        "$",
        "€",
        "£",
    ]

    return any(word in text for word in currency_words)


def entity_extract_currency_query(message):

    text = (message or "").strip()

    patterns = [
        r"^\s*"
        r"([0-9]+(?:\.[0-9]+)?)"
        r"\s*"
        r"([A-Za-z]{3})"
        r"\s*(?:to|in)\s*"
        r"([A-Za-z]{3})"
        r"\s*$",
        r"^\s*"
        r"([0-9]+(?:\.[0-9]+)?)"
        r"\s*"
        r"([A-Za-z]+)"
        r"\s*(?:to|in)\s*"
        r"([A-Za-z]+)"
        r"\s*$",
        r"^\s*"
        r"([0-9]+(?:\.[0-9]+)?)"
        r"\s*"
        r"([A-Za-z]{3})"
        r"\s*(?:ka|ki|ke)\s+"
        r"(?:rate|value)"
        r"\s*(?:in|me)\s*"
        r"([A-Za-z]{3})"
        r"\s*$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:

            amount = match.group(1)
            from_currency = match.group(2)
            to_currency = match.group(3)

            return (
                amount,
                from_currency,
                to_currency,
            )

    return None


def entity_normalize_currency(code):

    currency_map = {
        "dollar": "USD",
        "dollars": "USD",
        "usd": "USD",
        "rupee": "INR",
        "rupees": "INR",
        "inr": "INR",
        "euro": "EUR",
        "euros": "EUR",
        "eur": "EUR",
        "pound": "GBP",
        "pounds": "GBP",
        "gbp": "GBP",
        "yen": "JPY",
        "jpy": "JPY",
        "cad": "CAD",
        "aud": "AUD",
        "chf": "CHF",
        "aed": "AED",
        "qar": "QAR",
        "sar": "SAR",
    }

    return currency_map.get(
        code.strip().lower(),
        code.strip().upper(),
    )


def entity_get_currency_rate(
    amount,
    from_currency,
    to_currency,
):

    from_currency = entity_normalize_currency(from_currency)

    to_currency = entity_normalize_currency(to_currency)

    try:

        response = requests.get(
            FRANKFURTER_URL,
            params={
                "amount": amount,
                "from": from_currency,
                "to": to_currency,
            },
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        rates = (
            data.get(
                "rates",
                {},
            )
            or {}
        )

        if to_currency not in rates:
            return None

        return {
            "amount": amount,
            "from": from_currency,
            "to": to_currency,
            "result": rates[to_currency],
            "date": data.get(
                "date",
                "",
            ),
        }

    except requests.RequestException as error:

        print(
            "ENTITY Currency error:",
            error,
        )

        return None


@app.route(
    "/api/currency",
    methods=["GET"],
)
def entity_currency_api():

    amount = request.args.get(
        "amount",
        "",
    ).strip()

    from_currency = request.args.get(
        "from",
        "",
    ).strip()

    to_currency = request.args.get(
        "to",
        "",
    ).strip()

    if not amount or not from_currency or not to_currency:

        return jsonify({"error": ("amount, from and to " "are required.")}), 400

    try:

        amount_value = float(amount)

    except ValueError:

        return jsonify({"error": ("Invalid amount.")}), 400

    result = entity_get_currency_rate(
        amount_value,
        from_currency,
        to_currency,
    )

    if not result:

        return jsonify({"error": ("Currency conversion " "failed.")}), 502

    return jsonify(result)


# =========================================================
# CURRENCY DIRECT CHAT ROUTER
# =========================================================


def entity_currency_router():

    data = request.get_json(silent=True) or {}

    message = (
        data.get(
            "message",
            "",
        )
        or ""
    ).strip()

    if not entity_is_currency_question(message):

        return entity_smart_chat()

    query = entity_extract_currency_query(message)

    if not query:

        return entity_smart_chat()

    amount_text, from_currency, to_currency = query

    try:

        amount = float(amount_text)

    except ValueError:

        return entity_smart_chat()

    result = entity_get_currency_rate(
        amount,
        from_currency,
        to_currency,
    )

    if not result:

        return Response(
            ("Currency conversion " "failed."),
            content_type=("text/plain; charset=utf-8"),
        )

    converted = result.get("result")

    if converted is None:

        return Response(
            ("Currency conversion " "failed."),
            content_type=("text/plain; charset=utf-8"),
        )

    if float(converted).is_integer():

        converted_text = f"{int(converted):,}"

    else:

        converted_text = f"{converted:,.4f}".rstrip("0").rstrip(".")

    answer = (
        "💱 Currency Conversion\n\n"
        f"{amount_text} "
        f"{result['from']} = "
        f"{converted_text} "
        f"{result['to']}"
    )

    if result.get("date"):

        answer += "\nRate date: " + result["date"]

    return Response(
        answer,
        content_type=("text/plain; charset=utf-8"),
        headers={
            "Cache-Control": "no-cache",
            "X-Entity-Currency": "frankfurter",
            "X-Entity-Accurate": "true",
        },
    )


# =========================================================
# ACTIVATE CURRENCY ROUTER
# =========================================================

app.view_functions["chat"] = entity_currency_router


print("Entity Frankfurter Currency " "loaded successfully.")


# =========================================================
# ENTITY WIKIPEDIA API
# =========================================================

WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"

WIKIPEDIA_SEARCH_URL = "https://en.wikipedia.org/w/api.php"


def entity_is_wikipedia_question(message):

    text = (message or "").strip().lower()

    wikipedia_phrases = [
        "who is",
        "who was",
        "what is",
        "what was",
        "tell me about",
        "explain",
        "history of",
        "biography of",
        "information about",
        "about",
    ]

    return any(phrase in text for phrase in wikipedia_phrases)


def entity_extract_wikipedia_topic(message):

    text = (message or "").strip()

    patterns = [
        r"^\s*who\s+is\s+",
        r"^\s*who\s+was\s+",
        r"^\s*what\s+is\s+",
        r"^\s*what\s+was\s+",
        r"^\s*tell\s+me\s+about\s+",
        r"^\s*explain\s+",
        r"^\s*history\s+of\s+",
        r"^\s*biography\s+of\s+",
        r"^\s*information\s+about\s+",
        r"^\s*about\s+",
    ]

    for pattern in patterns:

        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE,
        )

    text = re.sub(
        r"[?.!,]+$",
        "",
        text,
    ).strip()

    # =====================================================
    # WIKIPEDIA TOPIC NORMALIZATION
    # =====================================================

    normalized_topic = text.strip().lower()

    if normalized_topic in (
        "python",
        "python language",
        "python programming",
        "python programming language",
    ):

        return "Python programming language"

    return text


def entity_get_wikipedia(topic):

    if not topic:
        return None

    try:

        page_name = re.sub(
            r"\s+",
            "_",
            topic.strip(),
        )

        url = WIKIPEDIA_API_URL + requests.utils.quote(page_name)

        response = requests.get(
            url,
            headers={"User-Agent": "Entity AI Assistant/1.0"},
            timeout=15,
        )

        if response.status_code == 404:

            return None

        response.raise_for_status()

        data = response.json()

        if not data:
            return None

        return {
            "title": data.get(
                "title",
                topic,
            ),
            "description": data.get(
                "description",
                "",
            ),
            "extract": data.get(
                "extract",
                "",
            ),
            "url": data.get(
                "content_urls",
                {},
            )
            .get(
                "desktop",
                {},
            )
            .get(
                "page",
                "",
            ),
            "thumbnail": data.get(
                "thumbnail",
                {},
            ).get(
                "source",
                "",
            ),
        }

    except requests.RequestException as error:

        print(
            "ENTITY Wikipedia error:",
            error,
        )

        return None

    except Exception as error:

        print(
            "ENTITY Wikipedia parse error:",
            error,
        )

        return None


def entity_wikipedia_direct_chat():

    data = request.get_json(silent=True) or {}

    message = (
        data.get(
            "message",
            "",
        )
        or ""
    ).strip()

    if not entity_is_wikipedia_question(message):

        return entity_currency_router()

    topic = entity_extract_wikipedia_topic(message)

    if not topic:

        return entity_currency_router()

    wikipedia_data = entity_get_wikipedia(topic)

    if not wikipedia_data:

        return entity_currency_router()

    title = (
        wikipedia_data.get(
            "title",
            topic,
        )
        or topic
    )

    description = (
        wikipedia_data.get(
            "description",
            "",
        )
        or ""
    )

    extract = (
        wikipedia_data.get(
            "extract",
            "",
        )
        or ""
    )

    page_url = (
        wikipedia_data.get(
            "url",
            "",
        )
        or ""
    )

    thumbnail = (
        wikipedia_data.get(
            "thumbnail",
            "",
        )
        or ""
    )

    answer_parts = [
        f"📚 {title}",
    ]

    if description:

        answer_parts.append(description)

    if extract:

        answer_parts.append(extract)

    if page_url:

        answer_parts.append("Source: " + page_url)

    answer = "\n\n".join(answer_parts)

    return Response(
        answer,
        content_type=("text/plain; charset=utf-8"),
        headers={
            "Cache-Control": "no-cache",
            "X-Entity-Source": "Wikipedia",
        },
    )


# =========================================================
# ACTIVATE WIKIPEDIA ROUTER
# =========================================================

app.view_functions["chat"] = entity_wikipedia_direct_chat


print("Entity Wikipedia API " "loaded successfully.")


# =========================================================
# ENTITY NEWS API
# =========================================================

NEWSDATA_URL = "https://newsdata.io/api/1/latest"

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")


def entity_is_news_question(message):

    text = (message or "").strip().lower()

    news_phrases = [
        "latest news",
        "today news",
        "news today",
        "latest news about",
        "news about",
        "current news",
        "recent news",
        "breaking news",
        "what happened today",
        "what happened",
        "headlines",
        "news",
        "khabar",
        "khabrein",
        "taaza khabar",
        "aaj ki khabar",
        "aaj ki news",
    ]

    return any(phrase in text for phrase in news_phrases)


def entity_extract_news_query(message):

    text = (message or "").strip()

    patterns = [
        r"^\s*latest\s+news\s+about\s+(.+)$",
        r"^\s*news\s+about\s+(.+)$",
        r"^\s*news\s+on\s+(.+)$",
        r"^\s*current\s+news\s+about\s+(.+)$",
        r"^\s*recent\s+news\s+about\s+(.+)$",
        r"^\s*breaking\s+news\s+about\s+(.+)$",
        r"^\s*latest\s+(.+?)\s+news$",
        r"^\s*(.+?)\s+news$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:

            query = match.group(1).strip()

            if query:
                return query

    return text


def entity_detect_news_category(message):

    text = (message or "").strip().lower()

    if any(
        word in text
        for word in [
            "sport",
            "sports",
            "cricket",
            "football",
            "tennis",
            "ipl",
        ]
    ):

        return "sports"

    if any(
        word in text
        for word in [
            "business",
            "stock",
            "market",
            "economy",
            "finance",
        ]
    ):

        return "business"

    if any(
        word in text
        for word in [
            "tech",
            "technology",
            "ai",
            "artificial intelligence",
            "software",
            "computer",
        ]
    ):

        return "technology"

    if any(
        word in text
        for word in [
            "entertainment",
            "movie",
            "movies",
            "film",
            "bollywood",
            "hollywood",
        ]
    ):

        return "entertainment"

    if any(
        word in text
        for word in [
            "health",
            "medical",
            "medicine",
        ]
    ):

        return "health"

    return ""


def entity_get_news(
    query,
    category="",
):

    if not NEWSDATA_API_KEY:

        print("ENTITY NewsData API key " "is not configured.")

        return []

    params = {
        "apikey": NEWSDATA_API_KEY,
        "q": query,
        "language": "en",
    }

    if category:
        params["category"] = category

    try:

        response = requests.get(
            NEWSDATA_URL,
            params=params,
            headers={"User-Agent": "Entity AI Assistant/1.0"},
            timeout=20,
        )

        response.raise_for_status()

        data = response.json()

        return (
            data.get(
                "results",
                [],
            )
            or []
        )

    except requests.RequestException as error:

        print(
            "ENTITY NewsData error:",
            error,
        )

        return []

    except Exception as error:

        print(
            "ENTITY NewsData parse error:",
            error,
        )

        return []


def entity_news_direct_chat():

    data = request.get_json(silent=True) or {}

    message = (
        data.get(
            "message",
            "",
        )
        or ""
    ).strip()

    if not entity_is_news_question(message):

        return entity_wikipedia_direct_chat()

    query = entity_extract_news_query(message)

    category = entity_detect_news_category(message)

    print(
        "ENTITY News query:",
        query,
    )

    print(
        "ENTITY News category:",
        category,
    )

    articles = entity_get_news(
        query=query,
        category=category,
    )

    if not articles:

        return Response(
            ("Abhi is topic ki news " "available nahi mili."),
            content_type=("text/plain; charset=utf-8"),
        )

    answer_lines = [
        "📰 Latest News",
        "",
    ]

    for index, article in enumerate(
        articles[:5],
        start=1,
    ):

        title = (
            article.get(
                "title",
                "Untitled",
            )
            or "Untitled"
        ).strip()

        source = (
            article.get(
                "source_name",
                "",
            )
            or ""
        ).strip()

        pub_date = (
            article.get(
                "pubDate",
                "",
            )
            or ""
        ).strip()

        link = (
            article.get(
                "link",
                "",
            )
            or ""
        ).strip()

        answer_lines.append(f"{index}. {title}")

        if source:

            answer_lines.append(f"   Source: {source}")

        if pub_date:

            answer_lines.append(f"   Published: {pub_date}")

        if link:

            answer_lines.append(f"   🔗 {link}")

        answer_lines.append("")

    answer = "\n".join(answer_lines)

    return Response(
        answer,
        content_type=("text/plain; charset=utf-8"),
        headers={
            "Cache-Control": "no-cache",
            "X-Entity-News": "newsdata",
        },
    )


# =========================================================
# ACTIVATE NEWSDATA ROUTER
# =========================================================

app.view_functions["chat"] = entity_news_direct_chat


print("Entity NewsData.io API " "loaded successfully.")


# =========================================================
# ENTITY TMDB MOVIE API
# =========================================================


@app.route("/api/movie")
def tmdb_movie():

    query = request.args.get(
        "query",
        "",
    ).strip()

    if not query:

        return jsonify({"error": "Movie name is required"}), 400

    if not TMDB_API_KEY:

        return jsonify({"error": "TMDB API key is not configured"}), 500

    try:

        response = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={
                "api_key": TMDB_API_KEY,
                "query": query,
                "language": "en-US",
                "include_adult": "false",
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for movie in data.get(
            "results",
            [],
        )[:10]:

            poster_path = movie.get("poster_path")

            results.append(
                {
                    "id": movie.get("id"),
                    "title": movie.get("title"),
                    "release_date": movie.get("release_date"),
                    "overview": movie.get("overview"),
                    "rating": movie.get("vote_average"),
                    "poster": (
                        "https://image.tmdb.org/t/p/w500" + poster_path
                        if poster_path
                        else None
                    ),
                }
            )

        return jsonify(
            {
                "query": query,
                "results": results,
            }
        )

    except requests.RequestException as error:

        print(
            "TMDB API error:",
            error,
        )

        return jsonify({"error": "Unable to contact TMDB"}), 502


# =========================================================
# ENTITY TMDB MOVIE CHAT INTEGRATION
# =========================================================


def entity_is_movie_question(message):

    text = (message or "").strip().lower()

    movie_words = [
        "movie",
        "movies",
        "film",
        "films",
        "cinema",
        "actor",
        "actress",
        "cast",
        "director",
        "rating",
        "imdb",
        "release date",
        "released",
        "box office",
        "trailer",
        "movie ke",
        "movie ki",
        "movie ka",
        "film ke",
        "film ki",
        "film ka",
        "movie batao",
        "film batao",
        "movie ke bare",
        "movie ke baare",
        "film ke bare",
        "film ke baare",
    ]

    return any(word in text for word in movie_words)


def entity_extract_movie_query(message):

    text = (message or "").strip()

    # -----------------------------------------------------
    # FIX:
    # "Interstellar movie ke bare mein batao"
    # MUST become:
    # "Interstellar"
    # -----------------------------------------------------

    match = re.search(
        r"^(.+?)\s+(?:movie|film)\s+"
        r"(?:ke\s+)?"
        r"(?:bare|baare)\s+"
        r"(?:mein|me)\b",
        text,
        flags=re.IGNORECASE,
    )

    if match:

        query = match.group(1).strip()

        if query:

            return query

    # -----------------------------------------------------
    # "Interstellar movie ke baare batao"
    # -----------------------------------------------------

    match = re.search(
        r"^(.+?)\s+(?:movie|film)\s+" r"(?:ke\s+)?" r"(?:bare|baare)\b",
        text,
        flags=re.IGNORECASE,
    )

    if match:

        query = match.group(1).strip()

        if query:

            return query

    # -----------------------------------------------------
    # "movie Interstellar"
    # "film Inception"
    # -----------------------------------------------------

    match = re.search(
        r"^(?:movie|film)\s+(.+?)$",
        text,
        flags=re.IGNORECASE,
    )

    if match:

        query = match.group(1).strip()

        if query:

            return query

    # -----------------------------------------------------
    # "tell me about Interstellar"
    # -----------------------------------------------------

    match = re.search(
        r"^(?:tell me about|about)\s+(.+)$",
        text,
        flags=re.IGNORECASE,
    )

    if match:

        query = match.group(1).strip()

        if query:

            return query

    return text


def entity_get_english_overview(
    movie_id,
    fallback_overview="",
):

    try:

        response = requests.get(
            ("https://api.themoviedb.org/3/" f"movie/{movie_id}/translations"),
            params={
                "api_key": TMDB_API_KEY,
            },
            timeout=10,
        )

        if not response.ok:

            return fallback_overview

        data = response.json()

        translations = (
            data.get(
                "translations",
                [],
            )
            or []
        )

        # -------------------------------------------------
        # PREFER US ENGLISH
        # -------------------------------------------------

        for item in translations:

            if item.get("iso_639_1") == "en" and item.get("iso_3166_1") == "US":

                translated_data = (
                    item.get(
                        "data",
                    )
                    or {}
                )

                overview = (
                    translated_data.get(
                        "overview",
                    )
                    or ""
                ).strip()

                if overview:

                    return overview

        # -------------------------------------------------
        # FALLBACK TO ANY ENGLISH
        # -------------------------------------------------

        for item in translations:

            if item.get("iso_639_1") == "en":

                translated_data = (
                    item.get(
                        "data",
                    )
                    or {}
                )

                overview = (
                    translated_data.get(
                        "overview",
                    )
                    or ""
                ).strip()

                if overview:

                    return overview

    except requests.RequestException as error:

        print(
            "TMDB translation error:",
            error,
        )

    return fallback_overview


def entity_tmdb_movie_response(message):

    query = entity_extract_movie_query(message)

    if not query:

        return None

    if not TMDB_API_KEY:

        return "TMDB API key is not configured."

    try:

        response = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={
                "api_key": TMDB_API_KEY,
                "query": query,
                "language": "en-US",
                "include_adult": "false",
            },
            timeout=10,
        )

        if not response.ok:

            print(
                "TMDB search HTTP error:",
                response.status_code,
            )

            return None

        data = response.json()

        results = (
            data.get(
                "results",
                [],
            )
            or []
        )

        if not results:

            print(
                "TMDB search returned " "no results for:",
                query,
            )

            return None

        movie = results[0]

        movie_id = movie.get("id")

        title = movie.get("title") or "Unknown movie"

        release_date = movie.get("release_date") or "Unknown"

        rating = movie.get("vote_average")

        fallback_overview = movie.get("overview") or ""

        overview = entity_get_english_overview(
            movie_id,
            fallback_overview,
        )

        if not overview:

            overview = "English overview is " "not available for this movie."

        poster_path = movie.get("poster_path")

        poster = None

        if poster_path:

            poster = "https://image.tmdb.org/t/p/w500" + poster_path

        answer = (
            f"🎬 {title}\n\n"
            f"📅 Release date: "
            f"{release_date}\n"
            f"⭐ Rating: "
            f"{rating}/10\n\n"
            f"📝 {overview}"
        )

        if poster:

            answer += f"\n\n🖼️ Poster: " f"{poster}"

        answer += "\n\nSource: TMDB"

        return answer

    except requests.RequestException as error:

        print(
            "TMDB chat error:",
            error,
        )

        return None


# =========================================================
# QUESTIONS THAT SHOULD GO DIRECTLY TO OLLAMA
# =========================================================

ENTITY_DIRECT_OLLAMA_WORDS = {
    "python",
    "javascript",
    "java",
    "c++",
    "html",
    "css",
    "code",
    "coding",
    "programming",
    "program",
    "function",
    "script",
    "debug",
    "bug",
    "error",
    "hello world",
    "ollama",
    "flask",
}


def entity_should_go_directly_to_ollama(message):

    message_lower = message.lower()

    for keyword in ENTITY_DIRECT_OLLAMA_WORDS:

        if keyword in message_lower:

            return True

    return False


# =========================================================
# TMDB CHAT INTERCEPTOR
# =========================================================


@app.before_request
def entity_tmdb_chat_interceptor():

    if request.path != "/api/chat":

        return None

    if request.method != "POST":

        return None

    try:

        payload = request.get_json(silent=True) or {}

    except Exception:

        return None

    message = (payload.get("message") or "").strip()

    if not message:

        return None

    # ---------------------------------------------
    # DIRECT OLLAMA ROUTING
    # ---------------------------------------------

    if entity_should_go_directly_to_ollama(message):

        print("ENTITY Route: Direct Ollama")

    return None

    if not entity_is_movie_question(message):

        return None

    movie_answer = entity_tmdb_movie_response(message)

    if not movie_answer:

        return None

    def generate_movie():

        yield movie_answer

    return Response(
        stream_with_context(generate_movie()),
        content_type=("text/plain; " "charset=utf-8"),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "X-Entity-Source": "TMDB",
        },
    )


# =========================================================
# ENTITY LOCAL KNOWLEDGE BRAIN
# JSON -> SEARCH -> OLLAMA
# =========================================================

KNOWLEDGE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "knowledge",
    "knowledge.json",
)


def entity_load_knowledge():

    try:

        if not os.path.exists(KNOWLEDGE_FILE):

            print(
                "ENTITY Knowledge file not found:",
                KNOWLEDGE_FILE,
            )

            return []

        with open(
            KNOWLEDGE_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            knowledge = json.load(file)

        if isinstance(knowledge, list):

            print(f"ENTITY Knowledge loaded: " f"{len(knowledge)} records.")

            return knowledge

        print("ENTITY Knowledge error: " "JSON root must be a list.")

        return []

    except json.JSONDecodeError as error:

        print(
            "ENTITY Knowledge JSON error:",
            error,
        )

        return []

    except Exception as error:

        print(
            "ENTITY Knowledge load error:",
            error,
        )

        return []


def entity_get_knowledge_text(item):

    if not isinstance(item, dict):

        return ""

    parts = []

    title = item.get(
        "title",
        "",
    )

    content = item.get(
        "content",
        "",
    )

    question = item.get(
        "question",
        "",
    )

    answer = item.get(
        "answer",
        "",
    )

    if title:

        parts.append(str(title))

    if content:

        parts.append(str(content))

    if question:

        parts.append(str(question))

    if answer:

        parts.append(str(answer))

    return " ".join(parts).strip()


# =========================================================
# HUGGING FACE HINGLISH CONVERSATIONS
# =========================================================

HINGLISH_DATASET_NAME = os.getenv(
    "HINGLISH_DATASET_NAME",
    "ankitdhiman/hinglish-conversations",
)

HINGLISH_DATASET_ENABLED = os.getenv(
    "HINGLISH_DATASET_ENABLED", "true"
).strip().lower() not in {"0", "false", "no", "off"}

try:
    HINGLISH_DATASET_LIMIT = int(os.getenv("HINGLISH_DATASET_LIMIT", "0"))
except ValueError:
    HINGLISH_DATASET_LIMIT = 0


def entity_load_hinglish_conversations():
    """
    Load the Hugging Face Hinglish conversation dataset once.

    Each dataset row is converted to the same question/answer shape
    already used by Entity's local knowledge search. The dataset is
    cached by Hugging Face after the first download, so later starts
    normally use the local cache.
    """

    if not HINGLISH_DATASET_ENABLED:
        print("ENTITY Hinglish dataset is disabled.")
        return []

    if load_dataset is None:
        print("ENTITY Hinglish dataset skipped: " "install the datasets package first.")
        return []

    try:
        print("ENTITY Hinglish dataset loading...")

        dataset = load_dataset(
            HINGLISH_DATASET_NAME,
            split="train",
        )

        records = []
        loaded = 0

        for row in dataset:
            if HINGLISH_DATASET_LIMIT > 0 and loaded >= HINGLISH_DATASET_LIMIT:
                break

            if not isinstance(row, dict):
                continue

            user_message = (row.get("user_message", "") or "").strip()

            assistant_message = (row.get("assistant_message", "") or "").strip()

            if not user_message or not assistant_message:
                continue

            records.append(
                {
                    "question": user_message,
                    "answer": assistant_message,
                    "source": "hinglish-conversations",
                    "language": (row.get("language", "hinglish") or "hinglish"),
                }
            )

            loaded += 1

        print("ENTITY Hinglish Conversations loaded: " f"{len(records)} records.")

        return records

    except Exception as error:
        print(
            "ENTITY Hinglish dataset load error:",
            error,
        )
        return []


# =========================================================
# LOAD KNOWLEDGE ONCE AT ENTITY STARTUP
# =========================================================

ENTITY_KNOWLEDGE = entity_load_knowledge()
ENTITY_HINGLISH_CONVERSATIONS = entity_load_hinglish_conversations()

print("ENTITY Factual local knowledge: " f"{len(ENTITY_KNOWLEDGE)} records.")
print(
    "ENTITY Hinglish conversation examples: "
    f"{len(ENTITY_HINGLISH_CONVERSATIONS)} records."
)


# =========================================================
# BUILD FAST INVERTED SEARCH INDEX
# WORD -> KNOWLEDGE RECORD IDs
# =========================================================

ENTITY_KNOWLEDGE_INDEX = []

ENTITY_WORD_INDEX = {}


def entity_extract_words(text):

    return set(
        re.findall(
            r"\b\w+\b",
            str(text).lower(),
        )
    )


print("ENTITY: Building fast search index...")


for record_id, knowledge_item in enumerate(ENTITY_KNOWLEDGE):

    knowledge_text = entity_get_knowledge_text(knowledge_item)

    if not knowledge_text:
        continue

    knowledge_words = entity_extract_words(knowledge_text)

    ENTITY_KNOWLEDGE_INDEX.append(knowledge_item)

    indexed_id = len(ENTITY_KNOWLEDGE_INDEX) - 1

    for word in knowledge_words:

        if len(word) < 2:
            continue

        if word not in ENTITY_WORD_INDEX:

            ENTITY_WORD_INDEX[word] = []

        ENTITY_WORD_INDEX[word].append(indexed_id)


print(f"ENTITY Search Index ready: " f"{len(ENTITY_KNOWLEDGE_INDEX)} indexed records.")

print(f"ENTITY Word Index ready: " f"{len(ENTITY_WORD_INDEX)} unique words.")

print(f"ENTITY Knowledge Brain ready: " f"{len(ENTITY_KNOWLEDGE)} records in memory.")


# =========================================================
# FAST KNOWLEDGE SEARCH
# =========================================================


# =========================================================
# SMART KNOWLEDGE SEARCH
# =========================================================


ENTITY_STOP_WORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "what",
    "which",
    "who",
    "whom",
    "why",
    "when",
    "where",
    "how",
    "do",
    "does",
    "did",
    "can",
    "could",
    "will",
    "would",
    "should",
    "may",
    "might",
    "please",
    "tell",
    "me",
    "about",
    "explain",
    "define",
    "give",
    "with",
    "for",
    "from",
    "into",
    "that",
    "this",
    "these",
    "those",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "at",
    "by",
}


ENTITY_MIN_KNOWLEDGE_SCORE = 2


def entity_search_knowledge(
    query,
    limit=5,
    return_score=False,
):

    if not ENTITY_KNOWLEDGE_INDEX:
        if return_score:
            return [], 0
        return []

    query_words = entity_extract_words(query)

    meaningful_words = {
        word for word in query_words if len(word) >= 3 and word not in ENTITY_STOP_WORDS
    }

    if not meaningful_words:
        if return_score:
            return [], 0
        return []

    scores = {}

    for word in meaningful_words:
        matching_ids = ENTITY_WORD_INDEX.get(word, [])

        for record_id in matching_ids:
            scores[record_id] = scores.get(record_id, 0) + 1

    if not scores:
        if return_score:
            return [], 0
        return []

    sorted_results = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    best_score = sorted_results[0][1]

    results = [
        ENTITY_KNOWLEDGE_INDEX[record_id] for record_id, score in sorted_results[:limit]
    ]

    if return_score:
        return results, best_score

    return results


def entity_build_knowledge_context(results):

    context_parts = []

    for index, item in enumerate(
        results,
        start=1,
    ):

        if not isinstance(item, dict):

            continue

        text = entity_get_knowledge_text(item)

        if not text:

            continue

        source = (
            item.get("source", "local knowledge")
            if isinstance(item, dict)
            else "local knowledge"
        )

        context_parts.append(f"[Knowledge {index} | {source}]\n{text}")

    return "\n\n".join(context_parts).strip()


@app.before_request
def entity_knowledge_chat_interceptor():

    if request.path != "/api/chat":

        return None

    if request.method != "POST":

        return None

    try:

        payload = request.get_json(silent=True) or {}

    except Exception:

        return None

    message = (
        payload.get(
            "message",
            "",
        )
        or ""
    ).strip()

    if not message:

        return None

    # ---------------------------------------------
    # DIRECT OLLAMA ROUTING
    # ---------------------------------------------

    if entity_should_go_directly_to_ollama(message):
        print("ENTITY Route: Direct Ollama")
        return None

    # ---------------------------------------------
    # SMART LOCAL KNOWLEDGE SEARCH
    # ---------------------------------------------

    results, best_score = entity_search_knowledge(
        message,
        limit=5,
        return_score=True,
    )

    # ---------------------------------------------
    # NO STRONG KNOWLEDGE MATCH
    # DIRECT OLLAMA
    # ---------------------------------------------

    if best_score < ENTITY_MIN_KNOWLEDGE_SCORE:
        print("ENTITY Route: Direct Ollama " f"(knowledge score: {best_score})")
        return None

    if not results:
        print("ENTITY Route: Direct Ollama (no knowledge match)")
        return None

    # ---------------------------------------------
    # STRONG KNOWLEDGE MATCH
    # USE LOCAL KNOWLEDGE
    # ---------------------------------------------

    knowledge_context = entity_build_knowledge_context(results)

    if not knowledge_context:
        return None

    print(
        "ENTITY Route: Local Knowledge | "
        f"Score: {best_score} | "
        f"Matches: {len(results)}"
    )

    model = (
        payload.get(
            "model",
            DEFAULT_MODEL,
        )
        or DEFAULT_MODEL
    ).strip()

    history = payload.get(
        "history",
        [],
    )

    effort = (
        payload.get(
            "effort",
            "Medium",
        )
        or "Medium"
    ).strip()

    effort_options = {
        "Low": {
            "num_ctx": 2048,
            "temperature": 0.4,
        },
        "Medium": {
            "num_ctx": 4096,
            "temperature": 0.6,
        },
        "High": {
            "num_ctx": 8192,
            "temperature": 0.7,
        },
        "Max": {
            "num_ctx": 16384,
            "temperature": 0.8,
        },
    }

    ollama_options = effort_options.get(
        effort,
        effort_options["Medium"],
    )

    conversation_messages = [
        {
            "role": "system",
            "content": (
                "You are Entity, a helpful AI assistant.\n\n"
                "You have been given information from "
                "Entity's local knowledge database.\n\n"
                "Use the LOCAL KNOWLEDGE when relevant to "
                "answer the user's question.\n"
                "Do not invent facts that contradict the "
                "provided knowledge.\n"
                "Answer naturally and clearly.\n\n"
                "LOCAL KNOWLEDGE:\n" + knowledge_context
            ),
        }
    ]

    if isinstance(
        history,
        list,
    ):

        for item in history[-20:]:

            if not isinstance(
                item,
                dict,
            ):
                continue

            role = item.get("role")

            content = item.get("content")

            if role not in (
                "user",
                "assistant",
            ):
                continue

            if not isinstance(
                content,
                str,
            ):
                continue

            content = content.strip()

            if not content:
                continue

            conversation_messages.append(
                {
                    "role": role,
                    "content": content,
                }
            )

    if not (
        conversation_messages
        and conversation_messages[-1].get("role") == "user"
        and conversation_messages[-1].get("content") == message
    ):

        conversation_messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

    def generate_knowledge_response():

        try:

            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": model,
                    "messages": conversation_messages,
                    "stream": True,
                    "options": ollama_options,
                },
                stream=True,
                timeout=300,
            )

            if not response.ok:

                yield (
                    "\n[ENTITY ERROR] " + (response.text or "Ollama request failed.")
                )

                return

            for line in response.iter_lines(decode_unicode=True):

                if not line:

                    continue

                try:

                    chunk = json.loads(line)

                except json.JSONDecodeError:

                    continue

                content = chunk.get(
                    "message",
                    {},
                ).get(
                    "content",
                    "",
                )

                if content:

                    yield content

                if chunk.get("done"):

                    break

        except requests.exceptions.ConnectionError:

            yield ("\n[ENTITY ERROR] " "Ollama is not running.")

        except requests.exceptions.Timeout:

            yield ("\n[ENTITY ERROR] " "Ollama timed out.")

        except requests.RequestException as error:

            yield ("\n[ENTITY ERROR] " + str(error))

        except Exception as error:

            yield ("\n[ENTITY ERROR] " + str(error))

    return Response(
        stream_with_context(generate_knowledge_response()),
        content_type=("text/plain; charset=utf-8"),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "X-Entity-Knowledge": "local-json",
        },
    )


print("Entity Local Knowledge Brain " "loaded successfully.")
# =========================================================
# ENTITY HINGLISH CONVERSATION BRAIN (SEPARATE)
# =========================================================
ENTITY_HINGLISH_INDEX = []
ENTITY_HINGLISH_WORD_INDEX = {}
ENTITY_HINGLISH_MAX_INDEX_RECORDS = int(os.getenv("HINGLISH_INDEX_LIMIT", "50000"))

print("ENTITY: Building Hinglish conversation index...")
for example in ENTITY_HINGLISH_CONVERSATIONS[:ENTITY_HINGLISH_MAX_INDEX_RECORDS]:
    question = (example.get("question", "") or "").strip()
    answer = (example.get("answer", "") or "").strip()
    if not question or not answer:
        continue
    ENTITY_HINGLISH_INDEX.append(example)
    indexed_id = len(ENTITY_HINGLISH_INDEX) - 1
    for word in entity_extract_words(question):
        if len(word) >= 2 and word not in ENTITY_STOP_WORDS:
            ENTITY_HINGLISH_WORD_INDEX.setdefault(word, []).append(indexed_id)

print("ENTITY Hinglish Index ready:", f"{len(ENTITY_HINGLISH_INDEX)} examples.")


def entity_is_hinglish_message(message):
    text = (message or "").strip().lower()
    if not text:
        return False
    words = set(re.findall(r"\b\w+\b", text))
    hindi_words = {
        "bhai",
        "yaar",
        "mujhe",
        "kya",
        "kaise",
        "kyu",
        "kyun",
        "hai",
        "hain",
        "batao",
        "samajh",
        "nahi",
        "acha",
        "accha",
        "wala",
        "wali",
        "mera",
        "meri",
        "tum",
        "aap",
        "karna",
        "karo",
    }
    return bool(words & hindi_words) or bool(re.search(r"[\u0900-\u097F]", text))


def entity_search_hinglish_examples(query, limit=3):
    scores = {}
    for word in entity_extract_words(query):
        if len(word) < 2 or word in ENTITY_STOP_WORDS:
            continue
        for record_id in ENTITY_HINGLISH_WORD_INDEX.get(word, []):
            scores[record_id] = scores.get(record_id, 0) + 1
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    results = []
    for record_id, _ in ranked:
        example = ENTITY_HINGLISH_INDEX[record_id]
        if (example.get("question", "") or "").strip().lower() != query.strip().lower():
            results.append(example)
        if len(results) >= limit:
            break
    return results


def entity_hinglish_response(message, model, history, effort, examples=None):
    """
    Generate a clean Hinglish response.

    The downloaded Hinglish dataset is useful for optional retrieval/search,
    but raw conversation examples are NOT injected into the model prompt.
    Random examples were causing the small local model to imitate awkward,
    unrelated wording.
    """

    opts = {
        "Low": {"num_ctx": 2048, "temperature": 0.25},
        "Medium": {"num_ctx": 4096, "temperature": 0.35},
        "High": {"num_ctx": 8192, "temperature": 0.4},
        "Max": {"num_ctx": 16384, "temperature": 0.45},
    }

    system = """
You are Entity, a helpful, accurate AI assistant.

LANGUAGE RULES:
- Detect the user's language and reply in the same language.
- If the user writes in Hinglish, reply in natural, everyday Hinglish.
- Do not translate English technical terms into unnatural Hindi.
- Use simple words and short, clear sentences.
- Never imitate broken, repetitive, overly literal, or machine-translated language.
- Do not use random examples from a dataset as facts or as a writing style.

QUALITY RULES:
- First answer the user's actual question directly.
- For programming or technical questions, explain the idea simply and give a small correct example only when useful.
- Do not make long lists unless the user asks for detail.
- Do not repeat the same point.
- If something is uncertain, say so instead of inventing an answer.
- Keep facts accurate and separate from guesses.
""".strip()

    messages = [{"role": "system", "content": system}]

    if isinstance(history, list):
        for item in history[-12:]:
            if (
                isinstance(item, dict)
                and item.get("role") in ("user", "assistant")
                and isinstance(item.get("content"), str)
                and item["content"].strip()
            ):
                messages.append(
                    {"role": item["role"], "content": item["content"].strip()}
                )

    if not (
        messages
        and messages[-1].get("role") == "user"
        and messages[-1].get("content") == message
    ):
        messages.append({"role": "user", "content": message})

    def generate():
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    "options": opts.get(effort, opts["Medium"]),
                },
                stream=True,
                timeout=300,
            )

            if not response.ok:
                yield "\n[ENTITY ERROR] " + (response.text or "Ollama request failed.")
                return

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue

                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content

                if chunk.get("done"):
                    break

        except requests.exceptions.ConnectionError:
            yield "\n[ENTITY ERROR] Ollama is not running."
        except requests.exceptions.Timeout:
            yield "\n[ENTITY ERROR] Ollama timed out."
        except requests.exceptions.RequestException as error:
            yield "\n[ENTITY ERROR] " + str(error)
        except Exception as error:
            yield "\n[ENTITY ERROR] " + str(error)

    return Response(
        stream_with_context(generate()),
        content_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "X-Entity-Hinglish": "guided",
        },
    )


@app.before_request
def entity_hinglish_chat_interceptor():
    if request.path != "/api/chat" or request.method != "POST":
        return None

    payload = request.get_json(silent=True) or {}
    message = (payload.get("message", "") or "").strip()

    if not message or not entity_is_hinglish_message(message):
        return None

    # Let live/factual tools and direct programming routes keep priority.
    if (
        entity_should_go_directly_to_ollama(message)
        or entity_is_news_question(message)
        or entity_is_weather_question(message)
        or entity_is_currency_question(message)
        or entity_is_movie_question(message)
    ):
        return None

    print("ENTITY Route: Clean Hinglish Assistant")

    return entity_hinglish_response(
        message,
        (payload.get("model", DEFAULT_MODEL) or DEFAULT_MODEL).strip(),
        payload.get("history", []),
        (payload.get("effort", "Medium") or "Medium").strip(),
    )


print("Entity Hinglish Conversation Brain loaded successfully.")


# =========================================================
# ENTITY TOOL CALLING BRAIN
# HUGGING FACE TOOL EXAMPLES + REAL LOCAL TOOLS
# =========================================================


TOOL_EXAMPLES_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "knowledge",
    "tool_examples.json",
)


# =========================================================
# LOAD TOOL EXAMPLES ONCE
# =========================================================


def entity_load_tool_examples():

    try:

        if not os.path.exists(TOOL_EXAMPLES_FILE):

            print(
                "ENTITY Tool Examples file not found:",
                TOOL_EXAMPLES_FILE,
            )

            return []

        with open(
            TOOL_EXAMPLES_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if isinstance(data, list):

            print(
                "ENTITY Tool Examples loaded:",
                f"{len(data)} examples.",
            )

            return data

        print(
            "ENTITY Tool Examples error:",
            "JSON root must be a list.",
        )

        return []

    except Exception as error:

        print(
            "ENTITY Tool Examples load error:",
            error,
        )

        return []


ENTITY_TOOL_EXAMPLES = entity_load_tool_examples()


# =========================================================
# TOOL EXAMPLE TEXT
# =========================================================


def entity_get_tool_example_text(item):

    if not isinstance(item, dict):

        return ""

    parts = []

    possible_fields = [
        "instruction",
        "input",
        "query",
        "question",
        "prompt",
        "user",
        "text",
        "content",
    ]

    for field in possible_fields:

        value = item.get(field)

        if isinstance(value, str):

            value = value.strip()

            if value:

                parts.append(value)

    messages = item.get("messages")

    if isinstance(messages, list):

        for message in messages:

            if not isinstance(message, dict):

                continue

            role = message.get("role", "")

            content = message.get("content", "")

            if role == "user" and isinstance(content, str) and content.strip():

                parts.append(content.strip())

    if not parts:

        try:

            text = json.dumps(
                item,
                ensure_ascii=False,
            )

            return text[:1200]

        except Exception:

            return ""

    return " ".join(parts).strip()


# =========================================================
# BUILD FAST TOOL EXAMPLE INDEX
# =========================================================


ENTITY_TOOL_EXAMPLE_INDEX = []

ENTITY_TOOL_WORD_INDEX = {}


print("ENTITY: Building Tool Calling example index...")


for example_id, example in enumerate(ENTITY_TOOL_EXAMPLES):

    example_text = entity_get_tool_example_text(example)

    if not example_text:

        continue

    ENTITY_TOOL_EXAMPLE_INDEX.append(example)

    indexed_id = len(ENTITY_TOOL_EXAMPLE_INDEX) - 1

    words = entity_extract_words(example_text)

    for word in words:

        if len(word) < 3:

            continue

        if word in ENTITY_STOP_WORDS:

            continue

        if word not in ENTITY_TOOL_WORD_INDEX:

            ENTITY_TOOL_WORD_INDEX[word] = []

        ENTITY_TOOL_WORD_INDEX[word].append(indexed_id)


print(
    "ENTITY Tool Example Index ready:",
    f"{len(ENTITY_TOOL_EXAMPLE_INDEX)} examples.",
)

print(
    "ENTITY Tool Word Index ready:",
    f"{len(ENTITY_TOOL_WORD_INDEX)} words.",
)


# =========================================================
# SEARCH TOOL EXAMPLES
# =========================================================


def entity_search_tool_examples(
    query,
    limit=3,
):

    if not ENTITY_TOOL_EXAMPLE_INDEX:

        return []

    query_words = entity_extract_words(query)

    meaningful_words = {
        word
        for word in query_words
        if (len(word) >= 3 and word not in ENTITY_STOP_WORDS)
    }

    if not meaningful_words:

        return []

    scores = {}

    for word in meaningful_words:

        matching_ids = ENTITY_TOOL_WORD_INDEX.get(
            word,
            [],
        )

        for record_id in matching_ids:

            scores[record_id] = (
                scores.get(
                    record_id,
                    0,
                )
                + 1
            )

    if not scores:

        return []

    sorted_results = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        ENTITY_TOOL_EXAMPLE_INDEX[record_id]
        for record_id, score in sorted_results[:limit]
    ]


# =========================================================
# BUILD TOOL EXAMPLE CONTEXT
# REFERENCE ONLY
# =========================================================


def entity_build_tool_example_context(examples):

    parts = []

    for index, example in enumerate(
        examples,
        start=1,
    ):

        text = entity_get_tool_example_text(example)

        if not text:

            continue

        text = text[:600]

        parts.append(f"[Tool Example {index}]\n{text}")

    return "\n\n".join(parts).strip()


# =========================================================
# REAL ENTITY TOOL SCHEMAS
# =========================================================


def entity_get_tool_schemas():

    return [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": ("Get current live weather " "for a city."),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": ("City name"),
                        },
                    },
                    "required": [
                        "city",
                    ],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "convert_currency",
                "description": (
                    "Convert an amount from one "
                    "currency to another using "
                    "the live currency rate."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "number",
                            "description": ("Amount to convert"),
                        },
                        "from_currency": {
                            "type": "string",
                            "description": ("Source currency code, " "for example USD"),
                        },
                        "to_currency": {
                            "type": "string",
                            "description": ("Target currency code, " "for example INR"),
                        },
                    },
                    "required": [
                        "amount",
                        "from_currency",
                        "to_currency",
                    ],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_local_knowledge",
                "description": ("Search Entity's local " "knowledge database."),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": ("Question or topic " "to search"),
                        },
                    },
                    "required": [
                        "query",
                    ],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": ("Get the current local " "date and time."),
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
    ]


# =========================================================
# EXECUTE SAFE ENTITY TOOLS
# =========================================================


def entity_execute_tool(
    tool_name,
    arguments,
):

    if not isinstance(arguments, dict):

        arguments = {}

    try:

        # ---------------------------------------------
        # WEATHER
        # ---------------------------------------------

        if tool_name == "get_weather":

            city = str(
                arguments.get(
                    "city",
                    "",
                )
            ).strip()

            if not city:

                return {
                    "success": False,
                    "error": ("City is required."),
                }

            result = entity_get_weather(city)

            if not result:

                return {
                    "success": False,
                    "error": ("Weather not found."),
                }

            return {
                "success": True,
                "tool": tool_name,
                "result": result,
            }

        # ---------------------------------------------
        # CURRENCY
        # ---------------------------------------------

        if tool_name == "convert_currency":

            amount = arguments.get("amount")

            from_currency = str(
                arguments.get(
                    "from_currency",
                    "",
                )
            ).strip()

            to_currency = str(
                arguments.get(
                    "to_currency",
                    "",
                )
            ).strip()

            if amount is None:

                return {
                    "success": False,
                    "error": ("Amount is required."),
                }

            try:

                amount = float(amount)

            except (
                TypeError,
                ValueError,
            ):

                return {
                    "success": False,
                    "error": ("Invalid amount."),
                }

            result = entity_get_currency_rate(
                amount,
                from_currency,
                to_currency,
            )

            if not result:

                return {
                    "success": False,
                    "error": ("Currency conversion failed."),
                }

            return {
                "success": True,
                "tool": tool_name,
                "result": result,
            }

        # ---------------------------------------------
        # LOCAL KNOWLEDGE
        # ---------------------------------------------

        if tool_name == ("search_local_knowledge"):

            query = str(
                arguments.get(
                    "query",
                    "",
                )
            ).strip()

            if not query:

                return {
                    "success": False,
                    "error": ("Query is required."),
                }

            results = entity_search_knowledge(
                query,
                limit=5,
            )

            cleaned_results = []

            for item in results:

                text = entity_get_knowledge_text(item)

                if text:

                    cleaned_results.append(text[:1500])

            return {
                "success": True,
                "tool": tool_name,
                "results": cleaned_results,
            }

        # ---------------------------------------------
        # TIME
        # ---------------------------------------------

        if tool_name == ("get_current_time"):

            return {
                "success": True,
                "tool": tool_name,
                "result": {
                    "date_time": (datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                },
            }

        # ---------------------------------------------
        # UNKNOWN TOOL
        # ---------------------------------------------

        return {
            "success": False,
            "error": (f"Unknown tool: {tool_name}"),
        }

    except Exception as error:

        print(
            "ENTITY Tool execution error:",
            error,
        )

        return {
            "success": False,
            "error": str(error),
        }


# =========================================================
# TOOL CALLING CHAT RESPONSE
# =========================================================


def entity_tool_calling_response(
    message,
    model,
    history,
    effort,
):

    effort_options = {
        "Low": {
            "num_ctx": 2048,
            "temperature": 0.4,
        },
        "Medium": {
            "num_ctx": 4096,
            "temperature": 0.6,
        },
        "High": {
            "num_ctx": 8192,
            "temperature": 0.7,
        },
        "Max": {
            "num_ctx": 16384,
            "temperature": 0.8,
        },
    }

    ollama_options = effort_options.get(
        effort,
        effort_options["Medium"],
    )

    # ---------------------------------------------
    # FIND RELEVANT TOOL DATASET EXAMPLES
    # ---------------------------------------------

    tool_examples = entity_search_tool_examples(
        message,
        limit=3,
    )

    example_context = entity_build_tool_example_context(tool_examples)

    system_content = (
        "You are Entity, a helpful AI assistant.\n\n"
        "You have access to real tools.\n"
        "Use a tool only when it is actually "
        "needed.\n"
        "Only call tools from the AVAILABLE "
        "TOOLS list.\n"
        "Never invent a tool name.\n"
        "Never claim a tool completed unless "
        "its result was returned.\n"
        "For normal questions, answer normally."
    )

    if example_context:

        system_content += (
            "\n\nREFERENCE TOOL EXAMPLES:\n"
            "These are learning examples only.\n"
            "Do not call any tool shown in these "
            "examples unless that exact tool exists "
            "in AVAILABLE TOOLS.\n\n" + example_context
        )

    messages = [
        {
            "role": "system",
            "content": system_content,
        }
    ]

    # ---------------------------------------------
    # HISTORY
    # ---------------------------------------------

    if isinstance(
        history,
        list,
    ):

        for item in history[-12:]:

            if not isinstance(
                item,
                dict,
            ):

                continue

            role = item.get("role")

            content = item.get("content")

            if role not in (
                "user",
                "assistant",
            ):

                continue

            if not isinstance(
                content,
                str,
            ):

                continue

            content = content.strip()

            if not content:

                continue

            messages.append(
                {
                    "role": role,
                    "content": content,
                }
            )

    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    tools = entity_get_tool_schemas()

    # ---------------------------------------------
    # TOOL CALLING LOOP
    # ---------------------------------------------

    for round_number in range(3):

        try:

            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "tools": tools,
                    "stream": False,
                    "options": ollama_options,
                },
                timeout=300,
            )

            response.raise_for_status()

            data = response.json()

        except Exception as error:

            return Response(
                ("[ENTITY ERROR] " + str(error)),
                content_type=("text/plain; charset=utf-8"),
            )

        assistant_message = (
            data.get(
                "message",
                {},
            )
            or {}
        )

        tool_calls = (
            assistant_message.get(
                "tool_calls",
                [],
            )
            or []
        )

        # -----------------------------------------
        # NORMAL FINAL ANSWER
        # -----------------------------------------

        if not tool_calls:

            final_answer = (
                assistant_message.get(
                    "content",
                    "",
                )
                or ""
            ).strip()

            if not final_answer:

                final_answer = "I could not generate " "a response."

            return Response(
                final_answer,
                content_type=("text/plain; charset=utf-8"),
                headers={
                    "Cache-Control": ("no-cache"),
                    "X-Entity-Tools": ("enabled"),
                },
            )

        # -----------------------------------------
        # ADD ASSISTANT TOOL CALL MESSAGE
        # -----------------------------------------

        messages.append(
            {
                "role": "assistant",
                "content": (
                    assistant_message.get(
                        "content",
                        "",
                    )
                    or ""
                ),
                "tool_calls": tool_calls,
            }
        )

        # -----------------------------------------
        # EXECUTE TOOL CALLS
        # -----------------------------------------

        for call in tool_calls:

            function = (
                call.get(
                    "function",
                    {},
                )
                or {}
            )

            tool_name = (
                function.get(
                    "name",
                    "",
                )
                or ""
            )

            arguments = (
                function.get(
                    "arguments",
                    {},
                )
                or {}
            )

            print(
                "ENTITY Tool Call:",
                tool_name,
                arguments,
            )

            tool_result = entity_execute_tool(
                tool_name,
                arguments,
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": json.dumps(
                        tool_result,
                        ensure_ascii=False,
                    ),
                }
            )

    return Response(
        ("ENTITY Tool limit reached."),
        content_type=("text/plain; charset=utf-8"),
    )


# =========================================================
# TOOL CALLING ROUTER
# =========================================================


def entity_tool_calling_router():

    data = request.get_json(silent=True) or {}

    message = (
        data.get(
            "message",
            "",
        )
        or ""
    ).strip()

    # Normal request
    # Existing Entity routing remains unchanged.

    if not message:

        return entity_smart_chat()

    text = message.lower()

    # -----------------------------------------
    # NEWS API ROUTING FIRST
    # -----------------------------------------

    if entity_is_news_question(message):
        print("ENTITY Route: NewsData API")
        return entity_news_direct_chat()

    tool_keywords = [
        "weather",
        "temperature",
        "currency",
        "convert",
        "exchange rate",
        "what time",
        "current time",
        "time now",
        "search my knowledge",
        "search knowledge",
        "find in knowledge",
    ]

    should_use_tools = any(keyword in text for keyword in tool_keywords)

    if not should_use_tools:

        return entity_smart_chat()

    model = (
        data.get(
            "model",
            DEFAULT_MODEL,
        )
        or DEFAULT_MODEL
    ).strip()

    history = data.get(
        "history",
        [],
    )

    effort = (
        data.get(
            "effort",
            "Medium",
        )
        or "Medium"
    ).strip()

    print("ENTITY Route: Tool Calling")

    return entity_tool_calling_response(
        message,
        model,
        history,
        effort,
    )


# =========================================================
# ACTIVATE TOOL CALLING ROUTER
# =========================================================


app.view_functions["chat"] = entity_tool_calling_router


print("Entity Tool Calling Brain " "loaded successfully.")


# =========================================================
# ENTITY GSM8K REASONING BRAIN
# =========================================================

GSM8K_REASONING_DATASET_NAME = os.getenv("GSM8K_REASONING_DATASET_NAME", "openai/gsm8k")

GSM8K_REASONING_DATASET_CONFIG = os.getenv("GSM8K_REASONING_DATASET_CONFIG", "main")


def entity_load_reasoning_examples():
    """
    GSM8K ko factual knowledge se alag load karta hai.
    """

    if load_dataset is None:
        print("ENTITY Reasoning Brain skipped: " "datasets package not available.")
        return []

    try:
        print("ENTITY GSM8K Reasoning dataset loading...")

        dataset = load_dataset(
            GSM8K_REASONING_DATASET_NAME, GSM8K_REASONING_DATASET_CONFIG, split="train"
        )

        examples = []

        for row in dataset:
            question = (row.get("question", "") or "").strip()

            answer = (row.get("answer", "") or "").strip()

            if question and answer:
                examples.append({"question": question, "answer": answer})

        print("ENTITY GSM8K Reasoning examples loaded:", f"{len(examples)} records.")

        return examples

    except Exception as error:
        print("ENTITY Reasoning Brain load error:", error)

        return []


# =========================================================
# LOAD REASONING DATA
# =========================================================

ENTITY_REASONING_EXAMPLES = entity_load_reasoning_examples()

ENTITY_REASONING_WORD_INDEX = {}


# =========================================================
# DETECT REASONING QUESTION
# =========================================================


def entity_is_reasoning_question(message):

    text = (message or "").lower()

    reasoning_markers = [
        # English
        "solve",
        "calculate",
        "calculation",
        "math",
        "mathematics",
        "equation",
        "percentage",
        "percent",
        "ratio",
        "average",
        "profit",
        "loss",
        "speed",
        "distance",
        "time problem",
        "word problem",
        "reasoning",
        "logic",
        "how many",
        "how much",
        # Hinglish
        "kitne",
        "kitna",
        "calculate karo",
        "solve karo",
        "hisab",
        "hisaab",
        "percentage kitna",
        # Hindi
        "गणित",
        "हल करो",
        "हिसाब",
        "कितना",
        "कितने",
    ]

    return any(marker in text for marker in reasoning_markers)


# =========================================================
# BUILD REASONING SEARCH INDEX
# =========================================================


def entity_build_reasoning_index():

    print("ENTITY: Building Reasoning Brain index...")

    for record_id, item in enumerate(ENTITY_REASONING_EXAMPLES):

        question = item.get("question", "") or ""

        words = entity_extract_words(question)

        for word in words:

            if len(word) < 3:
                continue

            if word in ENTITY_STOP_WORDS:
                continue

            ENTITY_REASONING_WORD_INDEX.setdefault(word, []).append(record_id)

    print(
        "ENTITY Reasoning Index ready:", f"{len(ENTITY_REASONING_EXAMPLES)} examples."
    )


# =========================================================
# SEARCH SIMILAR REASONING EXAMPLES
# =========================================================


def entity_search_reasoning_examples(query, limit=2):

    if not ENTITY_REASONING_EXAMPLES:
        return []

    words = entity_extract_words(query)

    meaningful_words = {
        word for word in words if (len(word) >= 3 and word not in ENTITY_STOP_WORDS)
    }

    if not meaningful_words:
        return []

    scores = {}

    for word in meaningful_words:

        matching_ids = ENTITY_REASONING_WORD_INDEX.get(word, [])

        for record_id in matching_ids:

            scores[record_id] = scores.get(record_id, 0) + 1

    if not scores:
        return []

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    return [ENTITY_REASONING_EXAMPLES[record_id] for record_id, score in ranked[:limit]]


# =========================================================
# CREATE REASONING CONTEXT
# =========================================================


def entity_get_reasoning_context(message):

    if not entity_is_reasoning_question(message):
        return ""

    examples = entity_search_reasoning_examples(message, limit=2)

    base_instruction = """

REASONING MODE:

Solve the user's problem carefully.

Rules:
- Understand the problem first.
- Solve step by step when useful.
- Check arithmetic before giving the answer.
- Do not blindly copy any example.
- Give the final answer clearly.
- Keep the explanation simple.
"""

    if not examples:
        return base_instruction

    parts = [base_instruction, "", "REFERENCE REASONING EXAMPLES:"]

    for index, item in enumerate(examples, start=1):

        question = item.get("question", "") or ""

        answer = item.get("answer", "") or ""

        # GSM8K markup remove
        answer = re.sub(r"<<.*?>>", "", answer)

        parts.append(f"""

Example {index}

Question:
{question}

Worked reasoning:
{answer[:1000]}
""")

    return "\n".join(parts)


# =========================================================
# BUILD INDEX
# =========================================================

entity_build_reasoning_index()

print("Entity GSM8K Reasoning Brain loaded successfully.")


# =========================================================
# RUN
# =========================================================


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        threaded=True,
    )
