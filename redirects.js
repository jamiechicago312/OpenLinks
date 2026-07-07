const redirectsConfig = require("./redirects.config.json");

const DEFAULT_REDIRECT_STATUS = 307;
const PERMANENT_REDIRECT_STATUS = 308;

function normalizePathname(pathname) {
  if (!pathname || pathname === "/") {
    return "/";
  }

  const trimmedPathname = pathname.startsWith("/") ? pathname : `/${pathname}`;
  return trimmedPathname.endsWith("/")
    ? trimmedPathname.slice(0, -1)
    : trimmedPathname;
}

function getRedirectStatusCode(permanent) {
  return permanent ? PERMANENT_REDIRECT_STATUS : DEFAULT_REDIRECT_STATUS;
}

function buildRedirectIndex(links) {
  const index = new Map();
  for (const link of links) {
    if (!link || typeof link.slug !== "string" || typeof link.destination !== "string") {
      continue;
    }
    index.set(normalizePathname(link.slug), {
      destination: link.destination,
      permanent: Boolean(link.permanent),
    });
  }
  return index;
}

function getRedirectDefinition(pathname, redirectsBySource, fallbackDestination) {
  const normalizedPathname = normalizePathname(pathname);
  const configuredRedirect = redirectsBySource.get(normalizedPathname);

  if (configuredRedirect) {
    return {
      source: normalizedPathname,
      destination: configuredRedirect.destination,
      permanent: configuredRedirect.permanent,
      isFallback: false,
      statusCode: getRedirectStatusCode(configuredRedirect.permanent),
    };
  }

  return {
    source: normalizedPathname,
    destination: fallbackDestination,
    permanent: false,
    isFallback: true,
    statusCode: DEFAULT_REDIRECT_STATUS,
  };
}

function buildDestinationUrl(destination, incomingSearchParams) {
  const destinationUrl = new URL(destination);

  for (const [key, value] of incomingSearchParams.entries()) {
    destinationUrl.searchParams.append(key, value);
  }

  return destinationUrl;
}

module.exports = {
  DEFAULT_REDIRECT_STATUS,
  PERMANENT_REDIRECT_STATUS,
  buildDestinationUrl,
  buildRedirectIndex,
  getRedirectDefinition,
  getRedirectStatusCode,
  normalizePathname,
  redirectsConfig,
};
