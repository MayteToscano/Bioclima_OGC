/*
 * BioClima viewer - UI translations.
 * The data labels themselves come from the ontology, not from this file.
 */
window.UI_STRINGS = {
  en: {
    subtitle: "OGC Building Blocks viewer",
    language: "Language",
    layers:   "Layers",
    time:     "Time",
    legend:   "Legend",
    policy:   "Policy alignment",
    footer:   "Register: ",
    value:    "Value",
    unit:     "Unit",
    cell:     "Cell",
    pci:      "PCI",
    category: "Category",
    noData:   "No data at this location"
  },
  es: {
    subtitle: "Visor de bloques OGC",
    language: "Idioma",
    layers:   "Capas",
    time:     "Tiempo",
    legend:   "Leyenda",
    policy:   "Alineación con políticas",
    footer:   "Registro: ",
    value:    "Valor",
    unit:     "Unidad",
    cell:     "Celda",
    pci:      "PCI",
    category: "Categoría",
    noData:   "Sin datos en este punto"
  },
  zh: {
    subtitle: "OGC 构建块查看器",
    language: "语言",
    layers:   "图层",
    time:     "时间",
    legend:   "图例",
    policy:   "政策对齐",
    footer:   "注册表:",
    value:    "数值",
    unit:     "单位",
    cell:     "单元",
    pci:      "PCI",
    category: "类别",
    noData:   "此位置无数据"
  },
  ro: {
    subtitle: "Vizualizator OGC Building Blocks",
    language: "Limbă",
    layers:   "Straturi",
    time:     "Timp",
    legend:   "Legendă",
    policy:   "Alinierea cu politici",
    footer:   "Registru: ",
    value:    "Valoare",
    unit:     "Unitate",
    cell:     "Celulă",
    pci:      "PCI",
    category: "Categorie",
    noData:   "Nu există date în această locație"
  }
};

window.applyTranslations = function (lang) {
  const dict = window.UI_STRINGS[lang] || window.UI_STRINGS.en;
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) el.textContent = dict[key];
  });
};
