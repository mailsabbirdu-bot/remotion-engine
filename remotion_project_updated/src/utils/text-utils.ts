/**
 * Safe Grapheme Splitter with Intl.Segmenter
 */
export const splitIntoGraphemes = (text: string): string[] => {
  if (typeof Intl !== "undefined" && (Intl as any).Segmenter) {
    const segmenter = new (Intl as any).Segmenter("bn", {
      granularity: "grapheme"
    });
    return Array.from(segmenter.segment(text)).map(
      (s: any) => s.segment
    );
  }
  return Array.from(text);
};

/**
 * Detects the font to use for a given character.
 */
export const getFontForChar = (char: string): "EnglishFont" | "BanglaFont" => {
  if (/[a-zA-Z0-9]/.test(char)) {
    return "EnglishFont";
  }

  if (/[\s\.,!\?\(\)\[\]\{\}:;'"_&%\$#@\*=\+\-\/\\<>|\|]/.test(char)) {
    return "EnglishFont";
  }

  return "BanglaFont";
};
