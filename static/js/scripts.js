function showTool(tool, el) {
    
    // 🔥 ocultar categorías
    document.querySelectorAll(".category").forEach(c => {
        c.style.display = "none";
    });

    // 🔥 mostrar contenedor
    const containers = document.querySelectorAll(".container");
    containers.forEach(c => c.classList.remove("active"));

    const selected = document.getElementById(tool);
    selected.classList.add("active");

    // 🔥 botón volver
    let backBtn = document.getElementById("backBtn");

    if (!backBtn) {
        backBtn = document.createElement("button");
        backBtn.id = "backBtn";
        backBtn.textContent = "← Volver";
        backBtn.className = "btn";

        backBtn.onclick = () => {
            document.querySelectorAll(".category").forEach(c => {
                c.style.display = "block";
            });

            document.querySelectorAll(".container").forEach(c => {
                c.classList.remove("active");
            });

            backBtn.remove();
        };

        document.body.prepend(backBtn);
    }

    setTimeout(() => {
        selected.scrollIntoView({
            behavior: "smooth"
        });
    }, 100);
}

const dropArea = document.getElementById("drop-area");
const input = document.getElementById("mergeInput");
const fileListContainer = document.getElementById("file-list");

let filesArray = [];

if (dropArea) {

    input.addEventListener("change", (e) => {
        filesArray = Array.from(e.target.files);
        renderFiles();
    });

    dropArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropArea.classList.add("dragover");
    });

    dropArea.addEventListener("dragleave", () => {
        dropArea.classList.remove("dragover");
    });

    dropArea.addEventListener("drop", (e) => {
        e.preventDefault();
        dropArea.classList.remove("dragover");

        const newFiles = Array.from(e.dataTransfer.files);
        filesArray = filesArray.concat(newFiles);
        updateInputFiles();
        renderFiles();
    });
}

function renderFiles() {

    const uploadContent = document.getElementById("upload-content");

    if (filesArray.length > 0) {
        uploadContent.style.display = "none";
    } else {
        uploadContent.style.display = "block";
    }

    fileListContainer.innerHTML = "";

    filesArray.forEach((file, index) => {
        const div = document.createElement("div");
        div.classList.add("file-item");

        div.innerHTML = `
            ${file.name}
            <span class="remove-file" data-index="${index}">❌</span>
        `;

        fileListContainer.appendChild(div);
    });

    addRemoveEvents();
}

function addRemoveEvents() {
    document.querySelectorAll(".remove-file").forEach(btn => {
        btn.addEventListener("click", function () {
            const index = this.getAttribute("data-index");
            filesArray.splice(index, 1);
            updateInputFiles();
            renderFiles();
        });
    });
}

function updateInputFiles() {
    const dataTransfer = new DataTransfer();

    filesArray.forEach(file => dataTransfer.items.add(file));

    input.files = dataTransfer.files;
}

/*==========================
    SPLIT 
==========================*/

const splitInput = document.getElementById("splitInput");
const fileInput = document.querySelector('input[type="file"]');
const fileNameDiv = document.querySelector('.file-name');
const pagesContainer = document.getElementById("pages-container");
const pagesInput = document.getElementById("pagesInput");
const zoomPreview = document.getElementById("zoomPreview"); // 👈 IMPORTANTE

let selectedPages = new Set();

if (splitInput && fileNameDiv) {
    splitInput.addEventListener("change", async function () {

        const file = this.files[0];
        if (!file) return;

        fileNameDiv.textContent = file.name;

        const loader = document.getElementById("previewLoader");

        // 🔥 MOSTRAR LOADER
        loader.classList.remove("hidden");
        loader.querySelector("p").textContent = "Analizando documento...";

        pagesContainer.innerHTML = "";
        pagesContainer.appendChild(loader);

        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/preview_pages", {
            method: "POST",
            body: formData
        });

        // 🔄 CAMBIO DE TEXTO
        setTimeout(() => {
            loader.querySelector("p").textContent = "Procesando páginas...";
        }, 800);

        const data = await res.json();

        // 🔥 OCULTAR LOADER
        loader.classList.add("hidden");
        pagesContainer.innerHTML = "";

        selectedPages.clear();

        // 🚨 MODO SIMPLE (PDF GRANDE)
        if (data.mode === "simple") {

            pagesContainer.innerHTML = `
                <div style="text-align:center; margin-top:30px;">
                    <p>📄 PDF grande detectado (${data.total_pages} páginas)</p>
                    <p>Ingresa las páginas que deseas separar:</p>

                    <input id="manualPages" 
                            placeholder="Ej: 1-5, 8, 10-12"
                            style="padding:10px; width:250px; border-radius:8px; border:1px solid #ccc;">
                </div>
            `;

            const input = document.getElementById("manualPages");

            input.addEventListener("input", function () {
                pagesInput.value = this.value;
            });

            return; // 🔥 IMPORTANTE: detiene ejecución
        }

        // 🟢 MODO NORMAL (PDF PEQUEÑO)
        data.images.forEach((src, index) => {

            const img = document.createElement("img");
            img.src = src;
            img.classList.add("page");

            // ✅ SELECCIÓN
            img.onclick = () => {
                if (selectedPages.has(index)) {
                    selectedPages.delete(index);
                    img.classList.remove("selected");
                } else {
                    selectedPages.add(index);
                    img.classList.add("selected");
                }

                const pagesArray = Array.from(selectedPages).map(i => i + 1);
                pagesInput.value = pagesArray.join(",");
            };

            // 🔥 ZOOM PREVIEW (PRO)
            if (zoomPreview) {

                let zoomTimeout;

                img.addEventListener("mouseenter", () => {
                    zoomTimeout = setTimeout(() => {
                        zoomPreview.innerHTML = `<img src="${src}">`;
                        zoomPreview.classList.remove("hidden");
                    }, 150);
                });

                img.addEventListener("mouseleave", () => {
                    clearTimeout(zoomTimeout);
                    zoomPreview.classList.add("hidden");
                });

            }

            pagesContainer.appendChild(img);
        });

    });
}

/* =========================
    FILE NAME DISPLAY (GLOBAL)
========================= */

const allInputs = document.querySelectorAll(".file-input");

allInputs.forEach(input => {

    input.addEventListener("change", function () {

        const container = this.closest("form");
        const fileNameDivs = container.querySelectorAll(".file-name");

        if (!fileNameDivs.length) return;

        // 🔥 Detectar cuál label corresponde
        let targetDiv;

        if (this.name === "pdf") {
            targetDiv = fileNameDivs[0];
        } else {
            targetDiv = fileNameDivs[fileNameDivs.length - 1];
        }

        if (this.files.length === 1) {
            targetDiv.innerHTML = `
                <span>${this.files[0].name}</span>
                <span class="file-size">
                    ${(this.files[0].size / (1024 * 1024)).toFixed(2)} MB
                </span>
            `;
        } else if (this.files.length > 1) {
            targetDiv.innerHTML = `
                <span>${this.files.length} archivos seleccionados</span>
                <span class="file-size">✔</span>
            `;
        }
    });

});



// 🔥 MENSAJES INTELIGENTES
const toolMessages = {
    "/merge": "Uniendo PDFs...",
    "/split": "Dividiendo páginas...",
    "/compress_pdf": "Comprimiendo archivo...",
    "/pdf_to_img": "Convirtiendo PDF a imágenes...",
    "/img_to_pdf": "Creando PDF desde imágenes...",
    "/pdf_to_word": "Convirtiendo a Word...",
    "/word_to_pdf": "Convirtiendo a PDF...",
    "/excel_to_pdf": "Convirtiendo Excel...",
    "/pdf_to_excel": "Extrayendo datos a Excel...",
    "/ppt_to_pdf": "Convirtiendo presentación...",
    "/ocr_pdf": "Reconociendo texto (OCR)...",
    "/rotate_pdf": "Rotando páginas...",
    "/reorder_pdf": "Organizando páginas...",
    "/add_images_pdf": "Insertando imágenes...",
    "/unlock_pdf": "Desbloqueando PDF...",
    "/protect_pdf": "Protegiendo archivo...",
    "/sign_pdf": "Aplicando firma...",
    "/watermark_pdf": "Agregando marca de agua...",
    "/number_pdf": "Numerando páginas..."
};

const forms = document.querySelectorAll("form");

forms.forEach(form => {

    if (form.action.includes("unlock_pdf")) return; // 🔥 ESTA ES LA CLAVE

    form.addEventListener("submit", function(e) {


        e.preventDefault();

        const modal = document.getElementById("processingModal");
        const progress = document.getElementById("progressFill");
        const loadingText = document.getElementById("loadingText");


        modal.classList.remove("hidden");


        const action = form.getAttribute("action");


        loadingText.textContent = toolMessages[action] || "Procesando archivo...";



        const formData = new FormData(form);

        // 🔥 SOLO PARA ROTATE (AQUÍ ES DONDE VA)
        if (form.id === "rotateForm") {
            formData.append("rotations", JSON.stringify(rotateData));
        }

        fetch(form.action, {
            method: "POST",
            body: formData
        })
        .then(res => res.text())
        .then(html => {

            // 🔥 SI ES MODAL DE CONTRASEÑA
            if (html.includes('ask_password')) {

            document.open();
            document.write(html);
            document.close();

            // 🔥 ESPERAR A QUE EL DOM EXISTA
            setTimeout(() => {
                const modal = document.getElementById("passwordModal");
                if (modal) {
                    modal.classList.add("active");
                }
            }, 50);

            return;
            }
            // 🔥 RESULTADO NORMAL
            document.open();
            document.write(html);
            document.close();

        })
        .catch(err => {
            console.error("Error:", err);
            alert("Hubo un error");
        });

    });

});


const modal = document.getElementById("processingModal");
const progress = document.getElementById("progressFill");
const loadingText = document.getElementById("loadingText");

const messages = [
    "Subiendo archivo...",
    "Procesando...",
    "Optimizando...",
    "Casi listo..."
];

function simulateProgress() {
    let percent = 0;
    let step = 0;

    const interval = setInterval(() => {

        percent += Math.random() * 15;

        if (percent >= 95) {
            percent = 95; // se detiene antes del final
            clearInterval(interval);
        }

        progress.style.width = percent + "%";

        if (step < messages.length) {
            loadingText.textContent = messages[step];
            step++;
        }

    }, 400);
}


/* =========================
    ROTATE (PÁGINAS INDIVIDUALES)
========================= */

const rotateInput = document.getElementById("rotateInput");
const rotateContainer = document.getElementById("rotate-pages-container");
const rotateForm = document.getElementById("rotateForm");

let rotateData = {};

if (rotateInput) {

    rotateInput.addEventListener("change", async function () {

        const file = this.files[0];
        if (!file) return;


        rotateContainer.innerHTML = `
            <div class="preview-loader">
                <div class="spinner"></div>
                <p>Analizando documento...</p>
            </div>
        `;

        // 🔥 SOLO ARCHIVO (NO ROTATIONS AQUÍ)
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/preview_pages", {
            method: "POST",
            body: formData
        });


        setTimeout(() => {
            const loaderText = rotateContainer.querySelector("p");
            if (loaderText) {
                loaderText.textContent = "Procesando páginas...";
            }
        }, 800);

        if (!res.ok) {
        const errorData = await res.json();
        alert(errorData.error || "Error al procesar el archivo");
        rotateContainer.innerHTML = "";
        return;
        }

        const data = await res.json();

        rotateContainer.innerHTML = "";
        rotateData = {};

        data.images.forEach((src, index) => {

            const wrapper = document.createElement("div");
            wrapper.style.textAlign = "center";

            const img = document.createElement("img");
            img.src = src;
            img.classList.add("page");

            const btn = document.createElement("button");
            btn.textContent = "⟲";
            btn.classList.add("btn");
            btn.type = "button";

            rotateData[index] = 0;

            btn.onclick = () => {
                
                rotateData[index] = (rotateData[index] + 90) % 360;

                img.style.transform = `rotate(${rotateData[index]}deg)`;
            };

            wrapper.appendChild(img);
            wrapper.appendChild(btn);

            rotateContainer.appendChild(wrapper);
        });

    });

}



/* =========================
    DELETE PAGES
========================= */

const deleteInput = document.getElementById("deleteInput");
const deleteContainer = document.getElementById("delete-pages-container");
const deletePagesInput = document.getElementById("deletePagesInput");
const deleteForm = document.getElementById("deleteForm");

let deleteSelected = new Set();

if (deleteInput) {

    deleteInput.addEventListener("change", async function () {

        const file = this.files[0];
        if (!file) return;

        // 🔥 LOADER
        deleteContainer.innerHTML = `
            <div class="preview-loader">
                <div class="spinner"></div>
                <p>Analizando documento...</p>
            </div>
        `;

        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/preview_pages", {
            method: "POST",
            body: formData
        });

        setTimeout(() => {
            const txt = deleteContainer.querySelector("p");
            if (txt) txt.textContent = "Procesando páginas...";
        }, 800);

        const data = await res.json();

        deleteContainer.innerHTML = "";
        deleteSelected.clear();

        data.images.forEach((src, index) => {

            const img = document.createElement("img");
            img.src = src;
            img.classList.add("page");

            img.onclick = () => {

                if (deleteSelected.has(index)) {
                    deleteSelected.delete(index);
                    img.classList.remove("selected");
                } else {
                    deleteSelected.add(index);
                    img.classList.add("selected");
                }

                const pagesArray = Array.from(deleteSelected).map(i => i + 1);
                deletePagesInput.value = pagesArray.join(",");
            };

            deleteContainer.appendChild(img);
        });

    });
}

if (deleteForm) {
    deleteForm.addEventListener("submit", function(e) {

        if (deleteSelected.size === 0) {
            e.preventDefault();
            alert("Selecciona al menos una página");
        }
    });
}

/* =========================
    REORDER PDF
========================= */

const reorderInput = document.getElementById("reorderInput");
const reorderContainer = document.getElementById("reorder-container");
const orderInput = document.getElementById("orderInput");

let dragged = null;

if (reorderInput) {

    reorderInput.addEventListener("change", async function () {

        const file = this.files[0];
        if (!file) return;

        reorderContainer.innerHTML = "<p>Cargando páginas...</p>";

        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/preview_reorder", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        reorderContainer.innerHTML = "";

        data.images.forEach(item => {

            const div = document.createElement("div");
            div.classList.add("draggable");
            div.draggable = true;
            div.dataset.page = item.page;

            div.innerHTML = `
                <img src="${item.src}" class="page">
                <p>Página ${item.page}</p>
            `;

            // 🔥 drag start
            div.addEventListener("dragstart", () => {
                dragged = div;
            });

            // 🔥 drag over
            div.addEventListener("dragover", (e) => {
                e.preventDefault();
            });

            // 🔥 drop
            div.addEventListener("drop", () => {
                if (dragged !== div) {
                    reorderContainer.insertBefore(dragged, div);
                    updateOrder();
                }
            });

            reorderContainer.appendChild(div);
        });

        updateOrder();
    });
}

function updateOrder() {
    const items = document.querySelectorAll(".draggable");
    const order = [];

    items.forEach(item => {
        order.push(item.dataset.page);
    });

    orderInput.value = order.join(",");
}

/* =========================
    ADD IMAGES (FILE NAMES)
========================= */

const addPdfInput = document.getElementById("addPdfInput");
const addImagesInput = document.getElementById("addImagesInput");

const pdfNameDiv = document.getElementById("pdf-name");
const imagesNameDiv = document.getElementById("images-name");

// 📄 PDF
if (addPdfInput) {
    addPdfInput.addEventListener("change", function () {

        const file = this.files[0];
        if (!file) return;

        pdfNameDiv.innerHTML = `
            <span>${file.name}</span>
            <span class="file-size">
                ${(file.size / (1024 * 1024)).toFixed(2)} MB
            </span>
        `;
    });
}

// 🖼 IMÁGENES
if (addImagesInput) {
    addImagesInput.addEventListener("change", function () {

        const files = this.files;
        if (!files.length) return;

        if (files.length === 1) {
            imagesNameDiv.innerHTML = `
                <span>${files[0].name}</span>
                <span class="file-size">
                    ${(files[0].size / (1024 * 1024)).toFixed(2)} MB
                </span>
            `;
        } else {
            imagesNameDiv.innerHTML = `
                <span>${files.length} imágenes seleccionadas</span>
                <span class="file-size">✔</span>
            `;
        }
    });
}

/* =========================
    UNLOCK PDF
========================= */

document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener("change", function () {
        const fileName = this.files[0]?.name || "No file selected";
        const display = this.closest("form").querySelector("#file-name");
        if (display) display.textContent = fileName;
    });
});


const fileInputUnlock = document.getElementById("fileInputUnlock");
const fileNameUnlock = document.getElementById("file-name-unlock");

const dropAreaUnlock = document.getElementById("dropAreaUnlock");
if (dropAreaUnlock) {

    dropAreaUnlock.addEventListener("click", () => fileInputUnlock.click());

    dropAreaUnlock.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropAreaUnlock.classList.add("dragover");
    });

    dropAreaUnlock.addEventListener("dragleave", () => {
        dropAreaUnlock.classList.remove("dragover");
    });

    dropAreaUnlock.addEventListener("drop", (e) => {
        e.preventDefault();
        dropAreaUnlock.classList.remove("dragover");

        const files = e.dataTransfer.files;
        fileInputUnlock.files = files;

        fileNameUnlock.textContent = files[0].name;
    });

    fileInputUnlock.addEventListener("change", () => {
        if (fileInputUnlock.files.length > 0) {
            fileNameUnlock.textContent = fileInputUnlock.files[0].name;
        }
    });
}

function submitPassword() {
    const password = document.getElementById("passwordInput").value;
    const tempName = document.getElementById("tempName").value;

    const formData = new FormData();
    formData.append("password", password);
    formData.append("temp_name", tempName);

    fetch("/unlock_pdf", {
        method: "POST",
        body: formData
    })
    .then(res => res.text())
    .then(html => {
        document.open();
        document.write(html);
        document.close();
    })
    .catch(err => {
        alert("Error al desbloquear PDF");
        console.error(err);
    });
}

function openFeedback() {
    document.getElementById("feedbackModal").style.display = "block";
}

function closeFeedback() {
    document.getElementById("feedbackModal").style.display = "none";
}

function closePasswordModal() {
    const modal = document.getElementById("passwordModal");

    modal.classList.remove("active");
    modal.classList.add("hidden");

    // 🔥 limpia estado del navegador
    window.history.replaceState({}, document.title, "/");
}

window.addEventListener("click", function(e) {
    const modal = document.getElementById("passwordModal");

    if (e.target === modal) {
        modal.classList.remove("active");
    }
});

function saveSignature() {

    const sig = document.getElementById("signature");

    const x = parseInt(sig.style.left);
    const y = parseInt(sig.style.top);
    const width = sig.offsetWidth;

    const pdfName = document.getElementById("pdfName").value;
    const sigName = document.getElementById("sigName").value;

    const formData = new FormData();

    formData.append("x", x);
    formData.append("y", y);
    formData.append("width", width);
    formData.append("pdf_name", pdfName);
    formData.append("sig_name", sigName);

    fetch("/apply_signature_manual", {
        method: "POST",
        body: formData
    })
    .then(res => res.text())
    .then(html => {
        document.open();
        document.write(html);
        document.close();
    });
}

function openDonateModal() {
    document.getElementById("donateModal").classList.add("active");
}

function closeDonateModal() {
    document.getElementById("donateModal").classList.remove("active");
}

function copyNequi() {
    navigator.clipboard.writeText("3188198651");
    document.getElementById("copyMsg").innerText = "Copied ✔";
}