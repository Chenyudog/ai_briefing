const editor = document.querySelector("#entry-body");
const tools = document.querySelector(".image-tools");
const insertButton = document.querySelector("#insert-image");
const fileInput = document.querySelector("#entry-image");
const statusText = document.querySelector("#image-status");
const preview = document.querySelector("#entry-preview");
const previewPanel = preview.parentElement;
const form = editor.form;

function renderPreview() {
    if (!previewPanel.open) return;
    const parts = editor.value.split(/\[图片:([a-f0-9]{32})\]/);
    preview.replaceChildren();
    parts.forEach((part, index) => {
        if (index % 2) {
            const image = document.createElement("img");
            image.src = tools.dataset.imageUrl.replace("IMAGE_ID", part);
            image.alt = "正文配图";
            preview.append(image);
        } else if (part.trim()) {
            const paragraph = document.createElement("p");
            paragraph.textContent = part.trim();
            preview.append(paragraph);
        }
    });
    if (!preview.childNodes.length) preview.textContent = "暂无正文。";
}

tools.hidden = false;
previewPanel.hidden = false;
insertButton.addEventListener("click", () => fileInput.click());
previewPanel.addEventListener("toggle", renderPreview);
let previewTimer;
editor.addEventListener("input", () => {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(renderPreview, 250);
});
fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    fileInput.value = "";
    if (file.size > 10 * 1024 * 1024) {
        statusText.textContent = "每张图片最大 10 MB。";
        return;
    }
    const position = editor.selectionStart;
    const data = new FormData();
    data.set("csrf", form.elements.csrf.value);
    data.set("image", file);
    const submitButtons = form.querySelectorAll("button[name=action]");
    editor.readOnly = true;
    insertButton.disabled = true;
    submitButtons.forEach(button => button.disabled = true);
    statusText.textContent = "正在上传图片…";
    try {
        const response = await fetch(tools.dataset.uploadUrl, { method: "POST", body: data });
        if (!response.headers.get("content-type")?.includes("application/json")) {
            throw new Error("上传未完成。请确认仍在登录状态后重试。");
        }
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "上传失败，请重试。");
        editor.setRangeText(`\n\n[图片:${result.id}]\n\n`, position, position, "end");
        statusText.textContent = "图片已插入。";
        previewPanel.open = true;
        renderPreview();
    } catch (error) {
        statusText.textContent = error.message || "上传失败，请重试。";
    } finally {
        editor.readOnly = false;
        insertButton.disabled = false;
        submitButtons.forEach(button => button.disabled = false);
        editor.focus();
    }
});
