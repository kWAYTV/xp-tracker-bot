import {Application} from 'express';
import helmet from 'helmet';

export default function (serverInstance: Application) {
  serverInstance.use(
    helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'", 'https://checker.kwayservices.top'],
          scriptSrc: ["'self'", "'unsafe-inline'"],
        },
      },
    })
  );
}
