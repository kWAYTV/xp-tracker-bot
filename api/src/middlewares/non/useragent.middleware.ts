import {Request, Response, NextFunction} from 'express';

export default function authUA(
  req: Request,
  res: Response,
  next: NextFunction
) {
  const allowedUserAgent = 'kWS-Auth';

  if (!req.headers['user-agent']?.includes(allowedUserAgent)) {
    return res
      .status(401)
      .json({success: false, message: 'Missmatched request!'});
  }

  return next();
}
