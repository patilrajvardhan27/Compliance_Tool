/**
 * Open/save files on the user's own machine. Chromium browsers get real Open/Save dialogs via
 * the File System Access API (and "Save" can silently re-write the same file); other browsers
 * fall back to a standard <input type="file"> picker and a Downloads-folder download.
 */

export interface OpenedLocalFile {
  file: File;
  /** Present only when the File System Access API is available (enables in-place re-save). */
  handle: FileSystemFileHandle | null;
}

const TCT_TYPE: FilePickerAcceptType = {
  description: "TUNBEEC project",
  accept: { "application/octet-stream": [".tct"] },
};

/** True when Save can write back to the originally opened file without re-prompting. */
export function supportsFilePickers(): boolean {
  return typeof window !== "undefined" && !!window.showOpenFilePicker && !!window.showSaveFilePicker;
}

/** Returns null when the user cancels the picker. */
export async function openLocalTct(): Promise<OpenedLocalFile | null> {
  if (window.showOpenFilePicker) {
    try {
      const [handle] = await window.showOpenFilePicker({ types: [TCT_TYPE], multiple: false });
      return { file: await handle.getFile(), handle };
    } catch (e) {
      if ((e as DOMException).name === "AbortError") return null;
      throw e;
    }
  }
  return new Promise((resolve) => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".tct";
    input.onchange = () => resolve(input.files?.[0] ? { file: input.files[0], handle: null } : null);
    // "cancel" fires on modern browsers when the dialog is dismissed without a choice
    input.oncancel = () => resolve(null);
    input.click();
  });
}

export interface SavedLocalFile {
  handle: FileSystemFileHandle | null;
  fileName: string;
}

/** Writes to an existing handle without any dialog. */
export async function writeToHandle(handle: FileSystemFileHandle, blob: Blob): Promise<void> {
  const writable = await handle.createWritable();
  await writable.write(blob);
  await writable.close();
}

/**
 * "Save As": real save dialog where available, otherwise a browser download named
 * `suggestedName`. Returns null when the user cancels.
 */
export async function saveLocalFile(
  blob: Blob,
  suggestedName: string,
  type: FilePickerAcceptType = TCT_TYPE
): Promise<SavedLocalFile | null> {
  if (window.showSaveFilePicker) {
    try {
      const handle = await window.showSaveFilePicker({ types: [type], suggestedName });
      await writeToHandle(handle, blob);
      return { handle, fileName: handle.name };
    } catch (e) {
      if ((e as DOMException).name === "AbortError") return null;
      throw e;
    }
  }
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = suggestedName;
  a.click();
  URL.revokeObjectURL(url);
  return { handle: null, fileName: suggestedName };
}

export const HTML_TYPE: FilePickerAcceptType = {
  description: "HTML report",
  accept: { "text/html": [".html"] },
};
