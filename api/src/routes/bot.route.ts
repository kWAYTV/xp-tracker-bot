import {Application, Request, Response} from 'express';

export default function (serverInstance: Application) {
    serverInstance.get('/bot/invite', async (_: Request, res: Response) => {
    const redirectURL = 'https://discord.com/api/oauth2/authorize?client_id=1128130924165464114&permissions=137707777104&scope=bot%20applications.commands';
    return res.redirect(redirectURL);
    });
}