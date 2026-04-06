/**
 * get-seat-map.mjs — 获取座位图及推荐座位（合并自 recommend-seats.mjs）
 *
 * Input（JSON，通过命令行参数或 stdin 传入）：
 *   seqNo      {string}  [必填] 场次编号（从 get-showtimes 返回的 plist[].seqNo 获取）
 *   authKey    {string}  [必填] 用户认证密钥（ctx.user.authKey）；也可通过环境变量 MAOYAN_TOKEN 传入
 *   ci         {number}  [可选] 城市 ID（ctx.locate.id），默认 1
 *   userid     {string}  [可选] 用户 ID（ctx.user.id）
 *   uuid       {string}  [可选] 设备 UUID（ctx.device.uuid）；也可通过环境变量 MAOYAN_UUID 传入
 *
 * Output（JSON）：
 *   {
 *     cinema   {object}  影院信息：{ cinemaId, cinemaName }
 *     show     {object}  场次信息：{ showDate, showTime, movieName }
 *     buyNumLimit {number} 最多可购票数，默认 4
 *     regions  {Array}   座位区域列表，每项包含：
 *       regionId    {string}   区域 ID
 *       regionName  {string}   区域名称
 *       rowSize     {number}   行数
 *       columnSize  {number}   列数
 *       canSell     {boolean}  是否可售
 *       rows        {Array}    行数据，每行包含：
 *         rowId   {string}  排 ID
 *         rowNum  {number}  排号
 *         seats   {Array}   座位列表，每个座位包含：
 *           seatNo      {string}  座位编号
 *           rowId       {string}  排 ID
 *           columnId    {string}  列 ID
 *           sectionId   {string}  区域 ID
 *           seatType     {string}  类型：N普通/L情侣左/R情侣右/E空位
 *           seatStatus   {number}  状态：0过道或空白区域（不渲染图标，无价格）/1可售/2已锁定/3已售出/4禁售
 *           price        {string}  座位区域单张票价（如 "59.9"），来自 price[sectionId].seatsPrice["1"].totalPrice，兜底 section[sectionId].sectionPrice
 *           sectionName  {string}  座位区域名称（如 "黄金区"），来自 section[sectionId].sectionName
 *     recommendation {object|null} 推荐座位信息（接口返回时存在）：
 *       isShowRecommendation {boolean}  是否显示推荐
 *       bestRecommendation   {object}   最佳推荐组合：
 *         seats   {Array}   推荐座位：[{ rowId, columnId, sectionId, row, column, no }]
 *         remind  {string}  推荐提示文案
 *       bestArea {object}   最佳观影区域四角坐标：
 *         { leftTop, leftBottom, rightTop, rightBottom }（各含 rowNum, colNum）
 *   }
 */
import {
  CHANNEL_ID,
  ERROR_CODES,
  ScriptError,
  readJsonInput,
  requireFields,
  run,
  generateMaoyanHeaders,
  loadSavedToken,
  mapAuthKey,
} from "./_shared.mjs";

const MAOYAN_API_URL = "https://m.maoyan.com/api/mtrade/seat/v8/show/seats.json";

/**
 * 提取单个座位的有用字段
 * @param {object} seat       - 原始座位对象
 * @param {object} sectionMap - section 索引表（key 为 sectionId），来自 data.seat.section
 * @param {object} priceMap   - price 索引表（key 为 sectionId），来自 data.price
 */
function normalizeSeat(seat, sectionMap, priceMap) {
  const sectionId = seat.sectionId == null ? "" : String(seat.sectionId);
  const seatStatus = seat.seatStatus;
  // seatStatus=0 为过道/空白区域，不渲染图标、无价格，直接返回 null
  const isAisle = seatStatus === 0;
  const section = !isAisle ? sectionMap?.[sectionId] : undefined;
  // 按业务逻辑：单张票价取 price[sectionId].seatsPrice["1"].totalPrice，
  // 兜底用 section[sectionId].sectionPrice；过道/空白区域固定为 null
  const sectionPriceFromTable = !isAisle
    ? (priceMap?.[sectionId]?.seatsPrice?.["1"]?.totalPrice ?? null)
    : null;
  return {
    seatNo: seat.seatNo,
    rowId: seat.rowId,
    columnId: seat.columnId,
    sectionId,
    seatType: seat.seatType || "E",
    seatStatus,
    price: sectionPriceFromTable ?? section?.sectionPrice ?? null,
    sectionName: section?.sectionName ?? null,
  };
}

/**
 * seat.section 可能是对象（key 为 sectionId）或数组（每项含 sectionId）
 */
function buildSectionMap(section) {
  if (!section) return {};
  if (!Array.isArray(section)) return section;

  return section.reduce((map, item) => {
    const sectionId = item?.sectionId == null ? "" : String(item.sectionId);
    if (sectionId) map[sectionId] = item;
    return map;
  }, {});
}

/**
 * 提取区域数据
 * @param {object} region     - 原始区域对象
 * @param {object} sectionMap - section 索引表（key 为 sectionId 字符串）
 * @param {object} priceMap   - price 索引表（key 为 sectionId 字符串）
 */
function normalizeRegion(region, sectionMap, priceMap) {
  return {
    regionId: region.regionId,
    regionName: region.regionName,
    rowSize: region.rowSize,
    columnSize: region.columnSize,
    canSell: region.canSell ?? true,
    rows: (region.rows || []).map((row) => ({
      rowId: row.rowId,
      rowNum: row.rowNum,
      seats: (row.seats || []).map((seat) => normalizeSeat(seat, sectionMap, priceMap)),
    })),
  };
}

/**
 * 提取推荐座位数据
 */
function normalizeRecommendation(rec) {
  if (!rec) return null;
  return {
    isShowRecommendation: !!rec.isShowRecommendation,
    bestRecommendation: rec.bestRecommendation
      ? {
          seats: (rec.bestRecommendation.seats || []).map((s) => ({
            rowId: s.rowId,
            columnId: s.columnId,
            sectionId: s.sectionId,
            row: s.row,
            column: s.column,
            no: s.no,
          })),
          remind: rec.bestRecommendation.remind || "",
        }
      : null,
    bestArea: rec.bestArea
      ? {
          leftTop: rec.bestArea.leftTop,
          leftBottom: rec.bestArea.leftBottom,
          rightTop: rec.bestArea.rightTop,
          rightBottom: rec.bestArea.rightBottom,
        }
      : null,
  };
}

await run(async () => {
  const input = mapAuthKey(await readJsonInput());
  requireFields(input, ["seqNo"]);

  const token = loadSavedToken(input.token);
  const cookie = input.cookie || process.env.MAOYAN_COOKIE || "";

  const params = new URLSearchParams({ seqNo: input.seqNo, channelId: CHANNEL_ID });
  if (input.ci != null) params.set("ci", input.ci);
  if (input.userid) params.set("userid", input.userid);
  if (input.deviceInfoByQQ) params.set("deviceInfoByQQ", input.deviceInfoByQQ);

  const url = `${MAOYAN_API_URL}?${params.toString()}`;

  const controller = new AbortController();
  const timer = setTimeout(
    () => controller.abort(),
    Number(process.env.MOVIE_TICKET_TIMEOUT_MS || 10000)
  );

  let res;
  try {
    res = await fetch(url, {
      method: "POST",
      headers: generateMaoyanHeaders({
        token,
        cookie,
        uuid: input.uuid,
        channelId: CHANNEL_ID,
        extraHeaders: { Origin: "https://m.maoyan.com" },
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
  const data = json.data || json;

  const seat = data.seat || {};
  // sectionMap: 来自 data.seat.section，key 为 sectionId，提供区域名称等信息
  const sectionMap = buildSectionMap(seat.section);
  // priceMap: 来自 data.price，key 为 sectionId，按业务逻辑提供各分区的单张票价
  const priceMap = data.price || {};
  const regions = (seat.regions || []).map((region) => normalizeRegion(region, sectionMap, priceMap));

  return {
    cinema: data.cinema
      ? { cinemaId: data.cinema.cinemaId, cinemaName: data.cinema.cinemaName }
      : null,
    show: data.show
      ? {
          showDate: data.show.showDate,
          showTime: data.show.showTime,
          movieName: data.show.movieName,
        }
      : null,
    buyNumLimit: data.buyNumLimit ?? 4,
    regions,
    recommendation: normalizeRecommendation(seat.recommendation ?? data.recommendation),
  };
});
