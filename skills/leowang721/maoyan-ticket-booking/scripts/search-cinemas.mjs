/**
 * search-cinemas.mjs — 按关键词搜索猫眼影院
 *
 * Input（JSON，通过命令行参数或 stdin 传入）：
 *   keyword   {string}  [必填] 搜索关键词，如"万达"
 *   cityId    {number}  [可选] 城市 ID（ctx.locate.id），如北京=1
 *   stype     {number}  [可选] 搜索类型，默认 -1（全部）
 *
 * Output（JSON）：
 *   {
 *     total    {number}  搜索结果总数
 *     cinemas  {Array}   影院列表，每项包含：
 *       cinemaId       {string}   影院 ID
 *       name           {string}   影院名称
 *       addr           {string}   地址
 *       sellPrice      {string}   最低售价，如"55"，无则为空字符串
 *       referencePrice {string}   参考价，无则为空字符串
 *       sell           {boolean}  是否可售票
 *       deal           {boolean}  是否有优惠
 *       hallType       {Array}    特色影厅类型列表，如["IMAX厅","CINITY厅"]
 *       allowRefund    {boolean}  是否支持退票
 *       endorse        {boolean}  是否支持改签
 *       snack          {boolean}  是否支持卖品
 *       vipDesc        {string}   会员描述，无则为空字符串
 *   }
 */
import {
  readJsonInput,
  requireFields,
  run,
  ScriptError,
  ERROR_CODES,
  generateMaoyanHeaders,
  mapAuthKey,
} from "./_shared.mjs";

// 统一搜索接口，同时返回影片和影院，这里只取 cinemas 部分
const MAOYAN_API_URL = "https://m.maoyan.com/apollo/ajax/search";

/**
 * 将搜索结果中每个影院对象提取对 OpenClaw 有用的字段
 */
function normalizeCinema(cinema) {
  return {
    cinemaId: String(cinema.id || ""),
    name: cinema.nm || "",
    addr: cinema.addr || "",
    sellPrice: cinema.sellPrice != null ? String(cinema.sellPrice) : "",
    referencePrice:
      cinema.referencePrice != null ? String(cinema.referencePrice) : "",
    sell: cinema.sell === 1 || cinema.sell === true,
    deal: cinema.deal === 1 || cinema.deal === true,
    // hallType 可能是数组也可能是字符串，统一为数组
    hallType: Array.isArray(cinema.hallType)
      ? cinema.hallType
      : cinema.hallType
        ? [cinema.hallType]
        : [],
    allowRefund: cinema.allowRefund === 1 || cinema.allowRefund === true,
    endorse: cinema.endorse === 1 || cinema.endorse === true,
    snack: cinema.snack === 1 || cinema.snack === true,
    vipDesc: cinema.vipDesc || "",
  };
}

await run(async () => {
  const input = mapAuthKey(await readJsonInput());
  requireFields(input, ["keyword"]);

  const token = input.token || process.env.MAOYAN_TOKEN || "";
  const cookie = input.cookie || process.env.MAOYAN_COOKIE || "";

  const params = new URLSearchParams({ kw: input.keyword });
  if (input.cityId != null) params.set("cityId", input.cityId);
  params.set("stype", input.stype ?? -1);

  const url = `${MAOYAN_API_URL}?${params.toString()}`;

  const controller = new AbortController();
  const timer = setTimeout(
    () => controller.abort(),
    Number(process.env.MOVIE_TICKET_TIMEOUT_MS || 10000)
  );

  let res;
  try {
    res = await fetch(url, {
      method: "GET",
      headers: generateMaoyanHeaders({
        token,
        cookie,
        uuid: input.uuid,
        extraHeaders: { Referer: "https://m.maoyan.com/apollo/search?searchtype=cinema" },
      }),
      signal: controller.signal,
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw new ScriptError(ERROR_CODES.TIMEOUT, "请求超时");
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }

  if (!res.ok) {
    throw new ScriptError(
      ERROR_CODES.HTTP_ERROR,
      `猫眼接口请求失败，状态码 ${res.status}`
    );
  }

  const json = await res.json();
  // 接口同时返回 movies 和 cinemas，取 cinemas 部分
  const cinemasData = json.cinemas || {};
  const rawList = cinemasData.list || [];
  const cinemas = rawList.map(normalizeCinema);

  return {
    total: cinemasData.total ?? cinemas.length,
    cinemas,
  };
});
