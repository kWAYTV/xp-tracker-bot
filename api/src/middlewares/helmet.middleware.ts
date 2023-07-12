import {Application} from 'express';
import helmet from 'helmet';

export default function (serverInstance: Application) {
  serverInstance.use(
    helmet({
      // Enable loading scripts from inside the <body>-Tag
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'", "'unsafe-inline'"],
        },
      },
    })
  );
}
