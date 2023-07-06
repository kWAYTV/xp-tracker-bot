const fs = require('fs');
const { createCanvas, loadImage } = require('canvas');

function wrapText(context, text, x, y, maxWidth, lineHeight) {
    const words = text.split(' ');
    let line = '';

    for(let n = 0; n < words.length; n++) {
        const testLine = line + words[n] + ' ';
        const metrics = context.measureText(testLine);
        const testWidth = metrics.width;
        if (testWidth > maxWidth && n > 0) {
            context.fillText(line, x, y);
            line = words[n] + ' ';
            y += lineHeight;
        }
        else {
            line = testLine;
        }
    }
    context.fillText(line, x, y);
}

module.exports.create = async function(medalData, queue_id) {
    const padding = 20;
    const medalSize = 100;
    const medalsPerRow = 15;
    const lineHeight = 15;
    const maxWidth = medalSize;
    const leftMargin = 15; // Add a left margin

    const rows = Math.ceil(medalData.length / medalsPerRow);
    const canvasWidth = medalsPerRow * (medalSize + padding) + leftMargin; // Increase canvas width by the size of the left margin
    const canvasHeight = rows * (medalSize + padding * 2);

    const canvas = createCanvas(canvasWidth, canvasHeight);
    const ctx = canvas.getContext('2d');
    ctx.font = 'bold 11px Comic Sans MS';

    ctx.fillStyle = '#2B2D31';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);

    Promise.all(medalData.map(medal => loadImage(`./src/medals/${medal.medal_id}.png`)))
        .then((images) => {
            images.forEach((img, i) => {
                const x = (i % medalsPerRow) * (medalSize + padding) + leftMargin; // Increase x coordinate by the size of the left margin
                const y = Math.floor(i / medalsPerRow) * (medalSize + padding * 2);

                ctx.drawImage(img, x, y, medalSize, medalSize);
                ctx.fillStyle = '#ffffff'; // Set the font color to white
                wrapText(ctx, medalData[i].medal_name.trim(), x, y + medalSize + padding, maxWidth, lineHeight); // Wrap text
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
