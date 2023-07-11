import registerMiddlewares from './handlers/middlewares.handler';
import registerRoutes from './handlers/routes.handler';
import express, {Application} from 'express';
import logger from './utils/logger.util';

export default class WebServer {
  private webServer: Application;

  public constructor(port: number) {
    this.webServer = express();

    this.registerMiddlewares();
    this.registerRoutes();

    this.run(port);
  }

  private registerMiddlewares() {
    registerMiddlewares(this.webServer);
  }

  private registerRoutes() {
    registerRoutes(this.webServer);
  }

  private run(port: number) {
    this.webServer.listen(port, () => {
      logger.info(`Server is running on http://localhost:${port}/`);
      logger.info('Try by sending a request to /test');
    });
  }
}
