document.addEventListener("DOMContentLoaded", () => {

    console.log("Entity app.js loaded successfully");

    const input =
        document.getElementById("messageInput");

    const addButton =
        document.getElementById("addButton") ||
        document.querySelector(".add-btn");

    const modelButton =
        document.getElementById("modelButton") ||
        document.querySelector(".model-btn");

    const accountButton =
        document.getElementById("accountButton") ||
        document.querySelector(".account-row");

    console.log("Add button:", addButton);


    /* =====================================================
       TEXTAREA
    ===================================================== */

    if (input) {

        input.addEventListener("input", () => {

            input.style.height = "auto";

            input.style.height =
                Math.min(input.scrollHeight, 90) + "px";

        });

    }


    /* =====================================================
       CREATE PLUS MENU
    ===================================================== */

    let addMenu =
        document.getElementById("entityAddMenu");


    if (!addMenu) {

        console.log("Creating Entity add menu...");

        addMenu =
            document.createElement("div");

        addMenu.id =
            "entityAddMenu";

        addMenu.className =
            "entity-add-menu";


        addMenu.innerHTML = `

            <button class="add-menu-item">

                <span class="material-symbols-rounded">
                    attach_file
                </span>

                <span class="menu-label">
                    Add files or photos
                </span>

                <span class="menu-shortcut">
                    Ctrl+U
                </span>

            </button>


            <button class="add-menu-item">

                <span class="material-symbols-rounded">
                    photo_camera
                </span>

                <span class="menu-label">
                    Take a screenshot
                </span>

            </button>


            <button class="add-menu-item">

                <span class="material-symbols-rounded">
                    inventory_2
                </span>

                <span class="menu-label">
                    Add to project
                </span>

                <span class="material-symbols-rounded submenu-arrow">
                    chevron_right
                </span>

            </button>


            <div class="menu-divider"></div>


            <button class="add-menu-item">

                <span class="material-symbols-rounded">
                    featured_play_list
                </span>

                <span class="menu-label">
                    Skills
                </span>

                <span class="material-symbols-rounded submenu-arrow">
                    chevron_right
                </span>

            </button>


            <button class="add-menu-item">

                <span class="material-symbols-rounded">
                    extension
                </span>

                <span class="menu-label">
                    Add connector
                </span>

                <span class="material-symbols-rounded submenu-arrow">
                    chevron_right
                </span>

            </button>


            <button class="add-menu-item">

                <span class="material-symbols-rounded">
                    extension_off
                </span>

                <span class="menu-label">
                    Add plugins...
                </span>

            </button>


            <div class="menu-divider"></div>


            <button class="add-menu-item">

                <span class="material-symbols-rounded">
                    language
                </span>

                <span class="menu-label">
                    Web search
                </span>

            </button>

        `;


        const composer =
            document.querySelector(".composer");


        if (composer) {

            composer.appendChild(addMenu);

            console.log(
                "Menu created inside composer."
            );

        } else {

            document.body.appendChild(addMenu);

            console.log(
                "Composer not found. Menu added to body."
            );

        }

    }


    /* =====================================================
       PLUS BUTTON
    ===================================================== */

    if (!addButton) {

        console.error(
            "ERROR: .add-btn button not found!"
        );

    } else {

        console.log(
            "Plus button successfully connected."
        );


        addButton.addEventListener("click", (event) => {

            event.preventDefault();

            event.stopPropagation();


            const isOpen =
                addMenu.classList.contains("visible");


            if (isOpen) {

                addMenu.classList.remove(
                    "visible"
                );

                addButton.classList.remove(
                    "menu-open"
                );

                console.log(
                    "Entity add menu closed."
                );

                return;

            }


            addMenu.classList.add(
                "visible"
            );

            addButton.classList.add(
                "menu-open"
            );


            addMenu.style.display =
                "block";

            addMenu.style.visibility =
                "visible";

            addMenu.style.opacity =
                "1";

            addMenu.style.zIndex =
                "999999";


            console.log(
                "Entity add menu OPENED."
            );

        });

    }


    /* =====================================================
       CLICK INSIDE MENU
    ===================================================== */

    if (addMenu) {

        addMenu.addEventListener(
            "click",
            (event) => {

                event.stopPropagation();

            }
        );

    }


    /* =====================================================
       CLICK OUTSIDE
    ===================================================== */

    document.addEventListener(
        "click",
        (event) => {

            if (
                addMenu &&
                addButton &&
                !addMenu.contains(event.target) &&
                !addButton.contains(event.target)
            ) {

                addMenu.classList.remove(
                    "visible"
                );

                addButton.classList.remove(
                    "menu-open"
                );

            }


            if (
                modelButton &&
                !modelButton.contains(event.target)
            ) {

                modelButton.classList.remove(
                    "open"
                );

            }


            if (
                accountButton &&
                !accountButton.contains(event.target)
            ) {

                accountButton.classList.remove(
                    "open"
                );

            }

        }
    );


    /* =====================================================
       MODEL BUTTON
    ===================================================== */

    if (modelButton) {

        modelButton.addEventListener(
            "click",
            (event) => {

                event.preventDefault();

                event.stopPropagation();

            }
        );

    }


    /* =====================================================
       ACCOUNT
    ===================================================== */

    if (accountButton) {

        accountButton.addEventListener(
            "click",
            (event) => {

                event.preventDefault();

                event.stopPropagation();

                accountButton.classList.toggle(
                    "open"
                );

            }
        );

    }


    /* =====================================================
       MODE SWITCH
    ===================================================== */

    document
        .querySelectorAll(".mode")
        .forEach(button => {

            button.addEventListener(
                "click",
                (event) => {

                    event.preventDefault();

                    event.stopPropagation();


                    document
                        .querySelectorAll(".mode")
                        .forEach(btn => {

                            btn.classList.remove(
                                "active"
                            );

                        });


                    button.classList.add(
                        "active"
                    );

                }
            );

        });


    /* =====================================================
       ESC
    ===================================================== */

    document.addEventListener(
        "keydown",
        (event) => {

            if (event.key === "Escape") {

                if (addMenu) {

                    addMenu.classList.remove(
                        "visible"
                    );

                }


                if (addButton) {

                    addButton.classList.remove(
                        "menu-open"
                    );

                }

            }

        }
    );


    console.log(
        "Entity plus-menu system ready."
    );


    /* =====================================================
       ENTITY MODEL DROPDOWN
    ===================================================== */

    (function () {

        if (!modelButton) {

            console.error(
                "Entity: modelButton not found"
            );

            return;

        }


        document
            .querySelectorAll(
                ".entity-model-menu"
            )
            .forEach(item => item.remove());


        document
            .querySelectorAll(
                ".entity-more-models-menu"
            )
            .forEach(item => item.remove());


        document
            .querySelectorAll(
                ".entity-effort-menu"
            )
            .forEach(item => item.remove());


        /* =====================================================
           STORAGE
        ===================================================== */

        const MODEL_KEY =
            "entity_ollama_model";

        const DISPLAY_KEY =
            "entity_model_display_name";

        const EFFORT_KEY =
            "entity_effort";


        function getSavedModel() {

            return (
                localStorage.getItem(
                    MODEL_KEY
                ) || ""
            );

        }


        function getSavedDisplayName() {

            return (
                localStorage.getItem(
                    DISPLAY_KEY
                ) || ""
            );

        }


        function getSavedEffort() {

            return (
                localStorage.getItem(
                    EFFORT_KEY
                ) || "Medium"
            );

        }


        /* =====================================================
           REAL OLLAMA MODEL NAME
        ===================================================== */

        function getEntityModelName(
            modelName
        ) {

            return modelName || "";

        }


        /* =====================================================
           MAIN MODEL MENU
        ===================================================== */

        const menu =
            document.createElement(
                "div"
            );

        menu.className =
            "entity-model-menu";


        menu.innerHTML = `

            <div class="model-main-section">

                <button
                    class="model-current-row"
                    type="button"
                >

                    <div class="model-row-left">

                        <span class="model-name">
                            Select model
                        </span>

                        <span class="model-description">
                            Local Ollama model
                        </span>

                    </div>

                    <span
                        class="material-symbols-rounded model-check"
                    >
                        check
                    </span>

                </button>


                <button
                    class="model-effort-row"
                    type="button"
                >

                    <span class="effort-title">
                        Effort
                    </span>

                    <span class="effort-value">

                        <span class="effort-text">
                            Medium
                        </span>

                        <span
                            class="material-symbols-rounded"
                        >
                            chevron_right
                        </span>

                    </span>

                </button>


                <button
                    class="more-models-row"
                    type="button"
                >

                    <span>
                        More models
                    </span>

                    <span
                        class="material-symbols-rounded"
                    >
                        chevron_right
                    </span>

                </button>

            </div>

        `;


        document.body.appendChild(
            menu
        );


        /* =====================================================
           MODEL BUTTON DISPLAY
        ===================================================== */

        function updateModelButton(
            displayName
        ) {

            const strong =
                modelButton.querySelector(
                    "strong"
                );


            if (strong) {

                strong.textContent =
                    displayName ||
                    "Select model";

            }

        }


        function updateCurrentModelRow(
            displayName
        ) {

            const name =
                menu.querySelector(
                    ".model-name"
                );


            if (name) {

                name.textContent =
                    displayName ||
                    "Select model";

            }


            const check =
                menu.querySelector(
                    ".model-check"
                );


            if (check) {

                check.style.visibility =
                    displayName
                        ? "visible"
                        : "hidden";

            }

        }


        function setSelectedModel(
            modelName,
            displayName = modelName
        ) {

            if (!modelName) {

                return;

            }


            const realName =
                String(
                    modelName
                );


            const shownName =
                String(
                    displayName ||
                    modelName
                );


            localStorage.setItem(
                MODEL_KEY,
                realName
            );


            localStorage.setItem(
                DISPLAY_KEY,
                shownName
            );


            updateModelButton(
                shownName
            );


            updateCurrentModelRow(
                shownName
            );


            console.log(
                "Entity selected Ollama model:",
                realName
            );

        }


        function restoreSelectedModel() {

            const savedModel =
                getSavedModel();


            const savedDisplay =
                getSavedDisplayName();


            if (savedModel) {

                const display =
                    savedDisplay ||
                    savedModel;


                updateModelButton(
                    display
                );


                updateCurrentModelRow(
                    display
                );

            } else {

                updateModelButton(
                    "Select model"
                );


                updateCurrentModelRow(
                    "Select model"
                );


                const check =
                    menu.querySelector(
                        ".model-check"
                    );


                if (check) {

                    check.style.visibility =
                        "hidden";

                }

            }

        }


        /* =====================================================
           EFFORT
        ===================================================== */

        const effortButton =
            menu.querySelector(
                ".model-effort-row"
            );


        function updateEffortUI(
            value
        ) {

            const valueElement =
                effortButton.querySelector(
                    ".effort-text"
                );


            if (valueElement) {

                valueElement.textContent =
                    value;

            }

        }


        function setSelectedEffort(
            value
        ) {

            const allowed = [
                "Low",
                "Medium",
                "High",
                "Max"
            ];


            if (
                !allowed.includes(
                    value
                )
            ) {

                value =
                    "Medium";

            }


            localStorage.setItem(
                EFFORT_KEY,
                value
            );


            updateEffortUI(
                value
            );


            console.log(
                "Entity effort selected:",
                value
            );

        }


        function restoreSelectedEffort() {

            setSelectedEffort(
                getSavedEffort()
            );

        }


        /* =====================================================
           OLLAMA MODELS MENU
        ===================================================== */

        const modelsMenu =
            document.createElement(
                "div"
            );


        modelsMenu.className =
            "entity-more-models-menu";


        document.body.appendChild(
            modelsMenu
        );


        async function loadOllamaModels() {

            modelsMenu.innerHTML = `

                <div class="ollama-loading">

                    <span
                        class="material-symbols-rounded"
                    >
                        progress_activity
                    </span>

                    Loading Ollama models...

                </div>

            `;


            try {

                const response =
                    await fetch(
                        "/api/models"
                    );


                if (!response.ok) {

                    throw new Error(
                        "Entity model API unavailable"
                    );

                }


                const data =
                    await response.json();


                const models =
                    data.models || [];


                if (
                    models.length === 0
                ) {

                    modelsMenu.innerHTML = `

                        <div class="ollama-empty">

                            <span
                                class="material-symbols-rounded"
                            >
                                smart_toy
                            </span>

                            No Ollama models found.

                        </div>

                    `;

                    return;

                }


                modelsMenu.innerHTML =
                    models
                        .map(
                            model => {

                                const name =
    typeof model === "string"
        ? model
        : (
            model.name ||
            model.model ||
            ""
        );


                                return `

                                    <button
                                        class="ollama-model-item"
                                        type="button"
                                        data-model="${name}"
                                    >

                                        <span>
                                            ${name}
                                        </span>

                                    </button>

                                `;

                            }
                        )
                        .join("");


                modelsMenu
                    .querySelectorAll(
                        ".ollama-model-item"
                    )
                    .forEach(
                        item => {

                            item.addEventListener(
                                "click",
                                function (event) {

                                    event.preventDefault();

                                    event.stopPropagation();


                                    const modelName =
                                        item.dataset.model;


                                    if (!modelName) {

                                        return;

                                    }


                                    setSelectedModel(
                                        modelName,
                                        modelName
                                    );


                                    modelsMenu.classList.remove(
                                        "show"
                                    );

                                    menu.classList.remove(
                                        "show"
                                    );

                                    modelButton.classList.remove(
                                        "open"
                                    );

                                }
                            );

                        }
                    );


            } catch (error) {

                console.error(
                    "Entity Ollama model loading error:",
                    error
                );


                modelsMenu.innerHTML = `

                    <div class="ollama-empty">

                        Unable to load Ollama models.

                    </div>

                `;

            }

        }


        /* =====================================================
           POSITION MODEL MENU
        ===================================================== */

        function positionModelMenu() {

            const rect =
                modelButton.getBoundingClientRect();


            const width =
                250;


            let left =
                rect.left;


            let top =
                rect.bottom + 8;


            if (
                left + width >
                window.innerWidth - 10
            ) {

                left =
                    window.innerWidth -
                    width -
                    10;

            }


            if (
                left < 10
            ) {

                left =
                    10;

            }


            menu.style.left =
                `${left}px`;


            menu.style.top =
                `${top}px`;

        }


        /* =====================================================
           POSITION MORE MODELS
        ===================================================== */

        function positionMoreModels() {

            const rect =
                menu.getBoundingClientRect();


            const width =
                260;


            let left =
                rect.right + 8;


            let top =
                rect.top;


            if (
                left + width >
                window.innerWidth - 10
            ) {

                left =
                    rect.left -
                    width -
                    8;

            }


            if (
                left < 10
            ) {

                left =
                    10;

            }


            if (
                top < 10
            ) {

                top =
                    10;

            }


            modelsMenu.style.left =
                `${left}px`;


            modelsMenu.style.top =
                `${top}px`;

        }


        /* =====================================================
           MODEL BUTTON CLICK
        ===================================================== */

        modelButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();


                const isOpen =
                    menu.classList.contains(
                        "show"
                    );


                if (isOpen) {

                    closeAllModelMenus();

                    return;

                }


                closeAllModelMenus();


                positionModelMenu();


                menu.classList.add(
                    "show"
                );


                modelButton.classList.add(
                    "open"
                );

            }
        );


        /* =====================================================
           MORE MODELS
        ===================================================== */

        const moreModelsButton =
            menu.querySelector(
                ".more-models-row"
            );


        moreModelsButton.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();

                event.stopPropagation();


                const isOpen =
                    modelsMenu.classList.contains(
                        "show"
                    );


                if (isOpen) {

                    modelsMenu.classList.remove(
                        "show"
                    );

                    return;

                }


                positionMoreModels();


                modelsMenu.classList.add(
                    "show"
                );


                await loadOllamaModels();


                positionMoreModels();

            }
        );


        /* =====================================================
           EFFORT MENU
        ===================================================== */

        effortButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();


                const existing =
                    document.querySelector(
                        ".entity-effort-menu"
                    );


                if (existing) {

                    existing.remove();

                    return;

                }


                const effortMenu =
                    document.createElement(
                        "div"
                    );


                effortMenu.className =
                    "entity-effort-menu";


                const currentEffort =
                    getSavedEffort();


                effortMenu.innerHTML = `

                    <button
                        class="effort-option ${
                            currentEffort === "Low"
                                ? "selected"
                                : ""
                        }"
                        type="button"
                        data-effort="Low"
                    >

                        <span>
                            Low
                        </span>

                        <span
                            class="material-symbols-rounded"
                        >
                            ${
                                currentEffort === "Low"
                                    ? "check"
                                    : ""
                            }
                        </span>

                    </button>


                    <button
                        class="effort-option ${
                            currentEffort === "Medium"
                                ? "selected"
                                : ""
                        }"
                        type="button"
                        data-effort="Medium"
                    >

                        <span>
                            Medium
                        </span>

                        <span
                            class="material-symbols-rounded"
                        >
                            ${
                                currentEffort === "Medium"
                                    ? "check"
                                    : ""
                            }
                        </span>

                    </button>


                    <button
                        class="effort-option ${
                            currentEffort === "High"
                                ? "selected"
                                : ""
                        }"
                        type="button"
                        data-effort="High"
                    >

                        <span>
                            High
                        </span>

                        <span
                            class="material-symbols-rounded"
                        >
                            ${
                                currentEffort === "High"
                                    ? "check"
                                    : ""
                            }
                        </span>

                    </button>


                    <button
                        class="effort-option ${
                            currentEffort === "Max"
                                ? "selected"
                                : ""
                        }"
                        type="button"
                        data-effort="Max"
                    >

                        <span>
                            Max
                        </span>

                        <span
                            class="material-symbols-rounded"
                        >
                            ${
                                currentEffort === "Max"
                                    ? "check"
                                    : ""
                            }
                        </span>

                    </button>

                `;


                document.body.appendChild(
                    effortMenu
                );


                const rect =
                    effortButton.getBoundingClientRect();


                const width =
                    180;


                let left =
                    rect.right -
                    width;


                let top =
                    rect.top;


                if (
                    left < 10
                ) {

                    left =
                        10;

                }


                if (
                    top + 190 >
                    window.innerHeight -
                    10
                ) {

                    top =
                        window.innerHeight -
                        200;

                }


                effortMenu.style.left =
                    `${left}px`;


                effortMenu.style.top =
                    `${top}px`;


                effortMenu.classList.add(
                    "show"
                );


                effortMenu
                    .querySelectorAll(
                        ".effort-option"
                    )
                    .forEach(
                        option => {

                            option.addEventListener(
                                "click",
                                function (clickEvent) {

                                    clickEvent.preventDefault();

                                    clickEvent.stopPropagation();


                                    const value =
                                        option.dataset.effort;


                                    setSelectedEffort(
                                        value
                                    );


                                    effortMenu
                                        .querySelectorAll(
                                            ".effort-option"
                                        )
                                        .forEach(
                                            item => {

                                                item.classList.remove(
                                                    "selected"
                                                );


                                                const icon =
                                                    item.querySelector(
                                                        ".material-symbols-rounded"
                                                    );


                                                if (icon) {

                                                    icon.textContent =
                                                        "";

                                                }

                                            }
                                        );


                                    option.classList.add(
                                        "selected"
                                    );


                                    const icon =
                                        option.querySelector(
                                            ".material-symbols-rounded"
                                        );


                                    if (icon) {

                                        icon.textContent =
                                            "check";

                                    }


                                    setTimeout(
                                        () => {

                                            effortMenu.remove();

                                        },
                                        120
                                    );

                                }
                            );

                        }
                    );

            }
        );


        /* =====================================================
           CLOSE ALL MODEL MENUS
        ===================================================== */

        function closeAllModelMenus() {

            menu.classList.remove(
                "show"
            );


            modelsMenu.classList.remove(
                "show"
            );


            modelButton.classList.remove(
                "open"
            );


            const effortMenu =
                document.querySelector(
                    ".entity-effort-menu"
                );


            if (effortMenu) {

                effortMenu.remove();

            }

        }


        /* =====================================================
           CLICK OUTSIDE MODEL MENUS
        ===================================================== */

        document.addEventListener(
            "click",
            function (event) {

                const effortMenu =
                    document.querySelector(
                        ".entity-effort-menu"
                    );


                if (
                    !menu.contains(
                        event.target
                    ) &&

                    !modelsMenu.contains(
                        event.target
                    ) &&

                    !modelButton.contains(
                        event.target
                    ) &&

                    !effortButton.contains(
                        event.target
                    ) &&

                    !(
                        effortMenu &&
                        effortMenu.contains(
                            event.target
                        )
                    )
                ) {

                    closeAllModelMenus();

                }

            }
        );


        /* =====================================================
           RESIZE
        ===================================================== */

        window.addEventListener(
            "resize",
            function () {

                if (
                    menu.classList.contains(
                        "show"
                    )
                ) {

                    positionModelMenu();

                }


                if (
                    modelsMenu.classList.contains(
                        "show"
                    )
                ) {

                    positionMoreModels();

                }

            }
        );


        /* =====================================================
           INITIAL RESTORE
        ===================================================== */

        restoreSelectedModel();

        restoreSelectedEffort();


        console.log(
            "Entity model dropdown loaded successfully"
        );


        /* =====================================================
           MODEL SYSTEM API
        ===================================================== */

        window.EntityModel = {

            getModel: function () {

                return getSavedModel();

            },


            getDisplayName: function () {

                return getSavedDisplayName();

            },


            getEffort: function () {

                return getSavedEffort();

            },


            setModel: function (
                modelName,
                displayName
            ) {

                setSelectedModel(
                    modelName,
                    displayName
                );

            },


            setEffort: function (
                effort
            ) {

                setSelectedEffort(
                    effort
                );

            }

        };


    })();


    /* =========================================================
       ENTITY CHAT SYSTEM
    ========================================================= */

    (function () {

        console.log(
            "Entity Chat system loaded."
        );


        const textarea =
            document.getElementById(
                "messageInput"
            );


        if (!textarea) {

            console.error(
                "Entity: messageInput not found."
            );

            return;

        }


        let isSending =
            false;


        let currentConversationId =
            localStorage.getItem(
                "entity_conversation_id"
            ) || null;


        if (!currentConversationId) {

            currentConversationId =
                crypto.randomUUID();


            localStorage.setItem(
                "entity_conversation_id",
                currentConversationId
            );

        }


        let messages = [];


        try {

            const savedMessages =
                localStorage.getItem(
                    "entity_messages"
                );


            if (savedMessages) {

                messages =
                    JSON.parse(
                        savedMessages
                    );

            }

        } catch (error) {

            console.warn(
                "Entity: Could not restore messages.",
                error
            );


            messages = [];

        }


        /* =====================================================
           HELPERS
        ===================================================== */

        function getSelectedModel() {

            if (
                window.EntityModel &&
                typeof window.EntityModel.getModel ===
                    "function"
            ) {

                return (
                    window.EntityModel.getModel() ||
                    "qwen3:4b"
                );

            }


            return (
                localStorage.getItem(
                    "entity_ollama_model"
                ) ||
                "qwen3:4b"
            );

        }


        function getSelectedEffort() {

            if (
                window.EntityModel &&
                typeof window.EntityModel.getEffort ===
                    "function"
            ) {

                return (
                    window.EntityModel.getEffort() ||
                    "Medium"
                );

            }


            return (
                localStorage.getItem(
                    "entity_effort"
                ) ||
                "Medium"
            );

        }


        function saveMessages() {

            try {

                localStorage.setItem(
                    "entity_messages",
                    JSON.stringify(
                        messages
                    )
                );

            } catch (error) {

                console.warn(
                    "Entity: Could not save messages.",
                    error
                );

            }

        }


        function addMessageToHistory(
            role,
            content
        ) {

            messages.push({

                role:
                    role,

                content:
                    content

            });


            saveMessages();

        }


        function clearHistory() {

            messages = [];


            localStorage.removeItem(
                "entity_messages"
            );

        }


        /* =====================================================
           FIND CHAT CONTAINER
        ===================================================== */

        function getChatContainer() {

            let container =
                document.querySelector(
                    ".chat-messages"
                );


            if (!container) {

                container =
                    document.querySelector(
                        ".messages"
                    );

            }


            if (!container) {

                container =
                    document.querySelector(
                        ".chat-container"
                    );

            }


            if (!container) {

                container =
                    document.querySelector(
                        ".home"
                    );

            }


            return container;

        }


        /* =====================================================
           CREATE MESSAGE ELEMENT
        ===================================================== */

        function createMessageElement(
            role,
            content = ""
        ) {

            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.className =
                role === "user"
                    ? "entity-user-message"
                    : "entity-assistant-message";


            const contentElement =
                document.createElement(
                    "div"
                );


            contentElement.className =
                "entity-message-content";


            contentElement.textContent =
                content;


            wrapper.appendChild(
                contentElement
            );


            const container =
                getChatContainer();


            if (container) {

                container.appendChild(
                    wrapper
                );

            }


            return {

                wrapper:
                    wrapper,

                content:
                    contentElement

            };

        }


        /* =====================================================
           THINKING MESSAGE
        ===================================================== */

        function createThinkingMessage() {

            const message =
                createMessageElement(
                    "assistant",
                    ""
                );


            message.wrapper.classList.add(
                "entity-thinking-message"
            );


            message.content.innerHTML = `

                <span class="entity-thinking-dots">

                    <span></span>
                    <span></span>
                    <span></span>

                </span>

            `;


            scrollToBottom();


            return message;

        }


        /* =====================================================
           SCROLL
        ===================================================== */

        function scrollToBottom() {

            const container =
                getChatContainer();


            if (container) {

                container.scrollTop =
                    container.scrollHeight;

            }


            window.scrollTo(
                0,
                document.body.scrollHeight
            );

        }


        /* =====================================================
           FAST WORD-BY-WORD TYPING
        ===================================================== */

        async function entityTypeWords(
            element,
            text
        ) {

            if (!element) {

                return;

            }


            element.textContent =
                "";


            const words =
                String(text || "")
                    .split(/(\s+)/);


            for (
                let i = 0;
                i < words.length;
                i++
            ) {

                element.textContent +=
                    words[i];


                scrollToBottom();


                await new Promise(
                    resolve =>
                        setTimeout(
                            resolve,
                            18
                        )
                );

            }

        }


        /* =====================================================
           SEND TO ENTITY / OLLAMA
        ===================================================== */

        async function sendToOllama(
            userMessage
        ) {

            const model =
                getSelectedModel();


            const effort =
                getSelectedEffort();


            console.log(
                "Entity selected Ollama model:",
                model
            );


            console.log(
                "Entity effort:",
                effort
            );


            const thinking =
                createThinkingMessage();


            try {

                const response =
                    await fetch(
                        "/api/chat",
                        {

                            method:
                                "POST",

                            headers: {

                                "Content-Type":
                                    "application/json"

                            },

                            body:
                                JSON.stringify({

                                    model:
                                        model,

                                    message:
                                        userMessage,

                                    effort:
                                        effort,

                                    history:
                                        messages,

                                    conversation_id:
                                        currentConversationId

                                })

                        }
                    );


                if (!response.ok) {

                    throw new Error(
                        "Entity API request failed."
                    );

                }


                if (thinking.wrapper) {

                    thinking.wrapper.remove();

                }


                const assistant =
                    createMessageElement(
                        "assistant",
                        ""
                    );


                let fullResponse =
                    "";


                /* =================================================
                   STREAM RESPONSE
                ================================================= */

                if (
                    response.body &&
                    response.body.getReader
                ) {

                    const reader =
                        response.body.getReader();


                    const decoder =
                        new TextDecoder(
                            "utf-8"
                        );


                    let buffer =
                        "";


                    while (true) {

                        const {
                            value,
                            done
                        } =
                            await reader.read();


                        if (done) {

                            break;

                        }


                        buffer +=
                            decoder.decode(
                                value,
                                {
                                    stream:
                                        true
                                }
                            );


                        const chunks =
                            buffer.split(
                                "\n"
                            );


                        buffer =
                            chunks.pop() || "";


                        for (
                            const chunk
                            of chunks
                        ) {

                            if (!chunk.trim()) {

                                continue;

                            }


                            let parsed =
                                null;


                            try {

                                parsed =
                                    JSON.parse(
                                        chunk
                                    );

                            } catch (error) {

                                parsed =
                                    null;

                            }


                            if (
                                parsed &&
                                typeof parsed.response ===
                                    "string"
                            ) {

                                fullResponse +=
                                    parsed.response;

                            } else {

                                fullResponse +=
                                    chunk;

                            }

                        }

                    }


                    if (buffer.trim()) {

                        try {

                            const parsed =
                                JSON.parse(
                                    buffer
                                );


                            if (
                                parsed &&
                                typeof parsed.response ===
                                    "string"
                            ) {

                                fullResponse +=
                                    parsed.response;

                            } else {

                                fullResponse +=
                                    buffer;

                            }

                        } catch (error) {

                            fullResponse +=
                                buffer;

                        }

                    }


                } else {

                    fullResponse =
                        await response.text();

                }


                /* =================================================
                   WORD-BY-WORD OUTPUT
                ================================================= */

                await entityTypeWords(
                    assistant.content,
                    fullResponse
                 );

                 

if (
    response.headers.get("X-Entity-Source") === "TMDB"
) {

    const raw = fullResponse;

    const titleMatch =
        raw.match(/🎬\s*(.*?)(?=\s*📅)/s);

    const dateMatch =
        raw.match(/📅\s*Release date:\s*(.*?)(?=\s*⭐)/s);

    const ratingMatch =
        raw.match(/⭐\s*Rating:\s*(.*?)(?=\s*📝)/s);

    const posterMatch =
        raw.match(/🖼️\s*Poster:\s*(https?:\/\/\S+)/i);

    const title =
        titleMatch
            ? titleMatch[1].trim()
            : "Movie";

    const releaseDate =
        dateMatch
            ? dateMatch[1].trim()
            : "";

    const rating =
        ratingMatch
            ? ratingMatch[1].trim()
            : "";

    const poster =
        posterMatch
            ? posterMatch[1].trim()
            : "";

    let overview = raw;

    overview =
        overview
            .replace(/🎬\s*.*?(?=\s*📅)/s, "")
            .replace(/📅\s*Release date:\s*.*?(?=\s*⭐)/s, "")
            .replace(/⭐\s*Rating:\s*.*?(?=\s*📝)/s, "")
            .replace(/📝\s*/g, "")
            .replace(/🖼️\s*Poster:\s*https?:\/\/\S+/gi, "")
            .replace(/Source:\s*TMDB/gi, "")
            .trim();


    assistant.content.innerHTML = "";

    const card =
        document.createElement("div");

    card.className =
        "entity-tmdb-card";

    card.style.cssText =
        `
        display: flex;
        gap: 18px;
        padding: 18px;
        border: 1px solid #333;
        border-radius: 16px;
        background: #1f1f1f;
        max-width: 850px;
        `;


    if (poster) {

        const image =
            document.createElement("img");

        image.src =
            poster;

        image.alt =
            title;

        image.style.cssText =
            `
            width: 150px;
            height: 225px;
            object-fit: cover;
            border-radius: 12px;
            `;

        card.appendChild(image);

    }


    const details =
        document.createElement("div");

    details.style.flex =
        "1";


    const heading =
        document.createElement("div");

    heading.textContent =
        "🎬 " + title;

    heading.style.cssText =
        `
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 12px;
        `;


    const meta =
        document.createElement("div");

    meta.textContent =
        "📅 " +
        releaseDate +
        "    ⭐ " +
        rating;

    meta.style.cssText =
        `
        color: #cccccc;
        margin-bottom: 15px;
        `;


    const description =
        document.createElement("div");

    description.textContent =
        overview;

    description.style.cssText =
        `
        line-height: 1.7;
        `;


    const source =
        document.createElement("div");

    source.textContent =
        "Powered by TMDB";

    source.style.cssText =
        `
        margin-top: 18px;
        font-size: 12px;
        color: #888;
        `;


    details.appendChild(heading);
    details.appendChild(meta);
    details.appendChild(description);
    details.appendChild(source);

    card.appendChild(details);

    assistant.content.appendChild(card);

}

                addMessageToHistory(
                    "user",
                    userMessage
                );


                addMessageToHistory(
                    "assistant",
                    fullResponse
                );


                if (
                    window.EntityVoice &&
                    window.EntityVoice.enabled()
                ) {

                    window.EntityVoice.speak(
                        fullResponse
                    );

                }


            } catch (error) {

                console.error(
                    "Entity chat error:",
                    error
                );


                if (thinking.wrapper) {

                    thinking.wrapper.remove();

                }


                const errorMessage =
                    createMessageElement(
                        "assistant",
                        "Sorry, something went wrong."
                    );


                scrollToBottom();

            }

        }


        /* =====================================================
           SEND MESSAGE
        ===================================================== */

        async function sendMessage() {

    if (window.entitySendingLock) {
        return;
    }

    window.entitySendingLock = true;

    try {

        const userMessage =
            textarea.value.trim();

        if (!userMessage) {
            return;
        }

        textarea.value = "";
        textarea.style.height = "auto";

        createMessageElement(
            "user",
            userMessage
        );

        scrollToBottom();

        await sendToOllama(
            userMessage
        );

    } finally {

        window.entitySendingLock = false;

    }
}

        

            


        /* =====================================================
           ENTER TO SEND
        ===================================================== */

        textarea.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    sendMessage();

                }

            }
        );


        /* =====================================================
           SEND BUTTON
        ===================================================== */

        const sendButton =
            document.querySelector(
                ".send-btn"
            ) ||
            document.getElementById(
                "sendButton"
            );


        if (sendButton) {

            sendButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    sendMessage();

                }
            );

        }


        /* =====================================================
           CLEAR CHAT
        ===================================================== */

        const clearButton =
            document.querySelector(
                ".clear-chat"
            );


        if (clearButton) {

            clearButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    clearHistory();


                    const container =
                        getChatContainer();


                    if (container) {

                        container.innerHTML =
                            "";

                    }

                }
            );

        }


        console.log(
            "Entity Chat system ready."
        );

    })();

});

/* =========================================================
   ENTITY VOICE INPUT
========================================================= */

(function () {

    const micButton =
        document.querySelector(".mic-btn");


    if (!micButton) {
        return;
    }


    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    if (!SpeechRecognition) {

        console.warn(
            "Entity: Speech Recognition is not supported."
        );

        return;
    }


    const recognition =
        new SpeechRecognition();


    recognition.lang =
        "en-IN";


    recognition.continuous =
        false;


    recognition.interimResults =
        true;


    let listening =
        false;


    micButton.addEventListener(
        "click",
        event => {

            event.preventDefault();

            event.stopPropagation();


            if (listening) {

                recognition.stop();

                return;

            }

            try {

                recognition.start();

            } catch (error) {

                console.warn(
                    "Entity microphone:",
                    error
                );

            }

        }
    );


    recognition.onstart =
        () => {

            listening =
                true;


            micButton.classList.add(
                "recording"
            );


            console.log(
                "Entity microphone started."
            );

        };


    recognition.onresult =
        event => {

            let transcript =
                "";


            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {

                transcript +=
                    event.results[i][0]
                        .transcript;

            }


            if (input) {

                input.value =
                    transcript;


                input.style.height =
                    "auto";


                input.style.height =
                    Math.min(
                        input.scrollHeight,
                        90
                    ) + "px";

            }

        };


    recognition.onerror =
        event => {

            console.error(
                "Entity speech recognition error:",
                event.error
            );

        };


    recognition.onend =
        () => {

            listening =
                false;


            micButton.classList.remove(
                "recording"
            );


            console.log(
                "Entity microphone stopped."
            );

        };


})();


/* =========================================================
   ENTITY VOICE MODE
========================================================= */

(function () {

    const waveButton =
        document.querySelector(
            ".wave-btn"
        );


    if (!waveButton) {
        return;
    }


    let voiceMode =
        false;


    waveButton.addEventListener(
        "click",
        event => {

            event.preventDefault();

            event.stopPropagation();


            voiceMode =
                !voiceMode;


            waveButton.classList.toggle(
                "active",
                voiceMode
            );


            console.log(
                "Entity voice mode:",
                voiceMode
            );


            if (
                "speechSynthesis"
                in window &&
                !voiceMode
            ) {

                window.speechSynthesis.cancel();

            }

        }
    );


    window.EntityVoice = {

        enabled:
            function () {

                return voiceMode;

            },


        speak:
            function (text) {

                if (
                    !voiceMode ||
                    !(
                        "speechSynthesis"
                        in window
                    )
                ) {

                    return;

                }


                if (!text) {
                    return;
                }


                window.speechSynthesis.cancel();


                const utterance =
                    new SpeechSynthesisUtterance(
                        text
                    );


                utterance.lang =
                    "en-IN";


                utterance.rate =
                    1;


                utterance.pitch =
                    1;


                window.speechSynthesis.speak(
                    utterance
                );

            }

    };


})();


/* =========================================================
   ADD MENU FILE INPUT
========================================================= */

(function () {

    const addMenu =
        document.getElementById(
            "entityAddMenu"
        );


    if (!addMenu) {
        return;
    }


    const fileInput =
        document.createElement(
            "input"
        );


    fileInput.type =
        "file";


    fileInput.multiple =
        true;


    fileInput.accept =
        "*/*";


    fileInput.style.display =
        "none";


    document.body.appendChild(
        fileInput
    );


    const fileButton =
        Array.from(
            addMenu.querySelectorAll(
                ".add-menu-item"
            )
        ).find(
            button =>
                button.textContent
                    .toLowerCase()
                    .includes(
                        "add files"
                    )
        );


    if (fileButton) {

        fileButton.addEventListener(
            "click",
            event => {

                event.preventDefault();

                event.stopPropagation();


                fileInput.click();

            }
        );

    }


    fileInput.addEventListener(
        "change",
        event => {

            const files =
                Array.from(
                    event.target.files
                );


            if (!files.length) {
                return;
            }


            console.log(
                "Entity selected files:",
                files
            );


            /*
             * File upload backend will be
             * connected later.
             *
             * For now Entity keeps the
             * selected files available
             * in the browser.
             */


            window.EntityFiles =
                files;


            fileInput.value =
                "";

        }
    );


})();


/* =========================================================
   ENTITY PAGE READY
========================================================= */

console.log(
    "=========================================="
);


console.log(
    "        ENTITY AI READY"
);


console.log(
    "=========================================="
);


console.log(
    "Ollama model:",
    localStorage.getItem(
        "entity_ollama_model"
    ) || "qwen3:4b"
);


console.log(
    "Entity effort:",
    localStorage.getItem(
        "entity_effort"
    ) || "Medium"
);


console.log(
    "=========================================="
);


/* =========================================================
   ENTITY - FINAL CODE BLOCK FORMAT FIX
========================================================= */

(function () {

    function entityFixCodeBlocks(root) {

        if (!root) {
            return;
        }


        const blocks =
            root.querySelectorAll(
                ".entity-code-block"
            );


        blocks.forEach(function (block) {

            const pre =
                block.querySelector(
                    "pre"
                );


            const code =
                block.querySelector(
                    "pre code"
                );


            if (!pre || !code) {
                return;
            }


            if (
                block.dataset.entityCodeFixed ===
                "true"
            ) {

                return;

            }


            block.dataset.entityCodeFixed =
                "true";


            let language =
                block.querySelector(
                    ".entity-code-language"
                );


            let languageText =
                language
                    ? language.textContent.trim()
                    : "code";


            const codeText =
                code.textContent || "";


            block.innerHTML =
                "";


            const header =
                document.createElement(
                    "div"
                );


            header.className =
                "entity-code-header";


            const lang =
                document.createElement(
                    "span"
                );


            lang.className =
                "entity-code-language";


            lang.textContent =
                languageText ||
                "code";


            const copy =
                document.createElement(
                    "button"
                );


            copy.type =
                "button";


            copy.className =
                "entity-copy-code";


            copy.textContent =
                "Copy";


            copy.addEventListener(
                "click",
                async function () {

                    try {

                        await navigator.clipboard.writeText(
                            codeText
                        );


                        const oldText =
                            copy.textContent;


                        copy.textContent =
                            "Copied";


                        copy.classList.add(
                            "copied"
                        );


                        setTimeout(
                            function () {

                                copy.textContent =
                                    oldText;


                                copy.classList.remove(
                                    "copied"
                                );

                            },
                            1500
                        );


                    } catch (error) {

                        console.error(
                            "ENTITY code copy error:",
                            error
                        );

                    }

                }
            );


            header.appendChild(
                lang
            );


            header.appendChild(
                copy
            );


            const newPre =
                document.createElement(
                    "pre"
                );


            const newCode =
                document.createElement(
                    "code"
                );


            newCode.textContent =
                codeText;


            newPre.appendChild(
                newCode
            );


            block.appendChild(
                header
            );


            block.appendChild(
                newPre
            );

        });

    }


    const observer =
        new MutationObserver(
            function (mutations) {

                mutations.forEach(
                    function (mutation) {

                        mutation.addedNodes.forEach(
                            function (node) {

                                if (
                                    node.nodeType !== 1
                                ) {

                                    return;

                                }


                                if (
                                    node.matches &&
                                    node.matches(
                                        ".entity-code-block"
                                    )
                                ) {

                                    entityFixCodeBlocks(
                                        node.parentElement ||
                                        node
                                    );


                                    return;

                                }


                                entityFixCodeBlocks(
                                    node
                                );

                            }
                        );

                    }
                );

            }
        );


    observer.observe(
        document.body,
        {
            childList: true,
            subtree: true
        }
    );


    document.addEventListener(
        "DOMContentLoaded",
        function () {

            entityFixCodeBlocks(
                document
            );

        }
    );


})();


/* =========================================================
   ENTITY INDEX2 - FINAL CODE BLOCK FIX
========================================================= */

(function () {

    function fixEntityCodeBlocks() {

        const blocks =
            document.querySelectorAll(
                ".code-block-wrap"
            );


        blocks.forEach(function (block) {

            if (
                block.dataset.entityFixed ===
                "1"
            ) {

                return;

            }


            const head =
                block.querySelector(
                    ".code-block-head"
                );


            const pre =
                block.querySelector(
                    "pre"
                );


            const code =
                block.querySelector(
                    "pre code"
                );


            if (
                !head ||
                !pre ||
                !code
            ) {

                return;

            }


            let cleanCode =
                code.textContent || "";


            cleanCode =
                cleanCode.replace(
                    /^\s*\n/,
                    ""
                );


            cleanCode =
                cleanCode.replace(
                    /\n\s*$/,
                    ""
                );


            cleanCode =
                cleanCode.replace(
                    /\r\n/g,
                    "\n"
                );


            code.textContent =
                cleanCode;


            block.classList.add(
                "entity-code-block"
            );


            head.classList.add(
                "entity-code-header"
            );


            const language =
                head.querySelector(
                    "span"
                );


            if (language) {

                language.classList.add(
                    "entity-code-language"
                );

            }


            const copy =
                head.querySelector(
                    ".code-copy-button"
                );


            if (copy) {

                copy.classList.add(
                    "entity-copy-code"
                );


                copy.type =
                    "button";

            }


            block.dataset.entityFixed =
                "1";

        });

    }


    /* =============================================
       FORCE FINAL CODE CSS
    ============================================= */

    const style =
        document.createElement(
            "style"
        );


    style.id =
        "entity-final-code-style";


    style.textContent = `

        .code-block-wrap.entity-code-block {

            display: block !important;

            position: relative !important;

            width: 100% !important;

            max-width: 100% !important;

            height: auto !important;

            min-height: 0 !important;

            margin: 16px 0 !important;

            padding: 0 !important;

            box-sizing: border-box !important;

            overflow: hidden !important;

            background: #181818 !important;

            border: 1px solid #383838 !important;

            border-radius: 10px !important;

        }


        .code-block-wrap.entity-code-block
        .code-block-head {

            width: 100% !important;

            height: 38px !important;

            min-height: 38px !important;

            display: flex !important;

            align-items: center !important;

            justify-content: space-between !important;

            box-sizing: border-box !important;

            margin: 0 !important;

            padding: 0 10px !important;

            background: #242424 !important;

            border: 0 !important;

            border-bottom: 1px solid #383838 !important;

        }


        .code-block-wrap.entity-code-block
        pre {

            display: block !important;

            width: 100% !important;

            max-width: 100% !important;

            margin: 0 !important;

            padding: 14px !important;

            box-sizing: border-box !important;

            overflow-x: auto !important;

            overflow-y: auto !important;

            background: #181818 !important;

            border: 0 !important;

            white-space: pre !important;

        }


        .code-block-wrap.entity-code-block
        pre code {

            display: block !important;

            width: max-content !important;

            min-width: 100% !important;

            margin: 0 !important;

            padding: 0 !important;

            background: transparent !important;

            white-space: pre !important;

            font-family:
                Consolas,
                "Courier New",
                monospace !important;

            font-size: 13px !important;

            line-height: 1.55 !important;

        }


        .entity-code-language {

            font-size: 12px !important;

            font-weight: 600 !important;

        }


        .entity-copy-code {

            border: 0 !important;

            cursor: pointer !important;

            padding: 5px 9px !important;

            border-radius: 6px !important;

            background: transparent !important;

        }


        .entity-copy-code:hover {

            background: #333333 !important;

        }

    `;


    document.head.appendChild(
        style
    );


    const observer =
        new MutationObserver(
            function () {

                fixEntityCodeBlocks();

            }
        );


    observer.observe(
        document.body,
        {
            childList: true,
            subtree: true
        }
    );


    fixEntityCodeBlocks();


})();


/* =========================================================
   ENTITY EXTRA UI HELPERS
========================================================= */

(function () {

    function safeText(
        value
    ) {

        return String(
            value || ""
        ).trim();

    }


    window.EntityUI = {

        scrollBottom:
            function () {

                const container =
                    document.querySelector(
                        ".chat-messages"
                    ) ||
                    document.querySelector(
                        ".messages"
                    ) ||
                    document.querySelector(
                        ".chat-container"
                    );


                if (container) {

                    container.scrollTop =
                        container.scrollHeight;

                }

            },


        getGreeting:
            function () {

                const hour =
                    new Date().getHours();


                if (
                    hour >= 5 &&
                    hour < 12
                ) {

                    return "Good morning";

                }


                if (
                    hour >= 12 &&
                    hour < 17
                ) {

                    return "Good afternoon";

                }


                if (
                    hour >= 17 &&
                    hour < 21
                ) {

                    return "Good evening";

                }


                return "Good night";

            },


        cleanText:
            function (text) {

                return safeText(
                    text
                );

            }

    };


})();

/* =========================================================
   ENTITY FINAL INITIALIZATION
========================================================= */

(function () {

    function initializeEntity() {

        console.log(
            "Entity final initialization..."
        );


        /* =============================================
           RESTORE TEXTAREA HEIGHT
        ============================================= */

        const textarea =
            document.getElementById(
                "messageInput"
            );


        if (textarea) {

            textarea.style.height =
                "auto";

        }


        /* =============================================
           RESTORE GREETING
        ============================================= */

        if (
            window.EntityUI &&
            typeof window.EntityUI.getGreeting ===
                "function"
        ) {

            const greeting =
                window.EntityUI.getGreeting();


            document
                .querySelectorAll(
                    ".greeting, .welcome-title, .welcome-message, .hero-title, .hero-greeting, #greeting, #welcomeGreeting"
                )
                .forEach(
                    element => {

                        const text =
                            element.textContent ||
                            "";


                        if (
                            /good\s+(morning|afternoon|evening|night)/i
                                .test(text)
                        ) {

                            const walker =
                                document.createTreeWalker(
                                    element,
                                    NodeFilter.SHOW_TEXT
                                );

                            let node;

                            while (
                                (node = walker.nextNode())
                            ) {

                                if (
                                    /good\s+(morning|afternoon|evening|night)/i
                                        .test(node.nodeValue || "")
                                ) {

                                    node.nodeValue =
                                        (node.nodeValue || "").replace(
                                            /good\s+(morning|afternoon|evening|night)/i,
                                            greeting
                                        );

                                    break;

                                }

                            }

                        }

                    }
                );

        }


        console.log(
            "Entity initialization complete."
        );

    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initializeEntity
        );

    } else {

        initializeEntity();

    }


})();


/* =========================================================
   ENTITY KEYBOARD SHORTCUTS
========================================================= */

(function () {

    document.addEventListener(
        "keydown",
        function (event) {

            /* =========================================
               CTRL + U
               Open file picker
            ========================================= */

            if (
                event.ctrlKey &&
                event.key.toLowerCase() === "u"
            ) {

                event.preventDefault();


                const fileInput =
                    document.querySelector(
                        'input[type="file"]'
                    );


                if (fileInput) {

                    fileInput.click();

                }

            }


            /* =========================================
               ESC
               Close menus
            ========================================= */

            if (
                event.key ===
                "Escape"
            ) {

                document
                    .querySelectorAll(
                        ".entity-model-menu.show, .entity-more-models-menu.show, .entity-effort-menu.show"
                    )
                    .forEach(
                        element => {

                            element.classList.remove(
                                "show"
                            );

                        }
                    );


                document
                    .querySelectorAll(
                        ".entity-add-menu.visible"
                    )
                    .forEach(
                        element => {

                            element.classList.remove(
                                "visible"
                            );

                        }
                    );

            }

        }
    );

})();


/* =========================================================
   ENTITY CONNECTION STATUS
========================================================= */

(function () {

    async function checkEntityConnection() {

        try {

            const response =
                await fetch(
                    "/api/models",
                    {
                        method:
                            "GET",
                        cache:
                            "no-store"
                    }
                );


            if (
                response.ok
            ) {

                document.body.classList.add(
                    "entity-online"
                );


                document.body.classList.remove(
                    "entity-offline"
                );


                console.log(
                    "Entity backend: ONLINE"
                );

            } else {

                throw new Error(
                    "Backend unavailable"
                );

            }

        } catch (error) {

            document.body.classList.add(
                "entity-offline"
            );


            document.body.classList.remove(
                "entity-online"
            );


            console.warn(
                "Entity backend: OFFLINE"
            );

        }

    }


    checkEntityConnection();


    setInterval(
        checkEntityConnection,
        30000
    );


})();


/* =========================================================
   ENTITY LOCAL STORAGE SAFETY
========================================================= */

(function () {

    const defaults = {

        "entity_effort":
            "Medium",

        "entity_messages":
            "[]"

    };


    Object.keys(
        defaults
    ).forEach(
        key => {

            if (
                localStorage.getItem(
                    key
                ) === null
            ) {

                localStorage.setItem(
                    key,
                    defaults[key]
                );

            }

        }
    );


})();


/* =========================================================
   ENTITY RESPONSE FORMAT HELPERS
========================================================= */

(function () {

    window.EntityFormat = {

        normalize:
            function (text) {

                if (
                    text === null ||
                    text === undefined
                ) {

                    return "";

                }


                return String(
                    text
                )
                .replace(
                    /\r\n/g,
                    "\n"
                )
                .replace(
                    /\r/g,
                    "\n"
                );

            },


        isCode:
            function (text) {

                const value =
                    String(
                        text || ""
                    );


                return (
                    value.includes(
                        "```"
                    ) ||
                    value.includes(
                        "<pre"
                    ) ||
                    value.includes(
                        "<code"
                    )
                );

            },


        clean:
            function (text) {

                return this
                    .normalize(
                        text
                    )
                    .trim();

            }

    };

})();


/* =========================================================
   ENTITY CHAT RESTORE
========================================================= */

(function () {

    function restoreEntityMessages() {

        let saved;


        try {

            saved =
                localStorage.getItem(
                    "entity_messages"
                );


        } catch (error) {

            console.warn(
                "Entity history read error:",
                error
            );


            return;

        }


        if (!saved) {

            return;

        }


        let parsed;


        try {

            parsed =
                JSON.parse(
                    saved
                );

        } catch (error) {

            console.warn(
                "Entity history parse error:",
                error
            );


            return;

        }


        if (
            !Array.isArray(
                parsed
            )
        ) {

            return;

        }


        const container =
    document.querySelector(
        ".chat-messages"
    ) ||
    document.querySelector(
        ".messages"
    );


        if (!container) {

            return;

        }


        /*
         * Do not duplicate messages if
         * the chat system already rendered them.
         */

        if (
            container.children.length >
            0
        ) {

            return;

        }


        parsed.forEach(
            message => {

                if (
                    !message ||
                    !message.role
                ) {

                    return;

                }


                const wrapper =
                    document.createElement(
                        "div"
                    );


                wrapper.className =
                    message.role ===
                    "user"

                        ? "entity-user-message"

                        : "entity-assistant-message";


                const content =
                    document.createElement(
                        "div"
                    );


                content.className =
                    "entity-message-content";


                content.textContent =
                    message.content ||
                    "";


                wrapper.appendChild(
                    content
                );


                container.appendChild(
                    wrapper
                );

            }
        );


        if (
            window.EntityUI &&
            typeof window.EntityUI.scrollBottom ===
                "function"
        ) {

            window.EntityUI.scrollBottom();

        }

    }


    /*
     * Wait briefly so the main chat
     * initialization can finish first.
     */

    setTimeout(
        restoreEntityMessages,
        150
    );


})();


/* =========================================================
   ENTITY GREETING OBSERVER
   Handles greeting elements added later by HTML/JS
========================================================= */

(function () {

    function updateDynamicGreeting() {

        if (
            !window.EntityUI ||
            typeof window.EntityUI.getGreeting !==
                "function"
        ) {

            return;

        }


        const greeting =
            window.EntityUI.getGreeting();


        const elements =
            document.querySelectorAll(
                ".greeting, .welcome-title, .welcome-message, .hero-title, .hero-greeting, #greeting, #welcomeGreeting"
            );


        elements.forEach(
            element => {

                const current =
                    element.textContent ||
                    "";


                if (
                    /good\s+(morning|afternoon|evening|night)/i
                        .test(current)
                ) {

                    const updated =
                        current.replace(
                            /good\s+(morning|afternoon|evening|night)/i,
                            greeting
                        );


                    if (
                        updated !==
                        current
                    ) {

                        const walker =
                            document.createTreeWalker(
                                element,
                                NodeFilter.SHOW_TEXT
                            );

                        let node;

                        while (
                            (node = walker.nextNode())
                        ) {

                            if (
                                /good\s+(morning|afternoon|evening|night)/i
                                    .test(node.nodeValue || "")
                            ) {

                                node.nodeValue =
                                    (node.nodeValue || "").replace(
                                        /good\s+(morning|afternoon|evening|night)/i,
                                        greeting
                                    );

                                break;

                            }

                        }

                    }

                }

            }
        );

    }


    const observer =
        new MutationObserver(
            function () {

                updateDynamicGreeting();

            }
        );


    observer.observe(
        document.body,
        {
            childList:
                true,

            subtree:
                true
        }
    );


    updateDynamicGreeting();

})();


/* =========================================================
   ENTITY FINAL LOG
========================================================= */

console.log(
    "=========================================="
);

console.log(
    " ENTITY APP.JS LOADED"
);

console.log(
    " Word-by-word response: ENABLED"
);

console.log(
    " Greeting rotation: ENABLED"
);

console.log(
    " Model selector: ENABLED"
);

console.log(
    " Effort selector: ENABLED"
);

console.log(
    " Voice input: ENABLED"
);

console.log(
    " Code formatting: ENABLED"
);

console.log(
    "=========================================="
);

/* =========================================================
   ENTITY UI FINAL PATCH
   Fix greeting icon + model dropdown appearance
========================================================= */

(function () {

    function updateGreetingSafely() {

        const hour = new Date().getHours();

        let greeting;

        if (hour >= 5 && hour < 12) {
            greeting = "Good morning";
        } else if (hour >= 12 && hour < 17) {
            greeting = "Good afternoon";
        } else if (hour >= 17 && hour < 21) {
            greeting = "Good evening";
        } else {
            greeting = "Good night";
        }


        /*
         * IMPORTANT:
         * innerHTML/textContent ko poore greeting element
         * par apply nahi karna.
         *
         * Sirf text node change karna hai taaki
         * auto_awesome/material icon safe rahe.
         */

        const greetingElements = document.querySelectorAll(
            ".greeting, .welcome-title, .welcome-message, .hero-title, .hero-greeting, #greeting, #welcomeGreeting"
        );


        greetingElements.forEach(function (element) {

            const walker =
                document.createTreeWalker(
                    element,
                    NodeFilter.SHOW_TEXT
                );


            const textNodes = [];


            while (walker.nextNode()) {

                textNodes.push(
                    walker.currentNode
                );

            }


            textNodes.forEach(function (node) {

                const text =
                    node.nodeValue || "";


                if (
                    /Good\s+(morning|afternoon|evening|night)/i
                        .test(text)
                ) {

                    node.nodeValue =
                        text.replace(
                            /Good\s+(morning|afternoon|evening|night)/i,
                            greeting
                        );

                }

            });

        });

    }


    updateGreetingSafely();


    setInterval(
        updateGreetingSafely,
        5000
    );


    /* =====================================================
       REMOVE LEAKED MATERIAL ICON TEXT
    ===================================================== */

    function fixIconText() {

        document
            .querySelectorAll(
                ".material-symbols-rounded"
            )
            .forEach(function (icon) {

                const text =
                    icon.textContent.trim();


                /*
                 * auto_awesome is a legitimate
                 * Material Symbol, so keep it as
                 * an icon and make sure the font
                 * is applied.
                 */

                if (
                    text === "auto_awesome"
                ) {

                    icon.style.fontFamily =
                        "'Material Symbols Rounded'";


                    icon.style.fontWeight =
                        "normal";


                    icon.style.fontStyle =
                        "normal";


                    icon.style.fontSize =
                        "24px";


                    icon.style.lineHeight =
                        "1";


                    icon.style.display =
                        "inline-flex";


                    icon.style.alignItems =
                        "center";


                    icon.style.justifyContent =
                        "center";


                    icon.style.flexShrink =
                        "0";

                }

            });

    }


    fixIconText();


    /* =====================================================
       MODEL DROPDOWN CLEANUP
    ===================================================== */

    const style =
        document.createElement(
            "style"
        );


    style.id =
        "entity-ui-final-patch";


    style.textContent = `

        /* -----------------------------------------
           GREETING
        ----------------------------------------- */

        .greeting,
        .welcome-title,
        .welcome-message,
        .hero-title,
        .hero-greeting,
        #greeting,
        #welcomeGreeting {

            display: flex !important;

            align-items: center !important;

            gap: 10px !important;

        }


        /* -----------------------------------------
           MATERIAL ICON
        ----------------------------------------- */

        .material-symbols-rounded {

            font-family:
                "Material Symbols Rounded" !important;

            font-weight:
                normal !important;

            font-style:
                normal !important;

            font-size:
                24px;

            line-height:
                1;

            letter-spacing:
                normal;

            text-transform:
                none;

            display:
                inline-flex;

            align-items:
                center;

            justify-content:
                center;

            white-space:
                nowrap;

        }


        /* -----------------------------------------
           MODEL MAIN DROPDOWN
        ----------------------------------------- */

        .entity-model-menu {

            min-width:
                300px !important;

            width:
                300px !important;

            max-width:
                300px !important;

            box-sizing:
                border-box !important;

            padding:
                8px !important;

            border-radius:
                16px !important;

            background:
                #242424 !important;

            border:
                1px solid #3b3b3b !important;

            box-shadow:
                0 18px 45px rgba(
                    0,
                    0,
                    0,
                    .45
                ) !important;

            overflow:
                visible !important;

            z-index:
                99999 !important;

        }


        .entity-model-menu.show {

            display:
                block !important;

            visibility:
                visible !important;

            opacity:
                1 !important;

        }


        /* -----------------------------------------
           CURRENT MODEL ROW
        ----------------------------------------- */

        .model-current-row {

            width:
                100% !important;

            min-height:
                62px !important;

            display:
                flex !important;

            align-items:
                center !important;

            justify-content:
                space-between !important;

            padding:
                10px 12px !important;

            border:
                0 !important;

            border-radius:
                10px !important;

            background:
                transparent !important;

            color:
                inherit !important;

            text-align:
                left !important;

        }


        .model-current-row:hover {

            background:
                #303030 !important;

        }


        .model-row-left {

            display:
                flex !important;

            flex-direction:
                column !important;

            gap:
                4px !important;

            min-width:
                0 !important;

        }


        .model-name {

            display:
                block !important;

            font-size:
                15px !important;

            font-weight:
                600 !important;

            line-height:
                1.25 !important;

            color:
                #f5f5f5 !important;

            white-space:
                nowrap !important;

            overflow:
                hidden !important;

            text-overflow:
                ellipsis !important;

        }


        .model-description {

            display:
                block !important;

            font-size:
                13px !important;

            line-height:
                1.2 !important;

            color:
                #9a9a9a !important;

        }


        .model-check {

            color:
                #74a7ff !important;

            flex-shrink:
                0 !important;

        }


        /* -----------------------------------------
           EFFORT ROW
        ----------------------------------------- */

        .model-effort-row,
        .more-models-row {

            width:
                100% !important;

            min-height:
                48px !important;

            display:
                flex !important;

            align-items:
                center !important;

            justify-content:
                space-between !important;

            padding:
                0 12px !important;

            border:
                0 !important;

            border-radius:
                10px !important;

            background:
                transparent !important;

            color:
                #eeeeee !important;

            text-align:
                left !important;

        }


        .model-effort-row:hover,
        .more-models-row:hover {

            background:
                #303030 !important;

        }


        .effort-title {

            font-weight:
                600 !important;

        }


        .effort-value {

            display:
                flex !important;

            align-items:
                center !important;

            gap:
                6px !important;

            color:
                #aaaaaa !important;

        }


        /* -----------------------------------------
           MORE MODELS MENU
        ----------------------------------------- */

        .entity-more-models-menu {

            width:
                280px !important;

            min-width:
                280px !important;

            max-height:
                420px !important;

            overflow-y:
                auto !important;

            box-sizing:
                border-box !important;

            padding:
                8px !important;

            border-radius:
                14px !important;

            background:
                #242424 !important;

            border:
                1px solid #3b3b3b !important;

            box-shadow:
                0 18px 45px rgba(
                    0,
                    0,
                    0,
                    .45
                ) !important;

            z-index:
                100000 !important;

        }


        .entity-more-models-menu.show {

            display:
                block !important;

            visibility:
                visible !important;

            opacity:
                1 !important;

        }


        .ollama-model-item {

            width:
                100% !important;

            min-height:
                42px !important;

            padding:
                0 12px !important;

            display:
                flex !important;

            align-items:
                center !important;

            border:
                0 !important;

            border-radius:
                8px !important;

            background:
                transparent !important;

            color:
                #eeeeee !important;

            text-align:
                left !important;

            cursor:
                pointer !important;

        }


        .ollama-model-item:hover {

            background:
                #333333 !important;

        }


        /* -----------------------------------------
           EFFORT SUBMENU
        ----------------------------------------- */

        .entity-effort-menu {

            width:
                180px !important;

            padding:
                6px !important;

            border-radius:
                12px !important;

            background:
                #242424 !important;

            border:
                1px solid #3b3b3b !important;

            box-shadow:
                0 18px 45px rgba(
                    0,
                    0,
                    0,
                    .45
                ) !important;

            z-index:
                100001 !important;

        }


        .effort-option {

            width:
                100% !important;

            min-height:
                44px !important;

            display:
                flex !important;

            align-items:
                center !important;

            justify-content:
                space-between !important;

            padding:
                0 12px !important;

            border:
                0 !important;

            border-radius:
                8px !important;

            background:
                transparent !important;

            color:
                #eeeeee !important;

            text-align:
                left !important;

            cursor:
                pointer !important;

        }


        .effort-option:hover,
        .effort-option.selected {

            background:
                #333333 !important;

        }

    `;


    /*
     * Existing duplicate style ko replace karo
     */

    const oldStyle =
        document.getElementById(
            "entity-ui-final-patch"
        );


    if (oldStyle) {

        oldStyle.remove();

    }


    document.head.appendChild(
        style
    );


    /*
     * Icons dynamically create hone par
     * bhi check karte raho.
     */

    const observer =
        new MutationObserver(
            function () {

                fixIconText();

            }
        );


    observer.observe(
        document.body,
        {
            childList:
                true,

            subtree:
                true
        }
    );


})();

/* =========================================================
   ENTITY CHAT PLACEHOLDER ANIMATION
   Word by word + Pause + Fade effect + Next line
========================================================= */

(function () {

    "use strict";

    const placeholderMessages = [

        "How can I help you today?",
        "What are we building today?",
        "Ask me anything.",
        "What's on your mind?",
        "Let's create something amazing.",
        "What would you like to explore?",
        "Describe your next idea.",
        "What should we work on?",
        "Let's solve something interesting.",
        "Start typing your idea.",
        "What can Entity help you with?",
        "Ready when you are.",
        "Let's make something happen.",
        "Tell me what you're thinking.",
        "What would you like to create?",
        "Your next idea starts here.",
        "Let's figure something out.",
        "Ask a question.",
        "What should we discover today?",
        "Bring me your next idea."

    ];


    const WORD_SPEED = 90;
    const DISPLAY_TIME = 4000;
    const DELETE_SPEED = 35;


    let lastMessage = "";
    let animationStarted = false;


    function getInput() {

        return document.querySelector(
            "#messageInput"
        ) || document.querySelector(
            "#homeInput"
        );

    }


    function wait(time) {

        return new Promise(function (resolve) {

            setTimeout(
                resolve,
                time
            );

        });

    }


    function getRandomMessage() {

        let message = lastMessage;

        while (
            placeholderMessages.length > 1 &&
            message === lastMessage
        ) {

            message =
                placeholderMessages[
                    Math.floor(
                        Math.random() *
                        placeholderMessages.length
                    )
                ];

        }

        lastMessage = message;

        return message;

    }


    async function typePlaceholder(
        input,
        text
    ) {

        const words =
            text.split(/\s+/);

        input.placeholder = "";

        for (
            let i = 0;
            i < words.length;
            i++
        ) {

            if (input.value.trim() !== "") {

                return false;

            }

            if (i > 0) {

                input.placeholder += " ";

            }

            input.placeholder += words[i];

            await wait(
                WORD_SPEED
            );

        }

        return true;

    }


    async function clearPlaceholder(
        input
    ) {

        const text =
            input.placeholder;

        for (
            let i = text.length;
            i >= 0;
            i--
        ) {

            if (input.value.trim() !== "") {

                return false;

            }

            input.placeholder =
                text.slice(
                    0,
                    i
                );

            await wait(
                DELETE_SPEED
            );

        }

        return true;

    }


    async function runPlaceholderAnimation() {

        while (true) {

            const input =
                getInput();

            if (!input) {

                await wait(1000);

                continue;

            }


            if (
                input.value.trim() !== ""
            ) {

                await wait(500);

                continue;

            }


            const message =
                getRandomMessage();


            const typed =
                await typePlaceholder(
                    input,
                    message
                );


            if (!typed) {

                continue;

            }


            await wait(
                DISPLAY_TIME
            );


            if (
                input.value.trim() !== ""
            ) {

                continue;

            }


            await clearPlaceholder(
                input
            );


            await wait(300);

        }

    }


    function startPlaceholderAnimation() {

        if (animationStarted) {

            return;

        }

        animationStarted = true;

        runPlaceholderAnimation();

    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            startPlaceholderAnimation
        );

    } else {

        startPlaceholderAnimation();

    }

})();

/* =========================================================
   ENTITY ACCOUNT MENU
   Open / Close Account Dropdown
========================================================= */

(function () {

    "use strict";

    const accountButton =
        document.getElementById(
            "accountButton"
        );

    const accountMenu =
        document.getElementById(
            "accountMenu"
        );


    if (
        !accountButton ||
        !accountMenu
    ) {

        console.warn(
            "Entity: account menu elements not found."
        );

        return;

    }


    function openAccountMenu() {

        accountMenu.classList.add(
            "show"
        );

        accountButton.setAttribute(
            "aria-expanded",
            "true"
        );

        accountMenu.setAttribute(
            "aria-hidden",
            "false"
        );

    }


    function closeAccountMenu() {

        accountMenu.classList.remove(
            "show"
        );

        accountButton.setAttribute(
            "aria-expanded",
            "false"
        );

        accountMenu.setAttribute(
            "aria-hidden",
            "true"
        );

    }


    function toggleAccountMenu() {

        if (
            accountMenu.classList.contains(
                "show"
            )
        ) {

            closeAccountMenu();

        } else {

            openAccountMenu();

        }

    }


    /* CLICK ACCOUNT BUTTON */

    accountButton.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

            toggleAccountMenu();

        }
    );


    /* CLICK INSIDE MENU */

    accountMenu.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

        }
    );


    /* CLICK OUTSIDE */

    document.addEventListener(
        "click",
        function (event) {

            if (
                !accountButton.contains(
                    event.target
                ) &&
                !accountMenu.contains(
                    event.target
                )
            ) {

                closeAccountMenu();

            }

        }
    );


    /* ESCAPE KEY */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape"
            ) {

                closeAccountMenu();

            }

        }
    );


    console.log(
        "Entity account menu ready."
    );

})();


