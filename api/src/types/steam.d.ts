export interface SteamJWT {
  iss: string;
  sub: string;
  aud: string[];
  exp: number;
  nbf: number;
  iat: number;
  jti: string;
  oat: number;
  per: number;
  ip_subject: string;
  ip_confirmer: string;
}

export interface SteamData {
  username: string;
  refreshToken: string;
  tokenExpiration: number;
}
