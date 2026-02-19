// static/js/org-query.js
(async () => {
  const $sede = document.getElementById("q_sede");
  const $dep = document.getElementById("q_dependencia");
  const $sub = document.getElementById("q_subdependencia");
  if (!$sede || !$dep || !$sub) return;

  const defaults = window.ACCESSUTI_QUERY_DEFAULTS || { sede:"", dependencia:"", subdependencia:"" };

  const orgUrl = (window.ACCESSUTI && window.ACCESSUTI.orgUrl) ? window.ACCESSUTI.orgUrl : null;
  if (!orgUrl) return;

  const res = await fetch(orgUrl);
  const data = await res.json();

  // Soporta varios formatos:
  // 1) { "SEDE": { "DEPENDENCIA": ["SUB1","SUB2"] } }
  // 2) { "sedes": [ { "nombre": "...", "dependencias":[{ "nombre":"...", "subdependencias":[...] }]} ] }
  function normalize(org) {
    // Formato 1
    if (org && typeof org === "object" && !Array.isArray(org) && !org.sedes) return org;

    // Formato 2
    const out = {};
    const sedes = org?.sedes || [];
    for (const s of sedes) {
      const sName = s.nombre || s.name || "";
      if (!sName) continue;
      out[sName] = {};
      for (const d of (s.dependencias || s.dependencies || [])) {
        const dName = d.nombre || d.name || "";
        if (!dName) continue;
        out[sName][dName] = (d.subdependencias || d.subdependencies || []).map(x => x.nombre || x.name || x).filter(Boolean);
      }
    }
    return out;
  }

  const ORG = normalize(data);

  function fillSelect(sel, items, placeholder) {
    sel.innerHTML = "";
    const opt0 = document.createElement("option");
    opt0.value = "";
    opt0.textContent = placeholder;
    sel.appendChild(opt0);

    items.forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t;
      opt.textContent = t;
      sel.appendChild(opt);
    });
  }

  const sedes = Object.keys(ORG).sort((a,b)=>a.localeCompare(b));
  fillSelect($sede, sedes, "Todas");

  function refreshDeps() {
    const sede = $sede.value;
    const deps = sede && ORG[sede] ? Object.keys(ORG[sede]) : [];
    fillSelect($dep, deps.sort((a,b)=>a.localeCompare(b)), "Todas");
    refreshSubs();
  }

  function refreshSubs() {
    const sede = $sede.value;
    const dep = $dep.value;
    const subs = (sede && dep && ORG[sede] && ORG[sede][dep]) ? ORG[sede][dep] : [];
    fillSelect($sub, [...subs].sort((a,b)=>a.localeCompare(b)), "Todas");
  }

  $sede.addEventListener("change", refreshDeps);
  $dep.addEventListener("change", refreshSubs);

  // Aplicar defaults (cuando vienes filtrado)
  if (defaults.sede) $sede.value = defaults.sede;
  refreshDeps();
  if (defaults.dependencia) $dep.value = defaults.dependencia;
  refreshSubs();
  if (defaults.subdependencia) $sub.value = defaults.subdependencia;
})();