/**
 * godotConfig.ts
 * Módulo de configuración y utilidades puras para integrar la compilación WebAssembly de Godot 4.7.2-stable
 * dentro de la aplicación web React/Vite.
 */

export interface GodotRuntimeConfig {
  engineVersion: string;
  entryUrl: string;
  projectTitle: string;
}

export type GodotLoadState = 'loading' | 'ready' | 'error';

export const DEFAULT_GODOT_CONFIG: GodotRuntimeConfig = {
  engineVersion: '4.7.2-stable',
  entryUrl: '/godot/index.html',
  projectTitle: 'Encuentra Gatos 3D - Godot Hello World',
};

/**
 * Normaliza la URL de entrada del export Web de Godot asegurando una ruta relativa válida
 * y propagando parámetros opcionales como autostart.
 */
export function buildGodotEntryUrl(basePath: string, autostart = false): string {
  const trimmed = basePath.trim();
  if (!trimmed) {
    throw new Error('La ruta base de Godot no puede estar vacía.');
  }
  const normalized = trimmed.startsWith('/') ? trimmed : `/${trimmed}`;
  if (!autostart) {
    return normalized;
  }
  const separator = normalized.includes('?') ? '&' : '?';
  return `${normalized}${separator}autostart=1`;
}

/**
 * Verifica si el estado actual del runtime permite interactuar con el canvas de Godot.
 */
export function isGodotInteractive(state: GodotLoadState): boolean {
  return state === 'ready';
}
