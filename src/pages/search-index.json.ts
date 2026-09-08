import armor from "../data/oncehuman_armor.json";
import weapons from "../data/oncehuman_weapons.json";
import ammo from "../data/oncehuman_ammo.json";
import food from "../data/oncehuman_food.json";
import deviations from "../data/oncehuman_deviations.json";

export function GET() {
  const entries = [
    ...armor.map((x) => ({
      title: x.title,
      href: `/armor/${x.slug}/`,
      sub: `Armor · ${x.fields?.hp || "?"} HP · ${x.fields?.armor_type || "?"}`,
    })),
    ...weapons.map((x) => ({
      title: x.title,
      href: `/weapons/${x.slug}/`,
      sub: `Weapon · ${x.fields?.dmg || "?"} dmg · ${x.fields?.weapon_type || ""}`,
    })),
    ...ammo.map((x) => ({
      title: x.title,
      href: `/ammo/${x.slug}/`,
      sub: `Ammo · ${x.fields?.type || ""} · ${x.fields?.rarity || ""}`,
    })),
    ...food.map((x) => ({
      title: x.title,
      href: `/food/${x.slug}/`,
      sub: `Food · ${x.fields?.status_energy || "?"} energy · ${x.fields?.status_hydration || "?"} hydration`,
    })),
    ...deviations.map((x) => ({
      title: x.title,
      href: `/deviations/${x.slug}/`,
      sub: `Deviation · ${x.fields?.rarity || ""}`,
    })),
  ].sort((a, b) => a.title.localeCompare(b.title));
  return new Response(JSON.stringify(entries), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}
