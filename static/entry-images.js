const editor = document.querySelector("#entry-body");
const tools = document.querySelector(".image-tools");
const insertButton = document.querySelector("#insert-image");
const fileInput = document.querySelector("#entry-image");
const statusText = document.querySelector("#image-status");
const preview = document.querySelector("#entry-preview");
const previewPanel = preview.parentElement;
const form = editor.form;

let previewRequest;

async function renderPreview() {
    if (!previewPanel.open) return;
    previewRequest?.abort();
    const controller = new AbortController();
    previewRequest = controller;
    try {
        const response = await fetch(tools.dataset.previewUrl, {
            method: "POST",
            body: new URLSearchParams({ csrf: form.elements.csrf.value, body: editor.value }),
            signal: controller.signal,
        });
        if (!response.ok) throw new Error();
        const result = await response.json();
        if (controller.signal.aborted) return;
        if (result.html) {
            // Only the server's Markdown renderer can supply this HTML.
            preview.innerHTML = result.html;
        } else {
            preview.textContent = "暂无正文。";
        }
    } catch (error) {
        if (error.name !== "AbortError") preview.textContent = "预览加载失败，请重新展开预览。";
    }
}

const headingButtons = tools.querySelectorAll("[data-heading]");
headingButtons.forEach(button => {
    button.addEventListener("click", () => {
        const cursor = editor.selectionStart;
        const start = cursor === 0 ? 0 : editor.value.lastIndexOf("\n", cursor - 1) + 1;
        const nextBreak = editor.value.indexOf("\n", cursor);
        const end = nextBreak === -1 ? editor.value.length : nextBreak;
        const line = editor.value.slice(start, end).replace(/^#{1,6} +/, "");
        editor.setRangeText(`${button.dataset.heading} ${line}`, start, end, "end");
        editor.focus();
        previewPanel.open = true;
        renderPreview();
    });
});

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
    const submitButtons = form.querySelectorAll("button[name=action], [data-heading]");
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
        editor.setRangeText(`\n\n![正文配图](${result.url})\n\n`, position, position, "end");
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
