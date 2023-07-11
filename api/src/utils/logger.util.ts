import {StreamOptions} from 'morgan';
import {join} from 'node:path';
import winston from 'winston';

/**
 * Custom logger class that uses Winston for logging.
 */
class Logger {
  private logger: winston.Logger;

  /**
   * Constructs a new Logger instance.
   */
  public constructor() {
    // Logger configuration
    const consoleTransport = new winston.transports.Console({
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.printf(({level, message, timestamp}) => {
          return `[${timestamp}] ${level}: ${message}`;
        })
      ),
    });

    const fileTransport = new winston.transports.File({
      filename: join(__dirname, '../../logs/combined.log'),
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
    });

    const errorFileTransport = new winston.transports.File({
      filename: join(__dirname, '../../logs/error.log'),
      level: 'error',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
    });

    this.logger = winston.createLogger({
      level: 'info',
      transports: [consoleTransport, fileTransport, errorFileTransport],
    });
  }

  /**
   * Returns a stream option for use with Morgan middleware.
   *
   * @returns {StreamOptions} - A stream option for logging with Morgan.
   */
  public getMorganStream(): StreamOptions {
    return {
      write: (message: string) => {
        this.logger.info(message.trim());
      },
    };
  }

  /**
   * Returns the underlying Winston logger instance.
   *
   * @returns {Logger} - The Winston logger instance.
   */
  public getLogger(): winston.Logger {
    return this.logger;
  }
}

// Create a new Logger instance and retrieve the logger
const newLogger = new Logger();
const logger: winston.Logger = newLogger.getLogger();

// Export the Morgan stream option and the default logger instance
export const morganStream = newLogger.getMorganStream();
export default logger;
