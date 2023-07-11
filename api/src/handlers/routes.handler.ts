import logger from '../utils/logger.util';
import {Application} from 'express';
import {readdirSync} from 'node:fs';
import {join} from 'node:path';

const routesPath = join(__dirname, '../routes/');
const errorRouteFile = 'catchall.route.ts';
const routesExtension = '.route.ts';

/**
 * Get the list of route files in the configured routes path.
 *
 * @returns {string[]} - Array of route file names.
 *
 * @description
 * This function reads the contents of the routes path directory and filters
 * the files based on the configured route extension.
 *
 * @example
 * const routeFiles = getRouteFiles();
 */
function getRouteFiles(): string[] {
  const routeFiles = readdirSync(routesPath).filter(f =>
    f.endsWith(routesExtension)
  );
  return routeFiles;
}

/**
 * Register routes in the Express application.
 *
 * @param {Application} serverInstance - The Express application instance.
 * @returns {void}
 *
 * @description
 * This function dynamically registers routes based on the route files found
 * in the configured routes path. The route named "catchall.route.ts" is
 * registered as the last route.
 *
 * @example
 * registerRoutes(app);
 */
export default function registerRoutes(serverInstance: Application): void {
  const routeFiles = getRouteFiles();
  const otherRouteFiles = routeFiles.filter(f => f !== errorRouteFile);

  try {
    for (const file of otherRouteFiles) {
      const fileHandler = require(join(routesPath, file)).default;
      if (typeof fileHandler === 'function') {
        fileHandler(serverInstance);
        logger.info(`Registered route '${file}'`);
      } else {
        logger.warn(
          `Error while registering route from file '${file}'. Wrong type of handler.`
        );
      }
    }

    const errorRouteHandler = require(join(routesPath, errorRouteFile)).default;
    if (typeof errorRouteHandler === 'function') {
      errorRouteHandler(serverInstance);
      logger.info(`Registered route '${errorRouteFile}' as the last route.`);
    } else {
      logger.warn(
        `Error while registering route from file '${errorRouteFile}'. Wrong type of handler.`
      );
    }
  } catch (error) {
    logger.error(`Unknown error during registration of a route! ${error}`);
  }
}
