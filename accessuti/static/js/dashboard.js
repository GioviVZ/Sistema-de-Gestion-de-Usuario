// static/js/dashboard.js
(async () => {
  const cfg = window.ACCESSUTI || {};
  const ep = cfg.endpoints || {};

  async function fetchData(url) {
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error("Error fetch " + url);
    return await res.json();
  }

  function renderXYColumn(divId, data) {
    const root = am5.Root.new(divId);
    root.setThemes([am5themes_Animated.new(root)]);
    root.numberFormatter.setAll({ numberFormat: "#,###" });

    const chart = root.container.children.push(
      am5xy.XYChart.new(root, {
        panX: true, panY: false,
        wheelX: "panX", wheelY: "zoomX",
        paddingLeft: 10, paddingRight: 10,
        paddingTop: 10, paddingBottom: 10
      })
    );

    const xRenderer = am5xy.AxisRendererX.new(root, { minGridDistance: 28 });
    xRenderer.labels.template.setAll({ oversizedBehavior: "wrap", maxWidth: 120, textAlign: "center" });

    const xAxis = chart.xAxes.push(
      am5xy.CategoryAxis.new(root, { categoryField: "category", renderer: xRenderer })
    );

    const yRenderer = am5xy.AxisRendererY.new(root, {});
    const yAxis = chart.yAxes.push(
      am5xy.ValueAxis.new(root, { renderer: yRenderer, min: 0, strictMinMax: true })
    );

    yRenderer.labels.template.setAll({ text: "{value.formatNumber('#,###')}" });

    const series = chart.series.push(
      am5xy.ColumnSeries.new(root, {
        xAxis, yAxis,
        valueYField: "value",
        categoryXField: "category",
        tooltip: am5.Tooltip.new(root, { labelText: "{categoryX}: {valueY.formatNumber('#,###')}" })
      })
    );

    series.columns.template.setAll({ cornerRadiusTL: 10, cornerRadiusTR: 10 });

    xAxis.data.setAll(data);
    series.data.setAll(data);

    const maxVal = Math.max(...data.map(d => Number(d.value || 0)), 0);
    yAxis.setAll({ max: Math.max(1, Math.ceil(maxVal)), extraMax: 0 });

    series.appear(900);
    chart.appear(900, 100);
  }

  function renderXYBar(divId, data) {
    const root = am5.Root.new(divId);
    root.setThemes([am5themes_Animated.new(root)]);
    root.numberFormatter.setAll({ numberFormat: "#,###" });

    const chart = root.container.children.push(
      am5xy.XYChart.new(root, {
        panY: true,
        wheelY: "panY",
        paddingLeft: 12, paddingRight: 12,
        paddingTop: 10, paddingBottom: 10
      })
    );

    const yRenderer = am5xy.AxisRendererY.new(root, { inversed: true });
    yRenderer.labels.template.setAll({ oversizedBehavior: "wrap", maxWidth: 240 });

    const yAxis = chart.yAxes.push(
      am5xy.CategoryAxis.new(root, { categoryField: "category", renderer: yRenderer })
    );

    const xRenderer = am5xy.AxisRendererX.new(root, {});
    const xAxis = chart.xAxes.push(
      am5xy.ValueAxis.new(root, { renderer: xRenderer, min: 0, strictMinMax: true })
    );

    xRenderer.labels.template.setAll({ text: "{value.formatNumber('#,###')}" });

    const series = chart.series.push(
      am5xy.ColumnSeries.new(root, {
        xAxis, yAxis,
        valueXField: "value",
        categoryYField: "category",
        tooltip: am5.Tooltip.new(root, { labelText: "{categoryY}: {valueX.formatNumber('#,###')}" })
      })
    );

    series.columns.template.setAll({ cornerRadiusTR: 10, cornerRadiusBR: 10 });

    yAxis.data.setAll(data);
    series.data.setAll(data);

    const maxVal = Math.max(...data.map(d => Number(d.value || 0)), 0);
    xAxis.setAll({ max: Math.max(1, Math.ceil(maxVal)), extraMax: 0 });

    series.appear(900);
    chart.appear(900, 100);
  }

  function renderDonut(divId, data) {
    const root = am5.Root.new(divId);
    root.setThemes([am5themes_Animated.new(root)]);
    root.numberFormatter.setAll({ numberFormat: "#,###" });

    const chart = root.container.children.push(
      am5percent.PieChart.new(root, { paddingTop: 10, paddingBottom: 10, paddingLeft: 10, paddingRight: 10 })
    );

    const series = chart.series.push(
      am5percent.PieSeries.new(root, {
        valueField: "value",
        categoryField: "category",
        alignLabels: false,
        tooltip: am5.Tooltip.new(root, { labelText: "{category}: {value.formatNumber('#,###')}" })
      })
    );

    series.setAll({
      centerX: am5.percent(50),
      centerY: am5.percent(50),
      radius: am5.percent(85),
      innerRadius: am5.percent(60)
    });

    series.labels.template.setAll({ forceHidden: true });
    series.ticks.template.setAll({ forceHidden: true });

    const legend = chart.children.push(
      am5.Legend.new(root, {
        centerX: am5.percent(50),
        x: am5.percent(50),
        layout: root.horizontalLayout,
        marginTop: 8
      })
    );

    legend.labels.template.setAll({ fontSize: 12 });
    legend.valueLabels.template.setAll({ fontSize: 12 });

    series.data.setAll(data);
    legend.data.setAll(series.dataItems);

    series.appear(900, 100);
  }

  try {
    const sede     = await fetchData(ep.sede);
    const contrato = await fetchData(ep.contrato);
    const permisos = await fetchData(ep.permisos);
    const vpn      = await fetchData(ep.vpn);
    const dep      = await fetchData(ep.dep);
    const sub      = await fetchData(ep.sub);

    renderXYColumn("chartSede", sede);
    renderDonut("chartContrato", contrato);
    renderDonut("chartPermisos", permisos);
    renderDonut("chartVPN", vpn);
    renderXYBar("chartDep", dep);
    renderXYBar("chartSub", sub);
  } catch (e) {
    console.error(e);
  }
})();