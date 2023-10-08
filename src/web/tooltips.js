function showTooltipForSelection() {
    const selection = window.getSelection();
    const range = selection.getRangeAt(0);
    const selectedText = range.toString().trim();
    if (!selectedText) return;
    const fragment = range.extractContents();

    const span = document.createElement("span");
    span.appendChild(fragment);
    range.insertNode(span);

    const tooltip = tippy(span, {
        placement: "bottom",
        allowHTML: true,
        theme: document.body.classList.contains("night_mode")
            ? "material"
            : "light",
        interactive: true,
        trigger: "",
        animation: "scale-extreme",
        appendTo: document.body,
        onHide() {
            try {
                span.insertAdjacentHTML("afterend", span.innerHTML);
                span.remove();
            } catch (err) {}
        },
    });
    tooltip.show();
    globalThis.tippyInstance = tooltip;
    pycmd(`trdict:popup:${selectedText}`);
}

function enableTooltips() {
    document.addEventListener("dblclick", showTooltipForSelection);
}

function disableTooltips() {
    document.removeEventListener("dblclick", showTooltipForSelection);
}
