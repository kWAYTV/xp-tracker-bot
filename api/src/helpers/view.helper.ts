import logger from '../utils/logger.util';
import {Response} from 'express';
import {join} from 'node:path';
import * as Twig from 'twig';

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
