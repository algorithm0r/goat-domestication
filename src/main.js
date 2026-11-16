'use strict';
// Browser entry + wiring (not loaded headlessly). reset() rebuilds the world from the current
// PARAMETERS; the boot sequence is straight — no AssetManager gate.
var gameEngine, world, dataManager, db;
var CELL_PX = 10;

function reset() {
  gameEngine.clear();
  world = new World();
  const graph = new LineGraph(10, world.H * CELL_PX + 8, 380, 84, 'goats (every ' + PARAMETERS.reportingPeriod + ' days)');
  db = createDB(PARAMETERS.db);
  dataManager = new DataManager(world, db, graph);
  gameEngine.add(world);
  gameEngine.add(new Observer(world, CELL_PX));
  gameEngine.add(dataManager);
  gameEngine.add(graph);
  if (typeof setStatus === 'function') setStatus('running — ' + world.W + '×' + world.H + ' cells');
}

window.onload = function () {
  const canvas = document.getElementById('gameWorld');
  canvas.width = PARAMETERS.width * CELL_PX;
  canvas.height = PARAMETERS.height * CELL_PX + 100;
  gameEngine = new GameEngine();
  gameEngine.init(canvas.getContext('2d'));
  buildControls();
  reset();
  gameEngine.start();
};
