import logger from '../utils/logger.util';
import {SteamJWT} from '../types/steam';

/**
 * Decodes a JSON Web Token (JWT) and returns its payload as a SteamJWT object.
 *
 * @description This function takes a JWT token as input, decodes the payload,
 * and returns the decoded data as a SteamJWT object. If there's an error during
 * decoding, it logs an error and returns an empty object as the SteamJWT result.
 *
 * @param {string} token - The JWT token to be decoded.
 * @returns {SteamJWT} The decoded JWT payload as a SteamJWT object.
 *
 * @example
 * // Usage example:
 * const jwtToken = 'JWT_TOKEN';
 * const decodedToken = decodeJWT(jwtToken);
 * console.log(decodedToken);
 * // Output:
 * // {
 * //   iss: 'steam',
 * //   sub: '1234567890',
 * //   iat: 1630593235,
 * //   exp: 1630593235,
 * //   jti: '1234567890',
 * //   oat: 1630593235,
 * //   per: 1,
 * //   ip_subject: '127.0.0.1',
 * //   ip_confirmer: '127.0.0.1'
 * // }
 */
export function decodeJWT(token: string): SteamJWT {
  const payload = token.split('.')[1];
  const decoded = Buffer.from(payload, 'base64');

  try {
    const parsedData = JSON.parse(decoded.toString());
    return parsedData;
  } catch (error) {
    logger.error('Error while decoding JWT! {error}');
    return {} as SteamJWT;
  }
}

/**
 * Checks if a JWT token or any timestamp-based expiration is expired or not.
 *
 * @description This function compares the given `expiration` timestamp with the current timestamp
 * (both in seconds) and returns `true` if the `expiration` is in the past (expired), or `false`
 * if it's still valid (not expired).
 *
 * @param {number} expiration - The expiration timestamp to check (in seconds).
 * @returns {boolean} `true` if the expiration is in the past (expired), or `false` if it's still valid (not expired).
 *
 * @example
 * // Example usage with JWT token expiration:
 * const jwtExpiration = 1707589787;
 * const isExpired = isExpired(jwtExpiration);
 * console.log('Is JWT token expired?', isExpired);
 * // Output: Is JWT token expired? true
 */
export function isExpired(expiration: number) {
  const currentTimestamp = Math.floor(Date.now() / 1000);
  return expiration < currentTimestamp;
}
