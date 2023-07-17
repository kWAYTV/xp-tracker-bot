import db from '../database/database.connection';
import logger from '../utils/logger.util';
import {SteamData} from '../types/steam';

/**
 * Inserts data into the database using the provided SteamData object.
 *
 * @description This function inserts the provided `data` into the database using the `db.insert` method.
 * It returns a Promise that resolves to `true` if the data insertion is successful, or rejects with an error
 * if there's an error during the insertion process.
 *
 * @param {SteamData} data - The data to be inserted into the database.
 * @returns {Promise<boolean>} A Promise that resolves to `true` if the data insertion is successful, or rejects with an error.
 *
 * @example
 * // Example usage:
 * const dataToInsert: SteamData = {
 *   steamId64: '76561198859916296',
 *   refreshToken: 'YOUR_REFRESH_TOKEN',
 *   tokenExpiration: 1707589787,
 * };
 *
 * insert(dataToInsert)
 *   .then(() => {
 *     logger.info('Data inserted successfully.');
 *   })
 *   .catch((error) => {
 *     logger.error(`Error inserting data: ${error}`);
 *   });
 */
export async function insert(data: SteamData): Promise<boolean> {
  return await new Promise((resolve, reject) => {
    db.insert(data, (error, document) => {
      if (error) {
        logger.error(
          `Error while inserting data into database! ${error.message}`
        );
      } else {
        document ? resolve(true) : reject(error);
      }
    });
  });
}

/**
 * Selects data from the database based on the provided filter object.
 *
 * @description This function queries the database for data that matches the provided `data` filter object using the `db.findOne` method.
 * It returns a Promise that resolves to the found document if data is found, or rejects with an error if there's an error during the retrieval process.
 *
 * @param {Record<string, any>} data - The filter object used to match data in the database.
 * @returns {Promise<Record<string, any> | null>} A Promise that resolves to the found document if data is found, or rejects with an error.
 *
 * @example
 * // Example usage:
 * const filterObject: Record<string, any> = {
 *   steamId64: '76561198859916296',
 * };
 *
 * select(filterObject)
 *   .then((document) => {
 *     if (document) {
 *       logger.info('Data found:', document);
 *     } else {
 *       logger.info('Data not found.');
 *     }
 *   })
 *   .catch((error) => {
 *     logger.error(`Error getting data: ${error}`);
 *   });
 */
export async function select(
  data: Record<string, any>
): Promise<Record<string, any> | null> {
  return new Promise((resolve, reject) => {
    db.findOne(data, (error, document) => {
      if (error) {
        logger.error(`Error while getting data for ${JSON.stringify(data)}`);
        reject(error);
      } else {
        resolve(document || null);
      }
    });
  });
}

/**
 * Removes records from the database based on the provided filter object.
 *
 * @description This function removes records from the database that match the provided `data` filter object
 * using the `db.remove` method. It returns a Promise that resolves to the number of removed records if successful,
 * or `null` if there's an error during the deletion process.
 *
 * @param {Record<string, any>} data - The filter object used to match records in the database for deletion.
 * @returns {Promise<number | null>} A Promise that resolves to the number of removed records if successful, or `null` if there's an error.
 *
 * @example
 * // Example usage:
 * const filterObject: Record<string, any> = {
 *   steamId64: '76561198859916296',
 * };
 *
 * remove(filterObject)
 *   .then((numberOfRemovedRecords) => {
 *     if (numberOfRemovedRecords !== null) {
 *       logger.info(`${numberOfRemovedRecords} record(s) removed successfully.`);
 *     } else {
 *       logger.info('No records found matching the filter.');
 *     }
 *   })
 *   .catch((error) => {
 *     logger.error(`Error removing records: ${error}`);
 *   });
 */
export async function remove(
  data: Record<string, any>
): Promise<number | null> {
  return new Promise((resolve, reject) => {
    db.remove(data, {}, (error, n) => {
      if (error) {
        logger.error(`Error while deleting record for ${JSON.stringify(data)}`);
        reject(error);
      } else {
        resolve(n || null);
      }
    });
  });
}
