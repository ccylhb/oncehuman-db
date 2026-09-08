# -*- coding: utf-8 -*-
"""Generate OnceHumanDB list + detail pages (token substitution)."""
import os

BASE = "src/pages"

LIST_TPL = '''---
import Base from "../../layouts/Base.astro";
import DataTable from "../../components/DataTable.astro";
import Related from "../../components/Related.astro";
import @VAR@ from "../../data/oncehuman_@BOARD@.json";

const n = (v) => {
  const m = String(v ?? "").match(/-?\\d+(?:\\.\\d+)?/);
  return m ? parseFloat(m[0]) : "";
};
const rows = @VAR@
  .map((x) => ({
    name: `<a href="/@BOARD@/${x.slug}/">${x.title}</a>`,
    _sort: x.title.toLowerCase(),
@ROWFIELDS@
  }))
  .sort((a, b) => a._sort.localeCompare(b._sort));
---
<Base
  title="@TITLE@ — ${@VAR@.length} entries with exact values"
  description="@DESC@ for ${@VAR@.length} Once Human @LABELLOW@."
>
  <h1>@LABEL@</h1>
  <p class="muted">${@VAR@.length} entries · click a column to sort.</p>
  <DataTable
    id="@BOARD@"
    rows={rows}
    searchPlaceholder="Search @LABELLOW@..."
    columns={[
@COLUMNS@
    ]}
  />
  <Related
    links={[
@RELATED@
    ]}
  />
</Base>
'''

DETAIL_TPL = '''---
import Base from "../../layouts/Base.astro";
import Related from "../../components/Related.astro";
import EntryStats from "../../components/EntryStats.astro";
import @VAR@ from "../../data/oncehuman_@BOARD@.json";

export function getStaticPaths() {
  return @VAR@.map((x) => ({ params: { slug: x.slug }, props: { x } }));
}

const { x } = Astro.props;
const f = x.fields || {};
const similar = @VAR@
  .filter((o) => o.slug !== x.slug && (o.fields?.rarity || "") === (f.rarity || ""))
  .slice(0, 6);
---
<Base
  title={`${x.title} — Once Human @BOARD@ stats`}
  description={`${x.title}: Once Human @BOARD@ values — exact stats from the wiki infobox.`}
>
  <h1>{x.title}</h1>
  {f.quote && <p class="muted">{f.quote}</p>}
  <EntryStats entry={x} keys={@DKEYS@} labels={@DLABELS@} />
  <p>
    {f.rarity && <span class="tag" style="margin:0.1rem">{f.rarity}</span>}
    {f.armor_type && <span class="tag" style="margin:0.1rem">{f.armor_type}</span>}
    {f.weapon_type && <span class="tag" style="margin:0.1rem">{f.weapon_type}</span>}
    {f.type && <span class="tag" style="margin:0.1rem">{f.type}</span>}
    {f.style && <span class="tag" style="margin:0.1rem">{f.style}</span>}
  </p>
  {f.armor_features && <p><strong>Features:</strong> {f.armor_features}</p>}
  {f.weapon_features && <p><strong>Features:</strong> {f.weapon_features}</p>}
  {x.intro && <p>{x.intro}</p>}
  <Related
    links={[
      ...similar.map((s) => ({
        href: `/@BOARD@/${s.slug}/`,
        title: s.title,
      })),
      { href: "/@BOARD@/", title: "All @LABEL@", sub: "Sortable table" },
      { href: "/rankings/", title: "Rankings", sub: "Best picks" },
    ]}
  />
</Base>
'''

boards = {
    "armor": {
        "varname": "armor",
        "label": "Armor",
        "desc": "HP, durability and resistances",
        "row_fields": '''    type: (x.fields?.armor_type || "").slice(0, 14),
    hp: n(x.fields?.hp),
    dur: n(x.fields?.durability),
    pollution: n(x.fields?.pollution_resist),
    psi: n(x.fields?.psi_intensity),
    weight: n(x.fields?.weight),
    rarity: (x.fields?.rarity || "").slice(0, 12),''',
        "columns": '''      { key: "name", label: "Piece" },
      { key: "type", label: "Slot" },
      { key: "hp", label: "HP", type: "number" },
      { key: "dur", label: "Durability", type: "number" },
      { key: "pollution", label: "Pollution res.", type: "number" },
      { key: "psi", label: "Psi intensity", type: "number" },
      { key: "weight", label: "Weight", type: "number" },
      { key: "rarity", label: "Rarity" },''',
        "dkeys": '["hp", "durability", "pollution_resist", "psi_intensity", "weight"]',
        "dlabels": '{ hp: "HP", durability: "Durability", pollution_resist: "Pollution resistance", psi_intensity: "Psi intensity", weight: "Weight" }',
    },
    "weapons": {
        "varname": "weapons",
        "label": "Weapons",
        "desc": "damage, crit and magazine values",
        "row_fields": '''    dmg: n(x.fields?.dmg),
    crit: n(x.fields?.crit_rate),
    weak: n(x.fields?.weakspot_dmg),
    mag: n(x.fields?.magazine_capacity),
    rarity: (x.fields?.rarity || "").slice(0, 12),
    wtype: (x.fields?.weapon_type || "").slice(0, 16),''',
        "columns": '''      { key: "name", label: "Weapon" },
      { key: "dmg", label: "Damage", type: "number" },
      { key: "crit", label: "Crit rate (%)", type: "number" },
      { key: "weak", label: "Weakspot dmg (%)", type: "number" },
      { key: "mag", label: "Magazine", type: "number" },
      { key: "wtype", label: "Type" },
      { key: "rarity", label: "Rarity" },''',
        "dkeys": '["dmg", "crit_rate", "crit_dmg", "weakspot_dmg", "fire_rate", "magazine_capacity", "durability", "weight"]',
        "dlabels": '{ dmg: "Damage", crit_rate: "Crit rate", crit_dmg: "Crit damage", weakspot_dmg: "Weakspot damage", fire_rate: "Fire rate", magazine_capacity: "Magazine", durability: "Durability", weight: "Weight" }',
    },
    "ammo": {
        "varname": "ammo",
        "label": "Ammo",
        "desc": "rarity, type and stack sizes",
        "row_fields": '''    atype: (x.fields?.type || "").slice(0, 16),
    stack: n(x.fields?.stack_size),
    rarity: (x.fields?.rarity || "").slice(0, 12),
    quote: (x.fields?.quote || "").slice(0, 60),''',
        "columns": '''      { key: "name", label: "Ammo" },
      { key: "atype", label: "Type" },
      { key: "stack", label: "Stack size", type: "number" },
      { key: "rarity", label: "Rarity" },
      { key: "quote", label: "Notes" },''',
        "dkeys": '["stack_size", "rarity", "type", "tradeability"]',
        "dlabels": '{ stack_size: "Stack size", rarity: "Rarity", type: "Type", tradeability: "Tradeability" }',
    },
    "food": {
        "varname": "food",
        "label": "Food",
        "desc": "energy, hydration and stack values",
        "row_fields": '''    energy: n(x.fields?.status_energy),
    hydration: n(x.fields?.status_hydration),
    stack: n(x.fields?.stack_size),
    weight: n(x.fields?.weight),
    rarity: (x.fields?.rarity || "").slice(0, 12),
    ftype: (x.fields?.type || "").slice(0, 16),''',
        "columns": '''      { key: "name", label: "Food" },
      { key: "energy", label: "Energy", type: "number" },
      { key: "hydration", label: "Hydration", type: "number" },
      { key: "stack", label: "Stack", type: "number" },
      { key: "weight", label: "Weight", type: "number" },
      { key: "ftype", label: "Type" },
      { key: "rarity", label: "Rarity" },''',
        "dkeys": '["status_energy", "status_hydration", "stack_size", "weight", "rarity", "type"]',
        "dlabels": '{ status_energy: "Energy", status_hydration: "Hydration", stack_size: "Stack size", weight: "Weight", rarity: "Rarity", type: "Type" }',
    },
    "deviations": {
        "varname": "deviations",
        "label": "Deviations",
        "desc": "deviation companions and abilities",
        "row_fields": '''    dtype: (x.fields?.type || "").slice(0, 16),
    rarity: (x.fields?.rarity || "").slice(0, 12),
    quote: (x.fields?.quote || "").slice(0, 70),''',
        "columns": '''      { key: "name", label: "Deviation" },
      { key: "dtype", label: "Type" },
      { key: "rarity", label: "Rarity" },
      { key: "quote", label: "Notes" },''',
        "dkeys": '["rarity", "type"]',
        "dlabels": '{ rarity: "Rarity", type: "Type" }',
    },
}

related_map = {
    "armor": '''      { href: "/rankings/", title: "Rankings", sub: "Best armor" },
      { href: "/weapons/", title: "Weapons", sub: "Damage values" },
      { href: "/food-calculator/", title: "Food Calculator", sub: "Plan intake", tool: true },''',
    "weapons": '''      { href: "/ammo/", title: "Ammo", sub: "Ammo types" },
      { href: "/rankings/", title: "Rankings", sub: "Best weapons" },
      { href: "/armor/", title: "Armor", sub: "Armor values" },''',
    "ammo": '''      { href: "/weapons/", title: "Weapons", sub: "Damage values" },
      { href: "/rankings/", title: "Rankings", sub: "Best picks" },
      { href: "/food/", title: "Food", sub: "Energy & hydration" },''',
    "food": '''      { href: "/food-calculator/", title: "Food Calculator", sub: "Plan intake", tool: true },
      { href: "/rankings/", title: "Rankings", sub: "Best food" },
      { href: "/deviations/", title: "Deviations", sub: "Companions" },''',
    "deviations": '''      { href: "/food/", title: "Food", sub: "Energy & hydration" },
      { href: "/rankings/", title: "Rankings", sub: "Best picks" },
      { href: "/armor/", title: "Armor", sub: "Armor values" },''',
}


def fill(tpl, mapping):
    for k, v in mapping.items():
        tpl = tpl.replace(k, v)
    return tpl


for board, cfg in boards.items():
    mapping = {
        "@BOARD@": board,
        "@VAR@": cfg["varname"],
        "@TITLE@": "Once Human " + cfg["label"],
        "@DESC@": cfg["desc"],
        "@LABEL@": cfg["label"],
        "@LABELLOW@": cfg["label"].lower(),
        "@ROWFIELDS@": cfg["row_fields"],
        "@COLUMNS@": cfg["columns"],
        "@RELATED@": related_map[board],
        "@DKEYS@": cfg["dkeys"],
        "@DLABELS@": cfg["dlabels"],
    }
    os.makedirs(f"{BASE}/{board}", exist_ok=True)
    open(f"{BASE}/{board}/index.astro", "w", encoding="utf-8").write(fill(LIST_TPL, mapping))
    open(f"{BASE}/{board}/[slug].astro", "w", encoding="utf-8").write(fill(DETAIL_TPL, mapping))

print("generated:", os.listdir(BASE))
