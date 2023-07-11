import {XMLParser} from 'fast-xml-parser';
import axios from 'axios';

const parser = new XMLParser();

/**
 * Resolves a SteamID64 based on the given input.
 *
 * @param {string} input - The input string containing the Steam ID or profile URL.
 * @returns {Promise<{ success: boolean; data: string }>} - A promise that resolves with an object indicating the success status and the resolved SteamID64 or error message.
 *
 * @description
 * This function resolves a SteamID64 based on the given input, which can be in different formats:
 * - A 17-digit SteamID64.
 * - A Steam community profile URL in the format 'steamcommunity.com/profiles/{SteamID64}'.
 * - A Steam community profile URL in the format 'steamcommunity.com/id/{CustomID}'.
 *
 * The function constructs the appropriate API URL to retrieve the XML data from the Steam Community API.
 * It then parses the XML response and returns an object indicating the success status and the resolved SteamID64 or error message.
 *
 * If the input format is invalid, the function returns an object with `success` set to `false` and the error message in the `data` field.
 * Upon successful resolution of the SteamID64, the function returns an object with `success` set to `true` and the resolved SteamID64 in the `data` field.
 * In case of any errors during the resolution process, the function returns an object with `success` set to `false` and the error message in the `data` field.
 *
 * @example
 * const input1 = '76561197960287930';
 * const result1 = await getSteam64(input1);
 * // result1: { success: true, data: '76561197960287930' }
 *
 * const input2 = 'https://steamcommunity.com/profiles/76561197960287930';
 * const result2 = await getSteam64(input2);
 * // result2: { success: true, data: '76561197960287930' }
 *
 * const input3 = 'https://steamcommunity.com/id/customprofile';
 * const result3 = await getSteam64(input3);
 * // result3: { success: true, data: '76561197960287930' }
 *
 * const input4 = 'invalid input';
 * const result4 = await getSteam64(input4);
 * // result4: { success: false, data: 'Invalid input format: invalid input' }
 */
export default async function getSteam64(
  input: string
): Promise<{success: boolean; data: Record<string, any> | string}> {
  let apiUrl = '';

  if (input.length === 17 && /^\d+$/.test(input)) {
    apiUrl = `https://steamcommunity.com/profiles/${input}?xml=1`;
  } else if (input.includes('steamcommunity.com/profiles/')) {
    const splittedInput = input.split('/');
    apiUrl = `https://steamcommunity.com/profiles/${
      splittedInput[splittedInput.length - 1]
    }?xml=1`;
  } else if (input.includes('steamcommunity.com/id/')) {
    const splittedInput = input.split('/');
    apiUrl = `https://steamcommunity.com/id/${
      splittedInput[splittedInput.length - 1]
    }?xml=1`;
  } else {
    apiUrl = `https://steamcommunity.com/id/${input}?xml=1`;
  }

  try {
    const response = await axios.get(apiUrl);
    const parsedData = parser.parse(response.data);

    if (parsedData.profile && parsedData.profile.steamID64) {
      return {
        success: true,
        data: {
          id: parsedData.profile.steamID64,
          nickname: parsedData.profile.steamID,
          avatar: parsedData.profile.avatarFull,
        },
      };
    } else {
      return {
        success: false,
        data: `Unable to resolve SteamID64 for input: ${input}`,
      };
    }
  } catch (error) {
    return {
      success: false,
      data: `Failed to fetch SteamID64 for input: ${input}. Error: ${error}`,
    };
  }
}