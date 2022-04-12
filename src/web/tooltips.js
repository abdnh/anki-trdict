function showTooltipForSelection() {
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();
    if (!selectedText) return;
    const tooltip = tippy(selection.anchorNode.parentElement, {
        placement: "bottom",
        allowHTML: true,
        theme: document.body.classList.contains("night_mode") ? "material" : "light",
        interactive: true,
        trigger: '',
        animation: "scale-extreme",
        appendTo: document.body,
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
