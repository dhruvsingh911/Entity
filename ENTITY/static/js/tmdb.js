console.log("TMDB JS LOADED SUCCESSFULLY");

(function () {
    "use strict";

    function getMovieData(raw) {
        raw = String(raw || "");

        const titleMatch = raw.match(
            /🎬\s*(.*?)(?=\s*📅|\s*⭐|\s*📝|\s*🖼️|\s*Source:|$)/s
        );

        const dateMatch = raw.match(
            /📅\s*Release date:\s*(.*?)(?=\s*⭐|\s*📝|\s*🖼️|\s*Source:|$)/s
        );

        const ratingMatch = raw.match(
            /⭐\s*Rating:\s*(.*?)(?=\s*📝|\s*🖼️|\s*Source:|$)/s
        );

        const overviewMatch = raw.match(
            /📝\s*(.*?)(?=\s*🖼️\s*Poster:|\s*Source:\s*TMDB|$)/s
        );

        const posterMatch = raw.match(
            /🖼️\s*Poster:\s*(https?:\/\/[^\s]+)/i
        );

        return {
            title: titleMatch ? titleMatch[1].trim() : "Movie",
            date: dateMatch ? dateMatch[1].trim() : "",
            rating: ratingMatch ? ratingMatch[1].trim() : "",
            overview: overviewMatch ? overviewMatch[1].trim() : "",
            poster: posterMatch
                ? posterMatch[1].trim()
                : ""
        };
    }


    function createCard(data) {
        const card = document.createElement("div");

        card.className = "entity-tmdb-card";

        card.style.cssText = `
            display: flex;
            gap: 20px;
            padding: 20px;
            margin-top: 10px;
            max-width: 850px;
            border: 1px solid rgba(255,255,255,.12);
            border-radius: 18px;
            background: rgba(35,35,40,.95);
            box-sizing: border-box;
        `;


        if (data.poster) {
            const img = document.createElement("img");

            img.src = data.poster;
            img.alt = data.title;

            img.style.cssText = `
                width: 150px;
                height: 225px;
                object-fit: cover;
                border-radius: 12px;
                flex-shrink: 0;
            `;

            img.onerror = function () {
                img.remove();
            };

            card.appendChild(img);
        }


        const details = document.createElement("div");

        details.style.cssText = `
            flex: 1;
            min-width: 0;
        `;


        const title = document.createElement("div");

        title.textContent = "🎬 " + data.title;

        title.style.cssText = `
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 14px;
        `;

        details.appendChild(title);


        const meta = document.createElement("div");

        const parts = [];

        if (data.date) {
            parts.push("📅 " + data.date);
        }

        if (data.rating) {
            parts.push("⭐ " + data.rating);
        }

        meta.textContent = parts.join("     ");

        meta.style.cssText = `
            margin-bottom: 18px;
            opacity: .9;
        `;

        details.appendChild(meta);


        if (data.overview) {
            const overview = document.createElement("div");

            overview.textContent = data.overview;

            overview.style.cssText = `
                line-height: 1.7;
                margin-top: 10px;
            `;

            details.appendChild(overview);
        }


        const source = document.createElement("div");

        source.textContent = "Powered by TMDB";

        source.style.cssText = `
            margin-top: 18px;
            font-size: 12px;
            opacity: .55;
        `;

        details.appendChild(source);

        card.appendChild(details);

        return card;
    }


    function formatMessage(content) {

    if (!content) {
        return;
    }

    const raw =
        content.innerText ||
        content.textContent ||
        "";

    if (!raw.includes("Source: TMDB")) {
        return;
    }

    const parent =
        content.parentElement;

    if (!parent) {
        return;
    }

    const existingCard =
        parent.querySelector(
            ".entity-tmdb-card"
        );

    if (existingCard) {
        return;
    }

    const data =
        getMovieData(raw);

    console.log(
        "TMDB CARD CREATED:",
        data.title
    );

    const card =
        createCard(data);

    content.style.display =
        "none";

    content.insertAdjacentElement(
        "afterend",
        card
    );

}


    function scanMessages() {

    const messages =
        document.querySelectorAll(
            ".assistant-content"
        );

    messages.forEach(function (message) {

        const raw =
            message.innerText ||
            message.textContent ||
            "";

        if (
            raw.includes("Source: TMDB")
        ) {

            formatMessage(message);

        }

    });

}


    let scanTimer = null;


    function delayedScan() {
        clearTimeout(scanTimer);

        scanTimer = setTimeout(function () {
            scanMessages();
        }, 300);
    }


    function startTMDB() {
        delayedScan();

        const observer = new MutationObserver(function () {
            delayedScan();
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            characterData: true
        });


        setInterval(function () {
            scanMessages();
        }, 1000);
    }


    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            startTMDB
        );
    } else {
        startTMDB();
    }

})();