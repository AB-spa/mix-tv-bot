require("dotenv").config();
const { Telegraf } = require("telegraf");
const axios = require("axios");

const bot = new Telegraf(process.env.BOT_TOKEN);
const tmdbApiKey = process.env.TMDB_API_KEY;
const shrinkApi = process.env.SHRINKME_API;

bot.start((ctx) => {
  ctx.reply("🎬 أهلاً بك في بوت Mix TV!\nاختر لغة البحث: /arabic أو /english");
});

bot.command("arabic", (ctx) => {
  ctx.session = { lang: "ar" };
  ctx.reply("أرسل اسم الفيلم أو المسلسل بالعربية 🎥");
});

bot.command("english", (ctx) => {
  ctx.session = { lang: "en" };
  ctx.reply("Send the name of the movie or series in English 🎬");
});

bot.on("text", async (ctx) => {
  const lang = ctx.session?.lang || "ar";
  const query = ctx.message.text;

  try {
    const url = `https://api.themoviedb.org/3/search/multi?api_key=${tmdbApiKey}&language=${lang}&query=${encodeURIComponent(query)}`;
    const res = await axios.get(url);

    const results = res.data.results.slice(0, 5);
    if (results.length === 0) return ctx.reply("❌ لا يوجد نتائج.");

    for (const item of results) {
      const title = item.title || item.name || "عنوان غير متوفر";
      const overview = item.overview ? item.overview.slice(0, 200) + "..." : "لا يوجد وصف.";
      const link = `${shrinkApi}https://www.themoviedb.org/${item.media_type}/${item.id}`;
      await ctx.reply(`🎬 *${title}*\n\n${overview}\n\n🔗 [مشاهدة أو تفاصيل](${link})`, { parse_mode: "Markdown" });
    }
  } catch (err) {
    ctx.reply("⚠️ حصل خطأ في جلب النتائج.");
    console.error(err);
  }
});

bot.launch();
