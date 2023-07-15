import {readFileSync} from 'node:fs';
import {join} from 'node:path';

const proxiesFilePath = join(__dirname, '../data/proxies.txt');

/**
 * Retrieves a random proxy from the list of available proxies.
 *
 * @returns {string} - A randomly selected proxy.
 *
 * @description
 * This function reads the list of available proxies from the specified file path and returns a random proxy from the list.
 * The file should contain one proxy per line.
 *
 * @example
 * const randomProxy = getRandomProxy();
 * // randomProxy: 'http://proxy.example.com:8080'
 */
export function getRandomProxy(): string {
  const proxies = readFileSync(proxiesFilePath).toString();
  const splittedProxies = proxies.split('\n');

  const randomProxy =
    splittedProxies[Math.floor(Math.random() * splittedProxies.length)];
  return randomProxy;
}
