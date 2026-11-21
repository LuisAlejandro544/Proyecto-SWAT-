/**
 * App.tsx
 * Punto de entrada de la aplicación web. Renderiza únicamente el contenedor del entorno Godot 4.7.2-stable
 * con la escena inicial Hello World.
 */

import { GodotViewport } from './components/GodotViewport';

export default function App() {
  return (
    <main className="h-screen w-screen overflow-hidden bg-slate-950">
      <GodotViewport />
    </main>
  );
}
