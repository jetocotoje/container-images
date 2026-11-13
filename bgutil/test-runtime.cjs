const assert = require("node:assert/strict");
const { X509Certificate } = require("node:crypto");
const { rootCertificates } = require("node:tls");

const minimum = [1, 2, 1];
const actual = process.versions.brotli.split(".").map(Number);
const firstDifference = actual.findIndex((part, index) => part !== minimum[index]);
assert.ok(
  firstDifference === -1 || actual[firstDifference] > minimum[firstDifference],
  `Expected Brotli >= ${minimum.join(".")}, actual ${process.versions.brotli}`,
);

const affectedRoots = rootCertificates
  .map((pem) => new X509Certificate(pem).subject)
  .filter((subject) =>
    subject.includes("CN=emSign ECC Root CA - G3") ||
    subject.includes("CN=AAA Certificate Services")
  );
assert.deepEqual(affectedRoots, []);

require("/app/node_modules/canvas");
console.log(`Node ${process.version}, Brotli ${process.versions.brotli}: no affected roots; canvas loads`);
