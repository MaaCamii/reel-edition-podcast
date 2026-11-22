// Paleta por defecto para los subtítulos y títulos. edit.json puede
// sobrescribir cualquier color en "paleta". Ajusta estos valores a la marca
// (ver references/estilo-agora.md).
export const DEFAULT_PALETTE = {
  texto: "#FFFFFF",
  primario: "#FFD54A", // palabra activa / título
  acento: "#4ADE80", // keywords resaltadas
  sombra: "rgba(0,0,0,0.6)",
  franja: "rgba(8,11,24,0.50)",
};

export type Palette = typeof DEFAULT_PALETTE;

export const mergePalette = (p?: Partial<Palette>): Palette => ({
  ...DEFAULT_PALETTE,
  ...(p || {}),
});
