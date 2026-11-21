/**
 * godotConfig.test.ts
 * Pruebas unitarias con node:test para validar la construcción de rutas y el estado del entorno Godot Web.
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import {
  DEFAULT_GODOT_CONFIG,
  buildGodotEntryUrl,
  isGodotInteractive,
} from './godotConfig';

test('buildGodotEntryUrl normaliza rutas con o sin barra inicial', () => {
  assert.equal(buildGodotEntryUrl('/godot/index.html'), '/godot/index.html');
  assert.equal(buildGodotEntryUrl('godot/index.html'), '/godot/index.html');
});

test('buildGodotEntryUrl agrega autostart=1 cuando se solicita', () => {
  assert.equal(
    buildGodotEntryUrl('/godot/index.html', true),
    '/godot/index.html?autostart=1'
  );
  assert.equal(
    buildGodotEntryUrl('/godot/index.html?lang=es', true),
    '/godot/index.html?lang=es&autostart=1'
  );
});

test('buildGodotEntryUrl lanza error si la ruta está vacía', () => {
  assert.throws(() => buildGodotEntryUrl('   '), /no puede estar vacía/);
});

test('isGodotInteractive solo habilita interacción cuando está listo', () => {
  assert.equal(isGodotInteractive('loading'), false);
  assert.equal(isGodotInteractive('error'), false);
  assert.equal(isGodotInteractive('ready'), true);
  assert.equal(DEFAULT_GODOT_CONFIG.engineVersion, '4.7.2-stable');
});
