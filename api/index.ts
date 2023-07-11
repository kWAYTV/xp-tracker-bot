import {startCSGO} from './src/controllers/steam.controller';
import WebServer from './src/server';
import 'dotenv/config';

const defaultPort: number = Number.parseInt(`${process.env.SERVER_PORT}`);
const fallbackPort: number = Number.parseInt(
  `${process.env.SERVER_PORT_FALLBACK}`
);

startCSGO().then(() => {
  new WebServer(defaultPort || fallbackPort);
});
