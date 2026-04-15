#!/usr/bin/env node

/**
 * 同程程心大模型 - 酒店专用查询 API
 * 
 * 用法：
 *   node hotel-query.js --destination "上海"
 *   node hotel-query.js --destination "上海" --extra "明天入住"
 *   node hotel-query.js --destination "上海" --extra "外滩附近 明天入住"
 * 
 * 参数说明：
 *   --destination <城市>      目的地城市
 *   --extra <补充信息>        额外信息（日期、位置偏好等）
 *   --channel <渠道>          通信渠道（webchat/wechat 等）
 *   --surface <界面>          交互界面（mobile/desktop/table/card）
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
const { format_hotel_card, format_hotel_table } = require('./lib/formatters');

// 酒店 API 路径
const HOTEL_API_PATH = '/hotelResource';

/**
 * 调用酒店专用 API
 * @param {object} params - 查询参数
 * @returns {Promise<object>} - API 响应
 */
function query_hotel_api(params) {
  return call_api(HOTEL_API_PATH, params);
}

/**
 * 格式化酒店结果
 * @param {object} hotel_data - 酒店数据
 * @param {boolean} use_table - 是否使用表格格式
 * @param {boolean} use_plain_link - 是否使用纯文本链接
 * @returns {string} - 格式化输出
 */
function format_hotel_result(hotel_data, use_table = false, use_plain_link = false) {
  if (!hotel_data || !hotel_data.hotelList) {
    return '未找到相关酒店信息';
  }
  
  const hotels = hotel_data.hotelList;
  let output = '🏨 酒店查询结果：\n\n';
  
  if (use_table) {
    // 表格格式
    output += format_hotel_table(hotels, use_plain_link);
  } else {
    // 卡片格式
    hotels.forEach((hotel) => {
      output += format_hotel_card(hotel, use_plain_link);
    });
  }
  
  output += '💡 **更多选择**：也可以打开 **同程旅行 APP** 或在 **微信 - 我 - 服务** 中，点击 **酒店民宿** 查看更丰富的资源。\n';
  output += '\n';
  return output;
}

/**
 * 解析命令行参数
 * @returns {object} - 解析后的参数对象
 */
function parse_args() {
  const args = process.argv.slice(2);
  const params = {
    destination: '',
    extra: '',
    channel: '',
    surface: ''
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--destination' && args[i + 1]) {
      params.destination = args[++i];
    } else if (arg === '--extra' && args[i + 1]) {
      params.extra = args[++i];
    } else if (arg === '--channel' && args[i + 1]) {
      params.channel = args[++i];
    } else if (arg === '--surface' && args[i + 1]) {
      params.surface = args[++i];
    } else if (!arg.startsWith('--') && !params.destination) {
      // 支持简写：第一个非选项参数作为目的地
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
    error: `⚠️ 参数不完整，请提供目的地城市。
  示例：--destination "上海"`
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
    console.log('  node hotel-query.js --destination "上海"');
    console.log('  node hotel-query.js --destination "上海" --extra "明天入住"');
    console.log('  node hotel-query.js --destination "上海" --extra "外滩附近 明天入住"');
    console.log('\n参数说明：');
    console.log('  --destination <城市>      目的地城市');
    console.log('  --extra <补充信息>        额外信息（日期、位置偏好等）');
    console.log('  --channel <渠道>          通信渠道（webchat/wechat 等）');
    console.log('  --surface <界面>          交互界面（mobile/desktop/table/card）');
    console.log('\n' + validation.error);
    process.exit(1);
  }
  
  // 构建请求参数（只包含非空字段）
  const request_params = {};
  if (params.destination) request_params.destination = params.destination;
  if (params.extra) request_params.extra = params.extra;
  if (params.channel) request_params.channel = params.channel;
  if (params.surface) request_params.surface = params.surface;
  
  // 检测输出格式
  const { use_table, use_plain_link } = resolve_output_mode(params);

  try {
    const result = await query_hotel_api(request_params);

    handle_api_result(result, {
      no_match_detail: NO_MATCH_DETAIL.hotel,
      on_success: (res) => {
        const print_success_once = create_success_banner_once();
        const response_data = res.data?.data || res.data;

        const hotel_data_list = response_data?.hotelDataList;

        if (Array.isArray(hotel_data_list) && hotel_data_list.length > 0) {
          let has_output = false;
          hotel_data_list.forEach((item, index) => {
            if (item.hotelList && item.hotelList.length > 0) {
              print_success_once();
              if (item.desc) {
                console.log(`📌 ${item.desc}\n`);
              } else if (hotel_data_list.length > 1) {
                console.log(`📌 列表 ${index + 1}\n`);
              }
              console.log(format_hotel_result(item, use_table, use_plain_link));
              has_output = true;
            }
          });
          if (!has_output) {
            print_no_match_lines(NO_MATCH_DETAIL.hotel);
          }
        } else {
          print_no_match_lines(NO_MATCH_DETAIL.hotel);
        }
      }
    });
  } catch (error) {
    print_request_exception(error);
  }
}

// 导出函数供其他模块使用
module.exports = {
  query_hotel_api,
  validate_params,
  format_hotel_result
};

// 运行主函数
if (require.main === module) {
  main();
}
