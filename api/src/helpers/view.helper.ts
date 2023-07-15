import logger from '../utils/logger.util';
import {Response} from 'express';
import {join} from 'node:path';
import * as Twig from 'twig';

/**
 * Renders a page using Twig.js and sends the rendered HTML as the response.
 *
 * @param {Response} res - The response object to send the rendered page.
 * @param {string} templateName - The name of the template to render.
 * @param {Twig.RenderOptions} options - The render options for the template.
 * @returns {Promise<Response>} A Promise that resolves to the response object.
 *
 * @example
 * // Render a page and send the response
 * const templateName = 'home';
 * const options = { data: { title: 'Home Page' } };
 *
 * renderPage(res, templateName, options)
 *   .then((response) => {
 *     // Handle successful rendering and response
 *   })
 *   .catch((error) => {
 *     // Handle error during rendering or response
 *   });
 */
export default async function renderPage(
  res: Response,
  templateName: string,
  options: Twig.RenderOptions
): Promise<Response> {
  const templatePath = join(
    __dirname,
    `../www/pages/${templateName}.html.twig`
  );

  try {
    const renderedHtml = await renderTemplate(templatePath, options);
    return res.status(200).send(renderedHtml);
  } catch (error) {
    logger.error(`Error while rendering template '${templateName}' ${error}`);
    return res.status(500).json({
      success: false,
      message: 'Internal Server Error!',
    });
  }
}

/**
 * Renders a template using Twig.js.
 *
 * @description
 * This function takes a template path and render options and returns a Promise that resolves to the rendered HTML.
 *
 * @example
 * // Render a template and log the result
 * const templatePath = 'path/to/template.twig';
 * const options = { data: { name: 'John Doe' } };
 * renderTemplate(templatePath, options)
 *   .then((html) => {
 *     console.log(html);
 *   })
 *   .catch((error) => {
 *     console.error(error);
 *   });
 */
async function renderTemplate(
  templatePath: string,
  options: Twig.RenderOptions
): Promise<string> {
  return new Promise((resolve, reject) => {
    Twig.renderFile(templatePath, options, (error, html) => {
      if (error) {
        reject(error);
      } else {
        resolve(html);
      }
    });
  });
}
