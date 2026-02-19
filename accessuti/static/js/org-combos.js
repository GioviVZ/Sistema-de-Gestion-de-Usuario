// static/js/org-combos.js
(() => {
  const cfg = window.ACCESSUTI || {};
  const ORG_URL = cfg.orgUrl;

  let ORG = null;

  const $sede = () => document.getElementById("sede");
  const $dep = () => document.getElementById("dependencia");
  const $sub = () => document.getElementById("subdependencia");

  function opt(text, value) {
    const o = document.createElement("option");
    o.value = value ?? text;
    o.textContent = text;
    return o;
  }

  function clearSelect(sel, placeholderText) {
    if (!sel) return;
    sel.innerHTML = "";
    sel.appendChild(opt(placeholderText || "Seleccione", ""));
  }

  function setOptions(sel, items, placeholderText) {
    clearSelect(sel, placeholderText);
    items.forEach((it) => sel.appendChild(opt(it, it)));
  }

  async function loadOrg() {
    if (!ORG_URL) throw new Error("ORG_URL no definido (window.ACCESSUTI.orgUrl)");
    const res = await fetch(ORG_URL, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error("No se pudo cargar org.json");
    ORG = await res.json();
    return ORG;
  }

  function getSedes() {
    return ORG ? Object.keys(ORG) : [];
  }

  function getDeps(sede) {
    if (!ORG || !sede || !ORG[sede]) return [];
    return Object.keys(ORG[sede]);
  }

  function getSubs(sede, dep) {
    if (!ORG || !sede || !dep) return [];
    const obj = ORG[sede];
    if (!obj || !obj[dep]) return [];
    return Array.isArray(obj[dep]) ? obj[dep] : [];
  }

  function refreshDeps(keepDep = "", keepSub = "") {
    const sede = $sede()?.value || "";
    const deps = getDeps(sede);

    setOptions($dep(), deps, deps.length ? "Seleccione dependencia" : "Sin dependencias");
    clearSelect($sub(), "Seleccione dependencia primero");

    if (keepDep && deps.includes(keepDep)) {
      $dep().value = keepDep;
      refreshSubs(keepSub);
    }
  }

  function refreshSubs(keepSub = "") {
    const sede = $sede()?.value || "";
    const dep = $dep()?.value || "";
    const subs = getSubs(sede, dep);

    setOptions($sub(), subs, subs.length ? "Seleccione subdependencia" : "Sin subdependencias");

    if (keepSub && subs.includes(keepSub)) {
      $sub().value = keepSub;
    }
  }

  // API pública para que modal.js pueda setear valores al editar/ver
  window.OrgCombos = {
    async init() {
      await loadOrg();

      // sedes
      const sedes = getSedes();
      setOptions($sede(), sedes, sedes.length ? "Seleccione sede" : "Sin sedes");
      clearSelect($dep(), "Seleccione sede primero");
      clearSelect($sub(), "Seleccione dependencia primero");

      // listeners
      $sede()?.addEventListener("change", () => refreshDeps());
      $dep()?.addEventListener("change", () => refreshSubs());
    },

    // setea y respeta jerarquía
    setValue({ sede = "", dependencia = "", subdependencia = "" } = {}) {
      if (!ORG) return;

      // sede
      if (sede && getSedes().includes(sede)) {
        $sede().value = sede;
      } else {
        $sede().value = "";
      }

      // dependencia + sub
      refreshDeps(dependencia || "", subdependencia || "");
    },

    reset() {
      if (!$sede()) return;
      $sede().value = "";
      clearSelect($dep(), "Seleccione sede primero");
      clearSelect($sub(), "Seleccione dependencia primero");
    }
  };
})();