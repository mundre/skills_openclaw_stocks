#!/usr/bin/env node

/**
 * 同程程心大模型 - 交通资源智能查询 API
 * 
 * 用法：
 *   node traffic-query.js --departure "北京" --destination "上海"
 *   node traffic-query.js --departure "北京" --destination "上海" --extra "明天"
 *   node traffic-query.js --departure "苏州" --destination "南京" --extra "自驾"
 * 
 * 参数说明：
 *   --departure <城市>        出发地城市
 *   --destination <城市>      目的地城市
 *   --extra <补充信息>        额外信息（日期、偏好等）
 *   --channel <渠道>          通信渠道（webchat/wechat 等）
 *   --surface <界面>          交互界面（mobile/desktop/table/card）
 * 
 * 说明：
 *   本接口用于用户未明确指定交通方式时的智能推荐
 *   会同时返回机票、火车票、汽车票等多种交通方式
 *   调用优先级低于专用查询接口（train-query.js, flight-query.js, bus-query.js）
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
  format_train_table,
  format_train_card,
  format_flight_table,
  format_flight_card,
  format_transfer_trip,
  format_bus_table,
  format_bus_card
} = require('./lib/formatters');

// 交通 API 路径
const TRAFFIC_API_PATH = '/trafficResource';

/**
 * 调用交通资源智能 API
 * @param {object} params - 查询参数
 * @returns {Promise<object>} - API 响应
 */
function query_traffic_api(params) {
  return call_api(TRAFFIC_API_PATH, params);
}

/**
 * 格式化火车结果
 */
function format_train_result(train_data, use_table = false, use_plain_link = false) {
  if (!train_data || !train_data.trainList) {
    return '';
  }
  
  const trains = train_data.trainList;
  const is_transfer = (t) =>
    t.tripType === 'TRANSFER' && t.segmentList && t.segmentList.length > 0;
  const direct_trains = trains.filter((t) => !is_transfer(t));
  const transfer_trains = trains.filter(is_transfer);

  let output = '\n🚄 **火车票**\n\n';

  if (use_table) {
    if (direct_trains.length > 0) {
      output += format_train_table(direct_trains, use_plain_link);
    }
    transfer_trains.forEach((train) => {
      output += format_transfer_trip(train, use_plain_link);
    });
  } else {
    direct_trains.forEach((train) => {
      output += format_train_card(train, use_plain_link);
    });
    transfer_trains.forEach((train) => {
      output += format_transfer_trip(train, use_plain_link);
    });
  }

  return output;
}

/**
 * 格式化机票结果
 */
function format_flight_result(flight_data, use_table = false, use_plain_link = false) {
  if (!flight_data || !flight_data.flightList) {
    return '';
  }
  
  const flights = flight_data.flightList;
  const page_pc_link = flight_data.pageDataList?.[0]?.pcRedirectUrl || '';
  let output = '\n✈️ **机票**\n\n';

  const is_transfer_flight = (f) =>
    f.tripType === 'TRANSFER' && f.segmentList && f.segmentList.length > 0;
  
  if (use_table) {
    const direct_flights = flights.filter((f) => !is_transfer_flight(f));
    const transfer_flights = flights.filter(is_transfer_flight);
    if (direct_flights.length > 0) {
      output += format_flight_table(direct_flights, use_plain_link, page_pc_link);
    }
    transfer_flights.forEach((flight) => {
      output += format_transfer_trip(flight, use_plain_link);
    });
  } else {
    flights.forEach((flight) => {
      if (is_transfer_flight(flight)) {
        output += format_transfer_trip(flight, use_plain_link);
      } else {
        output += format_flight_card(flight, use_plain_link, page_pc_link);
      }
    });
  }
  
  return output;
}

/**
 * 格式化汽车票结果
 */
function format_bus_result(bus_data, use_table = false, use_plain_link = false) {
  if (!bus_data || !bus_data.pageDataList) {
    return '';
  }
  
  const buses = bus_data.pageDataList;
  let output = '\n🚌 **汽车票**\n\n';
  
  if (use_table) {
    output += format_bus_table(buses, use_plain_link);
  } else {
    buses.forEach((bus) => {
      output += format_bus_card(bus, use_plain_link);
    });
  }
  
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
  if (params.departure && params.destination) {
    return { valid: true };
  }
  
  return { 
    valid: false, 
    error: `⚠️ 参数不完整，请提供出发地和目的地。
  示例：--departure "北京" --destination "上海"`
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
    console.log('  node traffic-query.js --departure "北京" --destination "上海"');
    console.log('  node traffic-query.js --departure "北京" --destination "上海" --extra "明天"');
    console.log('\n参数说明：');
    console.log('  --departure <城市>        出发地城市');
    console.log('  --destination <城市>      目的地城市');
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
  if (params.extra) request_params.extra = params.extra;
  if (params.channel) request_params.channel = params.channel;
  if (params.surface) request_params.surface = params.surface;
  
  const { use_table, use_plain_link } = resolve_output_mode(params);

  try {
    const result = await query_traffic_api(request_params);

    handle_api_result(result, {
      no_match_detail: NO_MATCH_DETAIL.traffic,
      on_success: (res) => {
        const print_success_once = create_success_banner_once();
        const response_data = res.data?.data || res.data;

        const train_data_list = response_data?.trainDataList;
        const flight_data_list = response_data?.flightDataList;
        const bus_data_list = response_data?.busDataList;

        let has_output = false;

        if (Array.isArray(train_data_list) && train_data_list.length > 0 && train_data_list[0].trainList) {
          print_success_once();
          train_data_list.forEach((item, index) => {
            if (item.desc && train_data_list.length > 1) {
              console.log(`📌 ${item.desc}\n`);
            }
            if (item.trainList && item.trainList.length > 0) {
              console.log(format_train_result(item, use_table, use_plain_link));
              has_output = true;
            }
          });
        }

        if (Array.isArray(flight_data_list) && flight_data_list.length > 0 && flight_data_list[0].flightList) {
          print_success_once();
          flight_data_list.forEach((item, index) => {
            if (item.desc && flight_data_list.length > 1) {
              console.log(`📌 ${item.desc}\n`);
            }
            if (item.flightList && item.flightList.length > 0) {
              console.log(format_flight_result(item, use_table, use_plain_link));
              has_output = true;
            }
          });
        }

        if (Array.isArray(bus_data_list) && bus_data_list.length > 0 && bus_data_list[0].pageDataList) {
          print_success_once();
          bus_data_list.forEach((item, index) => {
            if (item.desc && bus_data_list.length > 1) {
              console.log(`📌 ${item.desc}\n`);
            }
            if (item.pageDataList && item.pageDataList.length > 0) {
              console.log(format_bus_result(item, use_table, use_plain_link));
              has_output = true;
            }
          });
        }

        if (!has_output) {
          print_no_match_lines(NO_MATCH_DETAIL.traffic);
        } else {
          console.log('💡 **更多选择**：也可以打开 **同程旅行 APP** 或在 **微信 - 我 - 服务** 中，点击 **火车票机票** 查看更丰富的资源。\n');
        }
      }
    });
  } catch (error) {
    print_request_exception(error);
  }
}

// 导出函数供其他模块使用
module.exports = {
  query_traffic_api,
  validate_params
};

// 运行主函数
if (require.main === module) {
  main();
}
