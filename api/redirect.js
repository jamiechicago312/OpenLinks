const {
  buildDestinationUrl,
  getRedirectDefinition,
  normalizePathname,
} = require("../redirects");
const { fallbackDestination, redirectsBySource } = require("../redirects-loader");
const { notifyClick } = require("../lib/telegram");

const INTERNAL_PATHNAME_QUERY_KEY = "__oh_redirect_pathname";

function getRequestUrl(req) {
  const host = req.headers.host;
  const protocol = req.headers["x-forwarded-proto"] || "https";
  return new URL(req.url, `${protocol}://${host}`);
}

function getRequestPathname(req, requestUrl) {
  const routedPathname = req.query?.[INTERNAL_PATHNAME_QUERY_KEY];
  return normalizePathname(routedPathname || requestUrl.pathname);
}

function getIncomingSearchParams(requestUrl) {
  const incomingSearchParams = new URLSearchParams(requestUrl.searchParams);
  incomingSearchParams.delete(INTERNAL_PATHNAME_QUERY_KEY);
  return incomingSearchParams;
}

module.exports = async function handler(req, res) {
  const requestUrl = getRequestUrl(req);
  const requestPathname = getRequestPathname(req, requestUrl);
  const incomingSearchParams = getIncomingSearchParams(requestUrl);
  const redirectDefinition = getRedirectDefinition(
    requestPathname,
    redirectsBySource,
    fallbackDestination,
  );
  const destinationUrl = buildDestinationUrl(
    redirectDefinition.destination,
    incomingSearchParams,
  );

  res.setHeader("Cache-Control", "no-store, no-cache, must-revalidate");
  res.setHeader("Location", destinationUrl.toString());
  res.statusCode = redirectDefinition.statusCode;
  res.end();

  notifyClick({
    shortPath: requestPathname,
    timestamp: new Date().toISOString(),
    city: req.headers["x-vercel-ip-city"],
    country: req.headers["x-vercel-ip-country"],
    userAgent: req.headers["user-agent"],
    referer: req.headers["referer"] || req.headers["referrer"],
  });
};
