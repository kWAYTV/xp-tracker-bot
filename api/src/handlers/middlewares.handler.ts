import logger from '../utils/logger.util';
import {Application} from 'express';
import {readdirSync} from 'node:fs';
import {join} from 'node:path';

const middlewaresPath = join(__dirname, '../middlewares/');
const middlewaresExtension = '.middleware.ts';

/**
 * Get the list of middleware files in the configured middlewares path.
 *
 * @returns {string[]} - Array of middleware file names.
 *
 * @description
 * This function reads the contents of the middlewares path directory and filters
 * the files based on the configured middleware extension.
 *
 * @example
 * const middlewareFiles = getMiddewareFiles();
 */
function getMiddewareFiles(): string[] {
  const middlewareFiles = readdirSync(middlewaresPath).filter(f =>
    f.endsWith(middlewaresExtension)
  );
  return middlewareFiles;
}

/**
 * Registers middlewares in the Express application.
 *
 * @param {Application} serverInstance - The Express application instance.
 * @returns {void}
 *
 * @description
 * This function dynamically registers middlewares based on the middleware files
 * found in the configured middlewares path.
 *
 * @example
 * registerMiddlewares(app);
 */
export default function registerMiddlewares(serverInstance: Application): void {
  const middlewaresFile = getMiddewareFiles();

  try {
    for (const file of middlewaresFile) {
      const fileHandler = require(join(middlewaresPath, file)).default;
      if (typeof fileHandler === 'function') {
        fileHandler(serverInstance);
        logger.info(`Registered middleware '${file}'`);
      } else {
        logger.warn(
          `Error while registering middleware '${file}'! Wrong type of handler!`
        );
      }
    }
  } catch (error) {
    logger.error(
      `Unknown error occured during registration of a middleware! ${error}`
    );
  }
}
