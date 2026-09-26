// Collapses and expands the rows of an SVG Gantt chart written by pyTooling.Tracing.Render.Matplotlib.
// '/*DATA*/null' is replaced by the rows ({id, parent, collapsed}) and the distance between two rows (pitch).
(function () {
  "use strict";
  const data = /*DATA*/null;
  const rows = data.rows;
  const byID = new Map();
  for (const row of rows) { row.children = []; byID.set(row.id, row); }
  for (const row of rows) {
    if (row.parent !== null && byID.has(row.parent)) { byID.get(row.parent).children.push(row); }
  }
  const collapsed = new Set(rows.filter(row => row.collapsed && row.children.length > 0).map(row => row.id));
  const markers = new Map();

  function elementsOf(row) {
    return ["span-" + row.id, "span-" + row.id + "-queued", "span-" + row.id + "-ends", "label-" + row.id]
      .map(id => document.getElementById(id))
      .filter(element => element !== null);
  }

  function isHidden(row) {
    for (let parent = byID.get(row.parent); parent !== undefined; parent = byID.get(parent.parent)) {
      if (collapsed.has(parent.id)) { return true; }
    }
    return false;
  }

  function update() {
    let shift = 0;
    for (const row of rows) {
      const hidden = isHidden(row);
      const marker = markers.get(row.id);
      const shown = marker === undefined ? elementsOf(row) : elementsOf(row).concat([marker]);
      for (const element of shown) {
        element.style.display = hidden ? "none" : "";
        element.setAttribute("transform", "translate(0," + (-shift) + ")");
      }
      if (marker !== undefined) { marker.textContent = collapsed.has(row.id) ? "\u25B8" : "\u25BE"; }
      if (hidden) { shift += data.pitch; }
    }
  }

  function toggle(row) {
    if (collapsed.has(row.id)) { collapsed.delete(row.id); } else { collapsed.add(row.id); }
    update();
  }

  for (const row of rows) {
    if (row.children.length === 0) { continue; }
    for (const element of elementsOf(row)) {
      element.style.cursor = "pointer";
      element.addEventListener("click", () => toggle(row));
    }
    const label = document.getElementById("label-" + row.id);
    if (label !== null && typeof label.getBBox === "function") {
      const box = label.getBBox();
      const marker = document.createElementNS("http://www.w3.org/2000/svg", "text");
      marker.setAttribute("class", "gantt-marker");
      marker.setAttribute("x", box.x - 2);
      marker.setAttribute("y", box.y + box.height * 0.85);
      marker.setAttribute("text-anchor", "end");
      marker.setAttribute("font-size", box.height);
      marker.addEventListener("click", () => toggle(row));
      label.parentNode.insertBefore(marker, label.nextSibling);
      markers.set(row.id, marker);
    }
  }
  update();
})();
