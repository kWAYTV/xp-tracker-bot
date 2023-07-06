const fs = require('fs');
const { createCanvas, loadImage } = require('canvas');

function wrapText(context, text, x, y, maxWidth, lineHeight) {
    const words = text.split(' ');
    let line = '';
    let lines = 1;

    for(let n = 0; n < words.length; n++) {
        const testLine = line + words[n] + ' ';
        const metrics = context.measureText(testLine);
        const testWidth = metrics.width;
        if (testWidth > maxWidth && n > 0) {
            context.fillText(line, x, y);
            line = words[n] + ' ';
            y += lineHeight;
            lines++;
        }
        else {
            line = testLine;
        }
    }
    context.fillText(line, x, y);
    return lines;
}

module.exports.create = async function(medalData, queue_id) {
    const padding = 15;
    const medalSize = 100;
    const medalsPerRow = 15;
    const lineHeight = 12;
    const maxWidth = medalSize;
    const margin = 15; 

    const actualMedalsPerRow = Math.min(medalData.length, medalsPerRow);
    const rows = Math.ceil(medalData.length / medalsPerRow);
    
    const canvasWidth = actualMedalsPerRow * (medalSize + padding) - padding + 2 * margin;

    const canvas = createCanvas(canvasWidth, 0);
    const ctx = canvas.getContext('2d');
    ctx.font = 'bold 11px Comic Sans MS';

    let maxTextHeightPerRow = 0;
    for (let i = 0; i < medalData.length; i++) {
        const textHeight = wrapText(ctx, medalData[i].medal_name.trim(), 0, 0, maxWidth, lineHeight) * lineHeight;
        if (i % actualMedalsPerRow === actualMedalsPerRow - 1) {
            maxTextHeightPerRow = Math.max(maxTextHeightPerRow, textHeight);
        }
    }

    const canvasHeight = rows * (medalSize + padding + maxTextHeightPerRow) - padding + 2 * margin;
    canvas.height = canvasHeight;

    ctx.fillStyle = '#2B2D31';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);

    Promise.all(medalData.map(medal => loadImage(`./src/medals/${medal.medal_id}.png`)))
        .then((images) => {
            images.forEach((img, i) => {
                const x = margin + (i % actualMedalsPerRow) * (medalSize + padding);
                const y = margin + Math.floor(i / actualMedalsPerRow) * (medalSize + padding + maxTextHeightPerRow);

                ctx.drawImage(img, x, y, medalSize, medalSize);
                ctx.fillStyle = '#ffffff';
                wrapText(ctx, medalData[i].medal_name.trim(), x, y + medalSize + padding, maxWidth, lineHeight);
            });

            const out = fs.createWriteStream(`./src/medals/output/output_${queue_id}.png`);
            const stream = canvas.createPNGStream();
            stream.pipe(out);
            out.on('finish', () => console.log(`The PNG file output_${queue_id}.png was created.`));
        })
        .catch((err) => {
            console.error(err);
        });
}
