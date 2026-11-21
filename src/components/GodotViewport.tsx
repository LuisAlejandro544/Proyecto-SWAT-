/**
 * GodotViewport.tsx
 * Componente modular que aloja el build WebAssembly de Godot 4.7.2-stable en pantalla completa
 * mediante un iframe aislado y accesible.
 */

import { useState } from 'react';
import {
  DEFAULT_GODOT_CONFIG,
  GodotLoadState,
  buildGodotEntryUrl,
} from '../utils/godotConfig';

interface GodotViewportProps {
  entryUrl?: string;
  title?: string;
}

export function GodotViewport({
  entryUrl = DEFAULT_GODOT_CONFIG.entryUrl,
  title = DEFAULT_GODOT_CONFIG.projectTitle,
}: GodotViewportProps) {
  const [loadState, setLoadState] = useState<GodotLoadState>('loading');
  const resolvedUrl = buildGodotEntryUrl(entryUrl);

  return (
    <div
      className="relative h-screen w-screen overflow-hidden bg-slate-950"
      data-godot-state={loadState}
    >
      <iframe
        title={title}
        src={resolvedUrl}
        data-testid="godot-viewport"
        className="h-full w-full border-0 block"
        allow="autoplay; fullscreen; gamepad"
        onLoad={() => setLoadState('ready')}
        onError={() => setLoadState('error')}
      />

      {loadState === 'error' && (
        <div
          role="alert"
          className="absolute inset-0 flex items-center justify-center bg-slate-950 text-slate-100 p-6 text-center"
        >
          <p className="text-base font-medium">
            No se pudo cargar el entorno Web de Godot. Ejecuta el script de exportación primero.
          </p>
        </div>
      )}
    </div>
  );
}
