#!/usr/bin/env node

/**
 * 同程程心大模型 - 火车票专用查询 API
 * 
 * 用法：
 *   node train-query.js --departure "北京" --destination "上海"
 *   node train-query.js --train-number "G1234"
 *   node train-query.js --departure-station "北京南站" --arrival-station "上海虹桥站"
 *   node train-query.js --departure "北京" --destination "上海" --extra "明天 高铁"
 * 
 * 参数说明：
 *   --departure <城市>        出发地城市
 *   --destination <城市>      目的地城市
 *   --departure-station <站>  出发站
 *   --arrival-station <站>    到达站
 *   --train-number <车次>     车次号
 *   --extra <补充信息>        额外信息（日期、偏好等）
 *   --channel <渠道>          通信渠道（webchat/wechat 等）
 *   --surface <界面>          交互界面（mobile/desktop/table/card）
 * 
 * 合法组合：
 *   1. 出发地 + 目的地
 *   2. 车次号
 *   3. 出发站 + 到达站
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
const { format_train_table, format_transfer_trip, format_train_card } = require('./lib/formatters');

// 火车票 API 路径
const TRAIN_API_PATH = '/trainResource';

/**
 * 调用火车票专用 API
 * @param {object} params - 查询参数
 * @returns {Promise<object>} - API 响应
 */
function query_train_api(params) {
  return call_api(TRAIN_API_PATH, params);
}

/**
 * 格式化火车票结果
 * @param {object} train_data - 火车数据
 * @param {boolean} use_table - 是否使用表格格式
 * @param {boolean} use_plain_link - 是否使用纯文本链接
 * @returns {string} - 格式化输出
 */
function format_train_result(train_data, use_table = false, use_plain_link = false) {
  if (!train_data || !train_data.trainList) {
    return '未找到相关火车票信息';
  }
  
  const trains = train_data.trainList;
  let output = '🚄 火车票查询结果：\n\n';
  
  // 分离直达车次和中转联程
  const direct_trains = trains.filter(t => !(t.tripType === 'TRANSFER' && t.segmentList && t.segmentList.length > 0));
  const transfer_trains = trains.filter(t => t.tripType === 'TRANSFER' && t.segmentList && t.segmentList.length > 0);
  
  if (use_table) {
    // 表格格式
    if (direct_trains.length > 0) {
      output += format_train_table(direct_trains, use_plain_link) + '\n';
    }
    
    // 中转联程每个方案单独一个小表格
    if (transfer_trains.length > 0) {
      transfer_trains.forEach((train) => {
        output += format_transfer_trip(train, use_plain_link);
      });
    }
  } else {
    // 卡片格式
    direct_trains.forEach((train) => {
      output += format_train_card(train, use_plain_link);
    });
    
    // 中转联程也用卡片格式
    if (transfer_trains.length > 0) {
      transfer_trains.forEach((train) => {
        output += format_transfer_trip(train, use_plain_link);
      });
    }
  }
  
  // 如果没有直达也没有联程
  if (direct_trains.length === 0 && transfer_trains.length === 0) {
    output += '⚠️ 未找到符合条件的火车票，请尝试调整查询条件。\n';
  }
  
  output += '💡 **更多选择**：也可以打开 **同程旅行 APP** 或在 **微信 - 我 - 服务** 中，点击 **火车票机票** 查看更丰富的资源。\n';
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
    departure: '',
    destination: '',
    departureStation: '',
    arrivalStation: '',
    trainNumber: '',
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
    } else if (arg === '--departure-station' && args[i + 1]) {
      params.departureStation = args[++i];
    } else if (arg === '--arrival-station' && args[i + 1]) {
      params.arrivalStation = args[++i];
    } else if (arg === '--train-number' && args[i + 1]) {
      params.trainNumber = args[++i];
    } else if (arg === '--extra' && args[i + 1]) {
      params.extra = args[++i];
    } else if (arg === '--channel' && args[i + 1]) {
      params.channel = args[++i];
    } else if (arg === '--surface' && args[i + 1]) {
      params.surface = args[++i];
    } else if (!arg.startsWith('--') && !params.departure) {
      // 支持简写：第一个非选项参数作为查询文本
      params.query = arg;
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
  const has_departure_dest = params.departure && params.destination;
  const has_train_number = params.trainNumber;
  const has_stations = params.departureStation && params.arrivalStation;
  
  if (has_departure_dest || has_train_number || has_stations) {
    return { valid: true };
  }
  
  // 检查部分参数
  const has_partial = params.departure || params.destination || 
                      params.departureStation || params.arrivalStation;
  
  if (has_partial) {
    let error = '⚠️ 参数不完整，请提供以下组合之一：\n';
    error += '  1. 出发地 + 目的地（--departure "北京" --destination "上海"）\n';
    error += '  2. 车次号（--train-number "G1234"）\n';
    error += '  3. 出发站 + 到达站（--departure-station "北京南站" --arrival-station "上海虹桥站"）';
    return { valid: false, error };
  }
  
  return { valid: false, error: '请提供查询参数' };
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
    console.log('  node train-query.js --departure "北京" --destination "上海"');
    console.log('  node train-query.js --train-number "G1234"');
    console.log('  node train-query.js --departure-station "北京南站" --arrival-station "上海虹桥站"');
    console.log('  node train-query.js --departure "北京" --destination "上海" --extra "明天 高铁"');
    console.log('\n参数说明：');
    console.log('  --departure <城市>        出发地城市');
    console.log('  --destination <城市>      目的地城市');
    console.log('  --departure-station <站>  出发站');
    console.log('  --arrival-station <站>    到达站');
    console.log('  --train-number <车次>     车次号');
    console.log('  --extra <补充信息>        额外信息（日期、偏好等）');
    console.log('  --channel <渠道>          通信渠道（webchat/wechat 等）');
    console.log('  --surface <界面>          交互界面（mobile/desktop/table/card）');
    console.log('\n' + validation.error);
    process.exit(1);
  }
  
  // 构建请求参数（只包含非空字段）
  const request_params = {};
  if (params.departure) request_params.departure = params.departure;
  if (params.destination) request_params.destination = params.destination;
  if (params.departureStation) request_params.departureStation = params.departureStation;
  if (params.arrivalStation) request_params.arrivalStation = params.arrivalStation;
  if (params.trainNumber) request_params.trainNumber = params.trainNumber;
  if (params.extra) request_params.extra = params.extra;
  if (params.channel) request_params.channel = params.channel;
  if (params.surface) request_params.surface = params.surface;
  
  const { use_table, use_plain_link } = resolve_output_mode(params);
  
  try {
    const result = await query_train_api(request_params);

    handle_api_result(result, {
      no_match_detail: NO_MATCH_DETAIL.train,
      on_success: (res) => {
        const print_success_once = create_success_banner_once();
        const response_data = res.data?.data || res.data;

        const train_data_list = response_data?.trainDataList;

        if (Array.isArray(train_data_list) && train_data_list.length > 0) {
          let has_output = false;
          train_data_list.forEach((item, index) => {
            if (item.trainList && item.trainList.length > 0) {
              print_success_once();
              if (item.desc) {
                console.log(`📌 ${item.desc}\n`);
              } else if (train_data_list.length > 1) {
                console.log(`📌 列表 ${index + 1}\n`);
              }
              console.log(format_train_result(item, use_table, use_plain_link));
              has_output = true;
            }
          });
          if (!has_output) {
            print_no_match_lines(NO_MATCH_DETAIL.train);
          }
        } else {
          print_no_match_lines(NO_MATCH_DETAIL.train);
        }
      }
    });
  } catch (error) {
    print_request_exception(error);
  }
}

// 导出函数供其他模块使用
module.exports = {
  query_train_api,
  validate_params,
  format_train_result
};

// 运行主函数
if (require.main === module) {
  main();
}
