// static/js/modal.js
(() => {
  const modal = () => document.getElementById("modal");
  const title = () => document.getElementById("modalTitle");
  const saveBtn = () => document.getElementById("saveBtn");
  const form = () => document.getElementById("userForm");

  const fields = [
    "usuario_red","dni","nombres","apellidos",
    "correo","ip_equipo","host",

    "tipo_contrato","contrato_inicio","contrato_fin",
    "sede","dependencia","subdependencia",

    "acceso_nivel","acceso_redes_sociales",
    "permisos_activos","permiso_inicio","permiso_fin",

    "vpn_activo","equipo_personal","antivirus","antivirus_fin",
    "vpn_inicio","vpn_fin"
  ];

  function setDisabledAll(disabled) {
    form()?.querySelectorAll("input,select,textarea,button").forEach((el) => {
      if (el.id === "saveBtn") return;
      el.disabled = disabled;
    });
  }

  function toggleAntivirusFields() {
    const vpn = (document.getElementById("vpn_activo")?.value || "NO").toUpperCase();
    const eqp = (document.getElementById("equipo_personal")?.value || "NO").toUpperCase();

    const av = document.getElementById("antivirus");
    const avf = document.getElementById("antivirus_fin");

    const show = (vpn === "SI" && eqp === "SI");

    if (av) av.disabled = !show;
    if (avf) avf.disabled = !show;

    if (!show) {
      if (av) av.value = "";
      if (avf) avf.value = "";
    }
  }

  function fillForm(data) {
    fields.forEach((k) => {
      const el = document.getElementById(k);
      if (!el) return;
      el.value = (data?.[k] ?? "");
    });

    // combos org
    if (window.OrgCombos) {
      window.OrgCombos.setValue({
        sede: data?.sede || "",
        dependencia: data?.dependencia || "",
        subdependencia: data?.subdependencia || ""
      });
    }

    toggleAntivirusFields();
  }

  window.openModal = async function (mode) {
    modal().style.display = "block";

    // init combos si aún no
    if (window.OrgCombos && !window.__ORG_INIT__) {
      window.__ORG_INIT__ = true;
      try { await window.OrgCombos.init(); } catch (e) { console.error(e); }
    }

    if (mode === "view") {
      title().innerText = "Ver usuario";
      saveBtn().style.display = "none";
      setDisabledAll(true);
    } else if (mode === "edit") {
      title().innerText = "Editar usuario";
      saveBtn().style.display = "block";
      setDisabledAll(false);
      const ur = document.getElementById("usuario_red");
      if (ur) ur.readOnly = true;
    } else {
      title().innerText = "Registrar usuario";
      saveBtn().style.display = "block";
      setDisabledAll(false);

      const ur = document.getElementById("usuario_red");
      if (ur) ur.readOnly = false;

      if (window.OrgCombos) window.OrgCombos.reset();
      toggleAntivirusFields();
    }
  };

  window.closeModal = function () {
    modal().style.display = "none";
    form()?.reset();
    setDisabledAll(false);
    saveBtn().style.display = "block";

    const ur = document.getElementById("usuario_red");
    if (ur) ur.readOnly = false;

    if (window.OrgCombos) window.OrgCombos.reset();
    toggleAntivirusFields();
  };

  window.editUser = async function (data) {
    await window.openModal("edit");
    fillForm(data);
  };

  window.viewUser = async function (data) {
    await window.openModal("view");
    fillForm(data);
  };

  document.addEventListener("change", (e) => {
    if (!e.target) return;
    if (e.target.id === "vpn_activo" || e.target.id === "equipo_personal") {
      toggleAntivirusFields();
    }
  });

  // cerrar al hacer click fuera
  window.addEventListener("click", (e) => {
    const m = modal();
    if (e.target === m) window.closeModal();
  });

  // cerrar con ESC
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal()?.style.display === "block") window.closeModal();
  });
})();