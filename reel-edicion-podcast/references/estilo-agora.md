# Estilo de marca para los reels

Mantén coherencia con la skill hermana `reel-educativo-ia` y con
`agora-social-content`. Si el usuario confirma los colores/tipografía oficiales
de ÁgoraLAB, actualízalos aquí y en `assets/remotion-overlay/src/palette.ts`.

## Paleta por defecto (heredada de reel-educativo-ia)
```
texto      #FFFFFF   (subtítulo normal)
primario   #FFD54A   (palabra activa / título)  — amarillo Ágora
acento     #4ADE80   (keywords resaltadas)      — verde
fondo osc. #0B1020   (franjas, title chips)
```
> Confirma con el usuario los valores oficiales de marca antes de publicar en
> serie. Un solo color de acento, usado con criterio, se ve más pro que muchos.

## Tipografía
- Por defecto se usa la fuente del sistema (sans, peso 900) para máxima legibilidad.
- Para fuente de marca (p. ej. Montserrat/Poppins), instala el `.ttf` y cárgalo
  en Remotion (ver `subtitulos-y-overlays.md`). Prioriza un sans grueso y legible
  en pantalla pequeña.

## Reglas de legibilidad
- Subtítulos grandes (≈78 px sobre 1080 de ancho), peso fuerte, con sombra.
- Máximo 3 palabras por "línea" activa; frases cortas se leen mejor en vertical.
- Contraste alto siempre: franja semitransparente detrás del texto si el fondo es claro.
- **Safe areas:** deja libre el 12% inferior (UI de la app) y ~6% de cada borde.
- Título arriba, subtítulos en el tercio inferior: no los solapes.

## Tono
- **Pedagógico y con neutralidad partidista.** El reel enseña algo cívico; no
  toma partido ni saca frases de contexto para insinuar una postura.
- **Fidelidad al hablante:** los subtítulos reflejan lo dicho. No se inventan
  frases ni se "mejora" el mensaje.
- Cierre con intención: que la persona entienda algo mejor que antes de ver el reel.

## Elementos complementarios (usar con mesura)
- Un dato/cifra en pantalla cuando refuerza el punto exacto que se dice.
- Emojis como acento puntual, no decoración constante.
- Logo discreto (esquina, ~16% del ancho) para identidad.
- Barra de progreso: ayuda a la retención; actívala salvo que reste.
