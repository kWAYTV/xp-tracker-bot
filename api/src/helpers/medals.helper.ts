import {readFileSync} from 'node:fs';
import {join} from 'node:path';

const medalsDataPath = join(__dirname, '../data/medals/ids.txt');
const medalsData = readFileSync(medalsDataPath, 'utf-8');

const medalsNames: Record<string, string> = {};

medalsData.split('\n').forEach(line => {
  const [id, name] = line.split(';');
  medalsNames[id] = name;
});

/**
 * Retrieves the medals based on the given medal IDs.
 *
 * @param {string[]} medalIds - An array of medal IDs.
 * @returns {Medal[]} - An array of medal objects, each containing the medal ID and name.
 *
 * @description
 * This function takes in an array of medal IDs and retrieves the corresponding medals' names.
 * It returns an array of medal objects, each containing the medal ID and its associated name.
 * If the name for a particular medal ID is not found, an empty string is used as the name.
 *
 * @example
 * const medalIds = ['medal1', 'medal2', 'medal3'];
 * const medals = getMedals(medalIds);
 */
export default function getMedals(medalIds: number[]): object[] {
  return medalIds.map(id => ({
    medalId: id,
    medalName: medalsNames[id] || '',
  }));
}
