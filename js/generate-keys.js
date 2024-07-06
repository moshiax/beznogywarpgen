const httpx = require('httpx');
const fs = require('fs').promises;

exports.handler = async function(event, context) {
    const numKeys = JSON.parse(event.body).num_keys;
    const keys = (await fs.readFile('./basekeys.txt', 'utf8')).split('\n').filter(Boolean);
    const gkeys = [];
    const headers = {
        "CF-Client-Version": "a-6.11-2223",
        "Host": "api.cloudflareclient.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.12.1",
    };

    for (let i = 0; i < numKeys; i++) {
        try {
            const client = new httpx.Client({
                baseURL: "https://api.cloudflareclient.com/v0a2223",
                headers: headers,
                timeout: 30000
            });

            let r = await client.post('/reg');
            let { id, account: { license }, token } = r.data;

            r = await client.post('/reg');
            let id2 = r.data.id;
            let token2 = r.data.token;

            const headersGet = { "Authorization": `Bearer ${token}` };
            const headersGet2 = { "Authorization": `Bearer ${token2}` };
            const headersPost = {
                "Content-Type": "application/json; charset=UTF-8",
                "Authorization": `Bearer ${token}`
            };

            await client.patch(`/reg/${id}`, { referrer: `${id2}` }, { headers: headersPost });
            await client.delete(`/reg/${id2}`, { headers: headersGet2 });

            let key = keys[Math.floor(Math.random() * keys.length)];

            await client.put(`/reg/${id}/account`, { license: `${key}` }, { headers: headersPost });
            await client.put(`/reg/${id}/account`, { license: `${license}` }, { headers: headersPost });

            r = await client.get(`/reg/${id}/account`, { headers: headersGet });
            license = r.data.license;

            await client.delete(`/reg/${id}`, { headers: headersGet });

            gkeys.push(license);
        } catch (err) {
            console.error("Error.", err);
        }
    }

    await fs.appendFile('./basekeys.txt', gkeys.join('\n') + '\n');

    return {
        statusCode: 200,
        body: JSON.stringify({ keys: gkeys })
    };
}
