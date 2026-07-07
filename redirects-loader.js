const fs = require("node:fs");
const path = require("node:path");

const { buildRedirectIndex, redirectsConfig } = require("./redirects");

const LINKS_DIR = path.join(__dirname, "data", "links", "active");

function loadLinkFile(filePath) {
  const raw = fs.readFileSync(filePath, "utf8");
  const parsed = JSON.parse(raw);

  if (!parsed || typeof parsed !== "object") {
    throw new Error(`Link file ${filePath} must be a JSON object`);
  }
  if (typeof parsed.slug !== "string" || parsed.slug.trim() === "") {
    throw new Error(`Link file ${filePath} is missing a string "slug" field`);
  }
  if (typeof parsed.destination !== "string" || parsed.destination.trim() === "") {
    throw new Error(`Link file ${filePath} is missing a string "destination" field`);
  }

  return {
    slug: parsed.slug,
    destination: parsed.destination,
    permanent: Boolean(parsed.permanent),
    description: typeof parsed.description === "string" ? parsed.description : undefined,
    tags: Array.isArray(parsed.tags) ? parsed.tags : undefined,
  };
}

function loadLinksFromDisk(linksDir = LINKS_DIR) {
  if (!fs.existsSync(linksDir)) {
    return [];
  }

  return fs
    .readdirSync(linksDir)
    .filter((name) => name.endsWith(".json") && !name.startsWith("."))
    .sort()
    .map((name) => loadLinkFile(path.join(linksDir, name)));
}

const links = loadLinksFromDisk();
const redirectsBySource = buildRedirectIndex(links);
const fallbackDestination =
  process.env.FALLBACK_DESTINATION || redirectsConfig.fallbackDestination;

module.exports = {
  fallbackDestination,
  links,
  linksDir: LINKS_DIR,
  redirectsBySource,
};
