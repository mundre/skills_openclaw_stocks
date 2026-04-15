#!/usr/bin/env node

/**
 * 同程程心大模型 - 旅行资源专用查询 API
 * 
 * 用法：
 *   node travel-query.js --destination "三亚"
 *   node travel-query.js --destination "三亚" --extra "五一假期"
 *   node travel-query.js --destination "云南" --extra "6天5晚 自由行"
 * 
 * 参数说明：
 *   --destination <城市/地区>  目的地城市或地区
 *   --extra <补充信息>        额外信息（假期、天数、类型等）
 *   --channel <渠道>          通信渠道（webchat/wechat 等）
 *   --surface <界面>          交互界面（mobile/desktop/table/card）
 * 
 * 说明：
 *   本接口用于查询自由行、跟团游等度假产品
 *   作为用户有明确旅游意向时的补充推荐
 *   如果有合适的单品资源（机票、酒店），应提供更多选择
 * 
 * 配置（优先级：环境变量 > config.json）：
 *   - CHENGXIN_API_KEY（环境变量）
 *   - 或创建 config.json 文件（见 config.example.json）
 */

const { call_api } = require('./lib/api-client');
const { resolve_output_mode } = require('./lib/output-mode');
const {
  NO_MATCH_DETAIL,
  create_success_banner_once,
  handle_api_result,
  print_no_match_lines,
  print_request_exception
} = require('./lib/query-response');
const {
  format_trip_card,
  format_trip_table,
  format_trip_plans,
  format_train_table,
  format_hotel_table,
  format_scenery_table,
  render_booking_buttons
} = require('./lib/formatters');

// 度假产品 API 路径
const TRAVEL_API_PATH = '/travelResource';

/**
 * 调用旅行资源专用 API
 * @param {object} params - 查询参数
 * @returns {Promise<object>} - API 响应
 */
function query_travel_api(params) {
  return call_api(TRAVEL_API_PATH, params);
}

/**
 * 格式化旅行产品结果
 * @param {object} trip_data - 旅行产品数据
 * @param {boolean} use_table - 是否使用表格格式
 * @param {boolean} use_plain_link - 是否使用纯文本链接
 * @returns {string} - 格式化输出
 */
function format_travel_result(trip_data, use_table = false, use_plain_link = false) {
  if (!trip_data || !trip_data.tripList) {
    return '';
  }
  
  const trips = trip_data.tripList.slice(0, 10);
  let output = '🧳 **度假产品**\n\n';
  
  if (use_table) {
    output += format_trip_table(trips, use_plain_link);
  } else {
    // 卡片格式
    trips.forEach((trip) => {
      output += format_trip_card(trip, use_plain_link);
    });
  }
  
  return output;
}

/**
 * 格式化火车票结果
 * @param {Array} train_data_list - 火车票数据列表
 * @param {boolean} use_table - 是否使用表格格式
 * @param {boolean} use_plain_link - 是否使用纯文本链接
 * @returns {string} - 格式化输出
 */
function format_train_result(train_data_list, use_table = false, use_plain_link = false) {
  if (!train_data_list || train_data_list.length === 0) {
    return '';
  }

  let output = '🚄 **推荐火车/高铁**\n\n';

  train_data_list.forEach((item) => {
    if (item.desc) {
      output += `📌 ${item.desc}\n`;
    }
    if (item.trainList && item.trainList.length > 0) {
      output += format_train_table(item.trainList.slice(0, 5), use_plain_link);
      output += '\n';
    }
  });

  return output;
}

/**
 * 格式化酒店结果
 * @param {Array} hotel_data_list - 酒店数据列表
 * @param {boolean} use_table - 是否使用表格格式
 * @param {boolean} use_plain_link - 是否使用纯文本链接
 * @returns {string} - 格式化输出
 */
function format_hotel_result(hotel_data_list, use_table = false, use_plain_link = false) {
  if (!hotel_data_list || hotel_data_list.length === 0) {
    return '';
  }

  let output = '🏨 **推荐酒店**\n\n';

  hotel_data_list.forEach((item) => {
    if (item.hotelList && item.hotelList.length > 0) {
      output += format_hotel_table(item.hotelList.slice(0, 10), use_plain_link);
      output += '\n';
    }
  });

  return output;
}

/**
 * 格式化景区列表
 * @param {Array} scenery_data_list - 景区数据列表
 * @param {boolean} use_table - 是否使用表格格式
 * @param {boolean} use_plain_link - 是否使用纯文本链接
 * @returns {string} - 格式化输出
 */
function format_scenery_result(scenery_data_list, use_table = false, use_plain_link = false) {
  if (!scenery_data_list || scenery_data_list.length === 0) {
    return '';
  }

  let output = '🏞️ **推荐景区/景点**\n\n';

  scenery_data_list.forEach((item) => {
    if (item.sceneryList && item.sceneryList.length > 0) {
      if (use_table) {
        output += format_scenery_table(item.sceneryList.slice(0, 10), use_plain_link);
      } else {
        // 卡片格式
        item.sceneryList.slice(0, 10).forEach((scenery) => {
          const name = scenery.name || '未知景区';
          const city = scenery.cityName || '';
          const price = scenery.price ? `¥${scenery.price}` : '暂无价格';
          const star = scenery.star || '';
          const score = scenery.score ? `⭐${scenery.score}` : '';
          const intro = scenery.describe || '';
          const pc_link = scenery.pcRedirectUrl || '';
          const mobile_link = scenery.clawRedirectUrl || scenery.redirectUrl || '';

          output += `### 🏞️ ${name}\n`;
          if (city || star) output += `📍 ${city} | ${star}\n`;
          if (price || score) output += `💰 ${price} | ${score}\n`;
          if (intro) output += `${intro}\n`;
          const booking_line = render_booking_buttons(pc_link, mobile_link, use_plain_link);
          if (booking_line) output += `🔗 预订：${booking_line}\n`;
          output += '\n---\n\n';
        });
      }
      output += '\n';
    }
  });

  return output;
}

/**
 * 格式化 UGC 攻略指引
 * @param {Array} ugc_data_list - UGC 数据列表
 * @returns {string} - 格式化输出
 */
function format_ugc_guide(ugc_data_list) {
  if (!ugc_data_list || ugc_data_list.length === 0) {
    return '';
  }

  let output = '📝 **用户攻略推荐**\n\n';
  output += `共找到 ${ugc_data_list.length} 篇用户攻略，以下是部分推荐：\n\n`;

  ugc_data_list.slice(0, 3).forEach((item, idx) => {
    if (item.ugcList && item.ugcList.length > 0) {
      const ugc = item.ugcList[0];
      const name = ugc.name || '无标题';
      const author = ugc.nickName || '匿名用户';
      const redirect_url = ugc.redirectUrl || '#';
      
      output += `${idx + 1}. **${name}** - ${author}\n`;
      output += `   🔗 [查看全文](${redirect_url})\n\n`;
    }
  });

  output += '💡 以上攻略由真实用户分享，可供参考。\n\n';

  return output;
}

/**
 * 解析命令行参数
 * @returns {object} - 解析后的参数对象
 */
function parse_args() {
  const args = process.argv.slice(2);
  const params = {
    departure: '',
    destination: '',
    extra: '',
    channel: '',
    surface: ''
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--departure' && args[i + 1]) {
      params.departure = args[++i];
    } else if (arg === '--destination' && args[i + 1]) {
      params.destination = args[++i];
    } else if (arg === '--extra' && args[i + 1]) {
      params.extra = args[++i];
    } else if (arg === '--channel' && args[i + 1]) {
      params.channel = args[++i];
    } else if (arg === '--surface' && args[i + 1]) {
      params.surface = args[++i];
    } else if (!arg.startsWith('--') && !params.destination) {
      params.destination = arg;
    }
  }
  
  return params;
}

/**
 * 验证参数组合
 * @param {object} params - 参数对象
 * @returns {object} - { valid: boolean, error: string }
 */
function validate_params(params) {
  if (params.destination) {
    return { valid: true };
  }
  
  return { 
    valid: false, 
    error: `⚠️ 参数不完整，请提供目的地城市或地区。
  示例：--destination "三亚"`
  };
}

/**
 * 主函数
 */
async function main() {
  const params = parse_args();
  
  // 验证参数
  const validation = validate_params(params);
  if (!validation.valid) {
    console.log('用法：');
    console.log('  node travel-query.js --destination "三亚"');
    console.log('  node travel-query.js --departure "北京" --destination "三亚"');
    console.log('  node travel-query.js --departure "北京" --destination "三亚" --extra "五一假期"');
    console.log('\n参数说明：');
    console.log('  --departure <城市>          出发地城市（可选）');
    console.log('  --destination <城市/地区>   目的地城市或地区（必填）');
    console.log('  --extra <补充信息>          额外信息（假期、天数、类型等）');
    console.log('  --channel <渠道>            通信渠道（webchat/wechat 等）');
    console.log('  --surface <界面>            交互界面（mobile/desktop/table/card）');
    console.log('\n' + validation.error);
    process.exit(1);
  }
  
  // 构建请求参数（只包含非空字段）
  const request_params = {};
  if (params.departure) request_params.departure = params.departure;
  if (params.destination) request_params.destination = params.destination;
  if (params.extra) request_params.extra = params.extra;
  if (params.channel) request_params.channel = params.channel;
  if (params.surface) request_params.surface = params.surface;
  
  // 检测输出格式
  const { use_table, use_plain_link } = resolve_output_mode(params);

  try {
    const result = await query_travel_api(request_params);

    handle_api_result(result, {
      no_match_detail: NO_MATCH_DETAIL.travel,
      on_success: (res) => {
        const print_success_once = create_success_banner_once();
        const response_data = res.data?.data || res.data;

        let has_output = false;
        let output_parts = [];

        // 1. 火车票推荐（往返交通）
        const train_data_list = response_data?.trainDataList;
        if (Array.isArray(train_data_list) && train_data_list.length > 0) {
          const train_output = format_train_result(train_data_list, use_table, use_plain_link);
          if (train_output) {
            print_success_once();
            output_parts.push(train_output);
            has_output = true;
          }
        }

        // 2. 酒店推荐
        const hotel_data_list = response_data?.hotelDataList;
        if (Array.isArray(hotel_data_list) && hotel_data_list.length > 0) {
          const hotel_output = format_hotel_result(hotel_data_list, use_table, use_plain_link);
          if (hotel_output) {
            print_success_once();
            output_parts.push(hotel_output);
            has_output = true;
          }
        }

        // 2.5. 景区推荐（丰富行程规划）
        const scenery_data_list = response_data?.sceneryDataList;
        if (Array.isArray(scenery_data_list) && scenery_data_list.length > 0) {
          const scenery_output = format_scenery_result(scenery_data_list, use_table, use_plain_link);
          if (scenery_output) {
            print_success_once();
            output_parts.push(scenery_output);
            has_output = true;
          }
        }

        // 3. 传统打包产品（跟团游等）
        const trip_data_list = response_data?.tripDataList;
        if (Array.isArray(trip_data_list) && trip_data_list.length > 0) {
          trip_data_list.forEach((item, index) => {
            if (item.tripList && item.tripList.length > 0) {
              print_success_once();
              let part_output = '';
              if (item.desc) {
                part_output += `📌 ${item.desc}\n`;
              } else if (trip_data_list.length > 1) {
                part_output += `📌 列表 ${index + 1}\n`;
              }
              part_output += format_travel_result(item, use_table, use_plain_link);
              output_parts.push(part_output);
              has_output = true;
            }
          });
        }

        // 4. 行程规划（核心）
        const trip_plan_data_list = response_data?.tripPlanDataList;
        if (Array.isArray(trip_plan_data_list) && trip_plan_data_list.length > 0) {
          const plan_output = format_trip_plans(trip_plan_data_list, use_plain_link);
          if (plan_output) {
            print_success_once();
            output_parts.push(plan_output);
            has_output = true;
          }
        }

        // 5. UGC 攻略指引
        const ugc_data_list = response_data?.ugcDataList;
        if (Array.isArray(ugc_data_list) && ugc_data_list.length > 0) {
          const ugc_output = format_ugc_guide(ugc_data_list);
          if (ugc_output) {
            output_parts.push(ugc_output);
          }
        }

        // 输出所有内容
        if (has_output) {
          output_parts.forEach((part) => {
            console.log(part);
          });
          console.log('💡 **更多选择**：也可以打开 **同程旅行 APP** 或在 **微信 - 我 - 服务** 中，点击 **火车票机票** 以及 **酒店民宿** 查看更丰富的资源。\n');
        } else {
          print_no_match_lines(NO_MATCH_DETAIL.travel);
        }
      }
    });
  } catch (error) {
    print_request_exception(error);
  }
}

// 导出函数供其他模块使用
module.exports = {
  query_travel_api,
  validate_params,
  format_travel_result
};

// 运行主函数
if (require.main === module) {
  main();
}
