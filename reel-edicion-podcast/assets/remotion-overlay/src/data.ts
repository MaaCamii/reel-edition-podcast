import { staticFile } from "remotion";

export type Word = { text: string; startS: number; endS: number };
export type Overlay = {
  tipo: "img" | "emoji";
  valor: string;
  inicioS: number;
  finS: number;
  pos?: string; // centro | sup | inf | sup-izq | sup-der | inf-izq | inf-der
  escala?: number; // img: fracción del ancho (0.25). emoji: múltiplo de tamaño base.
  fade?: number; // segundos
};
export type EditData = {
  video: string;
  fps: number;
  durationS: number;
  paleta?: Record<string, string>;
  titulo?: string;
  tituloDur?: number;
  keywords?: string[];
  banda?: "baja" | "centro";
  progreso?: boolean;
  words: Word[];
  overlays?: Overlay[];
};

export async function loadEditData(): Promise<EditData> {
  const res = await fetch(staticFile("edit.json"));
  if (!res.ok) {
    throw new Error(
      "No se encontró public/edit.json. Genera el proyecto con preparar_remotion.sh."
    );
  }
  const d = (await res.json()) as EditData;
  d.fps = d.fps || 30;
  d.words = d.words || [];
  d.overlays = d.overlays || [];
  if (!d.durationS) {
    const last = d.words[d.words.length - 1];
    d.durationS = last ? last.endS + 0.5 : 10;
  }
  return d;
}
