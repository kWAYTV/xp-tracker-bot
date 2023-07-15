import {createCanvas, loadImage, CanvasRenderingContext2D} from 'canvas';
import logger from './logger.util';
import {join} from 'node:path';
import fs from 'fs';

const medalsPath = join(__dirname, '../data/medals/');
const medalsOutputPath = join(__dirname, '../data/medals/output/');

// Check if 'output' folder exists, if not create it
if (!fs.existsSync(medalsOutputPath)) {
  fs.mkdirSync(medalsOutputPath);
}

/**
 * Wraps the provided text within a specified width on a canvas using the given context.
 * The wrapped text is rendered starting from the provided coordinates (x, y).
 *
 * @param {CanvasRenderingContext2D} context - The canvas rendering context.
 * @param {string} text - The text to be wrapped.
 * @param {number} x - The x-coordinate to start rendering the wrapped text.
 * @param {number} y - The y-coordinate to start rendering the wrapped text.
 * @param {number} maxWidth - The maximum width for each line of the wrapped text.
 * @param {number} lineHeight - The height of each line of text.
 * @returns {number} - The number of lines created by the text wrapping.
 *
 * @description
 * This function takes in a canvas rendering context, a text string, coordinates (x, y)
 * specifying the starting position, a maximum width for each line, and a line height.
 * It wraps the text within the specified width and renders it on the canvas starting
 * from the provided coordinates. The function returns the number of lines created by
 * the text wrapping.
 *
 * @example
 * const canvas = document.createElement('canvas');
 * const context = canvas.getContext('2d');
 * const text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non enim eu dui mattis facilisis.';

 * const x = 10;
 * const y = 10;
 * const maxWidth = 200;
 * const lineHeight = 20;

 * const numLines = wrapText(context, text, x, y, maxWidth, lineHeight);
 * logger.info(`Number of lines created: ${numLines}`);
 */
function wrapText(
  context: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  maxWidth: number,
  lineHeight: number
): number {
  const words = text.split(' ');
  let line = '';
  let lines = 1;

  for (let n = 0; n < words.length; n++) {
    const testLine = line + words[n] + ' ';
    const metrics = context.measureText(testLine);
    const testWidth = metrics.width;
    if (testWidth > maxWidth && n > 0) {
      context.fillText(line, x, y);
      line = words[n] + ' ';
      y += lineHeight;
      lines++;
    } else {
      line = testLine;
    }
  }
  context.fillText(line, x, y);
  return lines;
}

/**
 * Creates a composite image containing multiple medals along with their corresponding names,
 * and saves it as a PNG file. The medals and names are provided in the `medalData` array.
 *
 * @param {any[]} medalData - An array of medal data objects.
 * @param {string} queue_id - The identifier for the queue.
 * @returns {Promise<void>} - A promise that resolves when the PNG file is created.
 *
 * @description
 * This function takes in an array of medal data objects and a queue identifier.
 * It generates a composite image containing the medals and their names in a grid-like layout.
 * The resulting image is saved as a PNG file with the name specified by the `queue_id`.
 * The function returns a promise that resolves when the PNG file is successfully created.
 *
 * The layout of the medals on the image is determined by the `medalsPerRow` and `margin` constants.
 * The size of each medal is specified by the `medalSize` constant.
 * The padding between medals and around the image is controlled by the `padding` constant.
 * The font and font size used for rendering the medal names are set by the `ctx.font` property.
 *
 * @example
 * const medalData = [
 *   { medalId: 'medal1', medalName: 'First Medal' },
 *   { medalId: 'medal2', medalName: 'Second Medal' },
 * ];
 * const queue_id = 'queue1';
 *
 * create(medalData, queue_id)
 *   .then(() => {
 *     logger.info(`The PNG file ${queue_id}.png was created.`);
 *   })
 *   .catch(error => {
 *     logger.error('Error creating the PNG file:', error);
 *   });
 */
export async function create(
  medalData: any[],
  queue_id: string
): Promise<void> {
  const padding = 15;
  const medalSize = 100;
  const medalsPerRow = 15;
  const lineHeight = 12;
  const maxWidth = medalSize;
  const margin = 15;

  const actualMedalsPerRow = Math.min(medalData.length, medalsPerRow);
  const rows = Math.ceil(medalData.length / medalsPerRow);

  const canvasWidth =
    actualMedalsPerRow * (medalSize + padding) - padding + 2 * margin;

  const canvas = createCanvas(canvasWidth, 0);
  const ctx = canvas.getContext('2d')!;
  ctx.font = 'bold 11px Arial';

  let maxTextHeightPerRow = 0;
  for (let i = 0; i < medalData.length; i++) {
    const medalName = medalData[i].medalName
      ? medalData[i].medalName.trim()
      : '';
    const textHeight =
      wrapText(ctx, medalName, 0, 0, maxWidth, lineHeight) * lineHeight;
    if (i % actualMedalsPerRow === actualMedalsPerRow - 1) {
      maxTextHeightPerRow = Math.max(maxTextHeightPerRow, textHeight);
    }
  }

  const canvasHeight =
    rows * (medalSize + padding + maxTextHeightPerRow) - padding + 2 * margin;
  canvas.height = canvasHeight;

  ctx.fillStyle = '#2B2D31';
  ctx.fillRect(0, 0, canvasWidth, canvasHeight);

  Promise.all(
    medalData.map(medal => {
      if (medal.medalId) {
        return loadImage(join(medalsPath, `${medal.medalId}.png`));
      } else {
        logger.error(
          `Medal with index ${medalData.indexOf(medal)} has no medalId property`
        );
        return null;
      }
    })
  )
    .then(images => {
      images.forEach((img, i) => {
        if (img) {
          const x = margin + (i % actualMedalsPerRow) * (medalSize + padding);
          const y =
            margin +
            Math.floor(i / actualMedalsPerRow) *
              (medalSize + padding + maxTextHeightPerRow);

          ctx.drawImage(img, x, y, medalSize, medalSize);
          ctx.fillStyle = '#ffffff';
          const medalName = medalData[i].medalName
            ? medalData[i].medalName.trim()
            : '';
          wrapText(
            ctx,
            medalName,
            x,
            y + medalSize + padding,
            maxWidth,
            lineHeight
          );
        }
      });

      const out = fs.createWriteStream(
        join(medalsOutputPath, `${queue_id}.png`)
      );
      const stream = canvas.createPNGStream();
      stream.pipe(out);
      out.on('finish', () =>
        logger.info(`The PNG file ${queue_id}.png was created.`)
      );
    })
    .catch(err => {
      logger.error(err);
    });
}
