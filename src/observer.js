'use strict';
// The view. Reads world state and draws it; never mutates the model. The field is painted into a
// W×H OffscreenCanvas (one pixel per cell) and scaled up in a single drawImage — no DOM, and no
// per-cell fillRect. Browser-only in practice; headless runs never construct it.
//
// Goats: does tan, bucks dark brown, kids small and pale; each goat is offset inside its cell by a
// hash of its id so a herd sharing cells reads as a cluster. Wolves: hunting (hungry) red, sated grey.
var Observer = class Observer {
  constructor(world, cellPx) {
    this.world = world;
    this.px = cellPx;
    this.off = new OffscreenCanvas(world.W, world.H);
    this.octx = this.off.getContext('2d');
    this.img = this.octx.createImageData(world.W, world.H);
  }

  update() {}

  draw(ctx) {
    const w = this.world, d = this.img.data, px = this.px;
    for (let i = 0; i < w.N; i++) {
      let r, g, b;
      if (w.river[i]) { r = 40; g = 90; b = 170; }
      else {
        const v = w.veg[i], e = w.elev[i];
        // bare ground: brown in the valley → grey-brown in the uplands; vegetation tints green
        const br = 120 + 50 * e, bg = 100 + 40 * e, bb = 70 + 50 * e;
        r = br * (1 - v) + 40 * v; g = bg * (1 - v) + 150 * v; b = bb * (1 - v) + 50 * v;
        if (w.escape[i]) { r *= 0.7; g *= 0.7; b *= 0.75; }
      }
      d[4 * i] = r; d[4 * i + 1] = g; d[4 * i + 2] = b; d[4 * i + 3] = 255;
    }
    this.octx.putImageData(this.img, 0, 0);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(this.off, 0, 0, w.W * px, w.H * px);

    ctx.fillStyle = '#e04040';
    for (const c of w.camps) ctx.fillRect(c.x * px - 2, c.y * px - 2, px + 4, px + 4);

    // goats
    for (const g of w.goats) {
      if (g.dead) continue;
      const h = (g.id * 2654435761) >>> 0, ox = (h & 7) / 8 * (px - 3), oy = ((h >>> 3) & 7) / 8 * (px - 3);
      const kid = g.isKid(), s = kid ? 2 : 3;
      ctx.fillStyle = g.herd >= 0 ? (kid ? '#ffd6f0' : '#ff66cc') : (kid ? '#f4ead2' : (g.sex === SEX_F ? '#e8c27a' : '#6b3f1d'));
      ctx.fillRect(g.x * px + ox, g.y * px + oy, s, s);
    }
    // wolves
    for (const wf of w.wolves) {
      ctx.fillStyle = wf.fullness < PARAMETERS.wolfHungry ? '#ff2020' : '#9aa0a6';
      ctx.fillRect(wf.x * px + 2, wf.y * px + 2, px - 4, px - 4);
    }

    // humans: hunters where they spent the day (blue), others at camp (white)
    for (const h of w.humans) {
      ctx.fillStyle = h.herding ? '#ffe000' : h.captive ? '#ff8c00' : h.hunting ? '#3fa9ff' : h.foraging ? '#3ccf5a' : '#ffffff';
      ctx.beginPath(); ctx.arc(h.x * px + px / 2, h.y * px + px / 2, px / 2 - 1, 0, TAU); ctx.fill();
    }

    ctx.fillStyle = '#fff'; ctx.font = '12px sans-serif';
    const season = w.growth > 0 ? 'growing' : 'lean';
    const c = w.census();
    ctx.fillText(`year ${w.year} · day ${w.day} · ${season} (${(w.growth * 100) | 0}%) · goats ${c.goats} (kids ${c.kids}) · wolves ${w.wolves.length} · humans ${w.humans.length}`, 8, w.H * px - 8);
    ctx.font = '11px sans-serif';
    let lx = 8;
    for (const [col, label] of [['#e8c27a', 'doe'], ['#6b3f1d', 'buck'], ['#f4ead2', 'kid'], ['#ff2020', 'wolf hunting'], ['#9aa0a6', 'wolf sated'], ['#3fa9ff', 'hunter'], ['#3ccf5a', 'forager'], ['#ff8c00', 'leading a captive'], ['#ffe000', 'herder'], ['#ff66cc', 'herded goat']]) {
      ctx.fillStyle = col; ctx.fillRect(lx, 5, 9, 9);
      ctx.fillStyle = '#fff'; ctx.fillText(label, lx + 12, 14); lx += 18 + ctx.measureText(label).width;
    }
    ctx.fillText('dark ground = cliffs (escape terrain)', lx + 6, 14);
  }
};
