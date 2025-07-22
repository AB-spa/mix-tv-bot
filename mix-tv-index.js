const { Telegraf } = require('telegraf');
require('dotenv').config();
const axios = require('axios');

const bot = new Telegraf(process.env.BOT_TOKEN);

bot.start((ctx) => {
  ctx.reply('أهلًا بك في بوت Mix TV 🎬
اكتب اسم أي فيلم أو مسلسل للبحث.');
});

bot.on('text', async (ctx) => {
  const query = ctx.message.text;
  try {
    const res = await axios.get(`https://api.themoviedb.org/3/search/multi`, {
      params: {
        api_key: process.env.TMDB_API_KEY,
        query: query,
        language: 'ar'
      }
    });

    const results = res.data.results.slice(0, 5);
    if (!results.length) return ctx.reply('ما في نتائج 😢');

    const reply = results.map(r => `🎬 ${r.title || r.name}
https://www.themoviedb.org/${r.media_type}/${r.id}`).join('

');
    ctx.reply(reply);
  } catch (err) {
    ctx.reply('صار خطأ أثناء البحث 😥');
  }
});

bot.launch();
