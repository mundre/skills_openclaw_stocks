const fs = require('fs');
const path = require('path');

// 加载门店和服务数据
const storeData = JSON.parse(fs.readFileSync(path.join(__dirname, 'org_store.json'), 'utf8'));
const serviceData = JSON.parse(fs.readFileSync(path.join(__dirname, 'prod_service.json'), 'utf8'));

/**
 * 智能匹配函数
 * @param input 用户输入
 * @param options 可选值列表
 * @returns 匹配结果
 */
function smartMatch(input, options) {
  const normalizedInput = input.toLowerCase().trim();
  const matches = options.filter(option => 
    option.toLowerCase().includes(normalizedInput)
  );
  
  if (matches.length === 1) {
    return { matched: true, exactMatch: matches[0] };
  } else if (matches.length > 1) {
    return { matched: false, candidates: matches };
  } else {
    return { matched: false, candidates: [] };
  }
}

/**
 * 验证手机号
 * @param mobile 手机号
 * @returns 验证结果
 */
function validatePhone(mobile) {
  const phoneRegex = /^1[3-9]\d{9}$/;
  if (!phoneRegex.test(mobile)) {
    return { valid: false, message: '请输入正确的11位中国大陆手机号' };
  }
  return { valid: true };
}

/**
 * 验证人数
 * @param count 人数
 * @returns 验证结果
 */
function validatePeopleCount(count) {
  if (typeof count !== 'number' || count < 1 || count > 20) {
    return { valid: false, message: '预约人数必须在1-20人之间' };
  }
  return { valid: true };
}

/**
 * 验证预约时间
 * @param bookTime 预约时间
 * @returns 验证结果
 */
function validateBookingTime(bookTime) {
  const timeRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/;
  if (!timeRegex.test(bookTime)) {
    return { valid: false, message: '预约时间格式不正确，请使用ISO 8601格式（如：2024-01-15T14:00:00）' };
  }
  
  const bookingDate = new Date(bookTime);
  const now = new Date();
  if (bookingDate <= now) {
    return { valid: false, message: '预约时间必须晚于当前时间' };
  }
  
  return { valid: true };
}

/**
 * 验证必填字符串
 * @param value 值
 * @param field 字段名
 * @returns 验证结果
 */
function validateRequiredString(value, field) {
  if (!value || typeof value !== 'string' || value.trim() === '') {
    return { valid: false, message: `${field}不能为空` };
  }
  return { valid: true };
}

/**
 * 调用后端API创建预约
 * @param params 预约参数
 * @returns API响应结果
 */
async function callCreateBookingAPI(params) {
  try {
    const response = await fetch('https://open.lannlife.com/mcp/book/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        mobile: params.mobile,
        storeName: params.storeName,
        serviceName: params.serviceName,
        count: params.count,
        bookTime: params.bookTime
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP 错误：${response.status}`);
    }

    const result = await response.json();

    if (result.code === '200' || result.code === '0') {
      return {
        success: true,
        bookingId: result.body?.bookId,
        message: result.msg || '预约成功！',
        startTime: result.body?.startTime,
        endTime: result.body?.endTime
      };
    } else {
      return {
        success: false,
        message: result.msg || '预约失败'
      };
    }
  } catch (error) {
    console.error('调用预约 API 失败:', error);
    return {
      success: false,
      message: error instanceof Error ? error.message : '预约失败，请稍后重试'
    };
  }
}

/**
 * 意图识别
 * @param userInput 用户输入
 * @returns 意图和实体
 */
function recognizeIntent(userInput) {
  const normalizedInput = userInput.toLowerCase().trim();
  
  // 门店查询意图
  if (normalizedInput.includes('门店') || normalizedInput.includes('地址') || normalizedInput.includes('哪里')) {
    return {
      intent: 'store_query',
      entities: {
        keyword: normalizedInput
      }
    };
  }
  
  // 服务查询意图
  if (normalizedInput.includes('服务') || normalizedInput.includes('项目') || normalizedInput.includes('按摩')) {
    return {
      intent: 'service_query',
      entities: {
        keyword: normalizedInput
      }
    };
  }
  
  // 创建预约意图
  if (normalizedInput.includes('预约') || normalizedInput.includes('预定') || normalizedInput.includes('book')) {
    // 提取实体
    const entities = extractBookingEntities(normalizedInput);
    return {
      intent: 'create_booking',
      entities
    };
  }
  
  // 默认意图
  return {
    intent: 'unknown',
    entities: {}
  };
}

/**
 * 提取预约实体
 * @param userInput 用户输入
 * @returns 提取的实体
 */
function extractBookingEntities(userInput) {
  const entities = {};
  
  // 提取手机号
  const phoneRegex = /1[3-9]\d{9}/;
  const phoneMatch = userInput.match(phoneRegex);
  if (phoneMatch) {
    entities.mobile = phoneMatch[0];
  }
  
  // 提取门店名称
  const storeNames = storeData.map(store => store.name);
  for (const storeName of storeNames) {
    if (userInput.includes(storeName)) {
      entities.storeName = storeName;
      break;
    }
  }
  
  // 提取服务名称
  const serviceNames = serviceData.map(service => service.name);
  for (const serviceName of serviceNames) {
    if (userInput.includes(serviceName)) {
      entities.serviceName = serviceName;
      break;
    }
  }
  
  // 提取人数
  const countRegex = /(\d+)人/;
  const countMatch = userInput.match(countRegex);
  if (countMatch) {
    entities.count = parseInt(countMatch[1]);
  }
  
  // 提取时间（简单处理，实际项目中可能需要更复杂的时间解析）
  // 这里暂时返回空，需要用户提供具体的ISO格式时间
  
  return entities;
}

/**
 * 查询门店
 * @param keyword 关键词
 * @returns 门店列表
 */
function queryStores(keyword) {
  if (!keyword) {
    return storeData;
  }
  
  const normalizedKeyword = keyword.toLowerCase();
  return storeData.filter(store => 
    store.name.toLowerCase().includes(normalizedKeyword) ||
    (store.ADDRESS && store.ADDRESS.toLowerCase().includes(normalizedKeyword))
  );
}

/**
 * 查询服务
 * @param keyword 关键词
 * @returns 服务列表
 */
function queryServices(keyword) {
  if (!keyword) {
    return serviceData;
  }
  
  const normalizedKeyword = keyword.toLowerCase();
  return serviceData.filter(service => 
    service.name.toLowerCase().includes(normalizedKeyword) ||
    (service.desc && service.desc.toLowerCase().includes(normalizedKeyword))
  );
}

/**
 * 创建预约
 * @param params 预约参数
 * @returns 预约结果
 */
async function createBooking(params) {
  // 1. 验证必填参数
  const mobileValidation = validateRequiredString(params.mobile, '手机号');
  if (!mobileValidation.valid) {
    return { success: false, message: mobileValidation.message };
  }

  const storeNameValidation = validateRequiredString(params.storeName, '门店名称');
  if (!storeNameValidation.valid) {
    return { success: false, message: storeNameValidation.message };
  }

  const serviceNameValidation = validateRequiredString(params.serviceName, '服务项目');
  if (!serviceNameValidation.valid) {
    return { success: false, message: serviceNameValidation.message };
  }

  // 2. 验证手机号格式
  const phoneValid = validatePhone(params.mobile);
  if (!phoneValid.valid) {
    return { success: false, message: phoneValid.message };
  }

  // 3. 验证人数
  const peopleValid = validatePeopleCount(params.count);
  if (!peopleValid.valid) {
    return { success: false, message: peopleValid.message };
  }

  // 4. 验证预约时间
  const timeValid = validateBookingTime(params.bookTime);
  if (!timeValid.valid) {
    return { success: false, message: timeValid.message };
  }

  // 5. 智能匹配门店
  const storeMatchResult = smartMatch(params.storeName, storeData.map(store => store.name));
  
  if (!storeMatchResult.matched) {
    if (storeMatchResult.candidates.length > 0) {
      return { 
        success: false, 
        message: `未找到完全匹配的门店，您是否指：${storeMatchResult.candidates.join('、')}` 
      };
    } else {
      return { success: false, message: '未找到匹配的门店' };
    }
  }

  const matchedStore = storeData.find(store => store.name === storeMatchResult.exactMatch);
  if (!matchedStore) {
    return { success: false, message: '未找到匹配的门店信息' };
  }

  // 6. 智能匹配服务
  const serviceMatchResult = smartMatch(params.serviceName, serviceData.map(service => service.name));
  
  if (!serviceMatchResult.matched) {
    if (serviceMatchResult.candidates.length > 0) {
      return { 
        success: false, 
        message: `未找到完全匹配的服务项目，您是否指：${serviceMatchResult.candidates.join('、')}` 
      };
    } else {
      return { success: false, message: '未找到匹配的服务项目' };
    }
  }

  const matchedService = serviceData.find(service => service.name === serviceMatchResult.exactMatch);
  if (!matchedService) {
    return { success: false, message: '未找到匹配的服务项目' };
  }

  // 7. 调用真实后端 API
  const apiResult = await callCreateBookingAPI({
    mobile: params.mobile,
    storeName: matchedStore.name,
    serviceName: matchedService.name,
    count: params.count,
    bookTime: params.bookTime
  });

  // 8. 返回结果
  return {
    ...apiResult,
    storeInfo: matchedStore,
    serviceInfo: matchedService
  };
}

/**
 * 处理用户输入
 * @param userInput 用户输入
 * @returns 处理结果
 */
async function handleUserInput(userInput) {
  const intentResult = recognizeIntent(userInput);
  
  switch (intentResult.intent) {
    case 'store_query':
      const stores = queryStores(intentResult.entities.keyword);
      if (stores.length === 0) {
        return {
          success: true,
          message: '未找到匹配的门店',
          data: []
        };
      } else {
        const storeList = stores.map(store => `${store.name} - ${store.address}`).join('\n');
        return {
          success: true,
          message: `找到以下门店：\n${storeList}`,
          data: stores
        };
      }
      
    case 'service_query':
      const services = queryServices(intentResult.entities.keyword);
      if (services.length === 0) {
        return {
          success: true,
          message: '未找到匹配的服务项目',
          data: []
        };
      } else {
        const serviceList = services.map(service => service.name).join('\n');
        return {
          success: true,
          message: `找到以下服务项目：\n${serviceList}`,
          data: services
        };
      }
      
    case 'create_booking':
      const entities = intentResult.entities;
      // 检查是否缺少必要参数
      const missingParams = [];
      if (!entities.mobile) missingParams.push('手机号');
      if (!entities.storeName) missingParams.push('门店名称');
      if (!entities.serviceName) missingParams.push('服务项目');
      if (!entities.count) missingParams.push('人数');
      if (!entities.bookTime) missingParams.push('预约时间（ISO格式）');
      
      if (missingParams.length > 0) {
        return {
          success: false,
          message: `请提供以下信息：${missingParams.join('、')}`
        };
      }
      
      // 创建预约
      return await createBooking(entities);
      
    default:
      return {
        success: false,
        message: '抱歉，我不太理解您的意思。您可以查询门店、服务项目或创建预约。'
      };
  }
}

// 导出功能
module.exports = {
  handleUserInput,
  queryStores,
  queryServices,
  createBooking,
  recognizeIntent,
  validatePhone,
  validatePeopleCount,
  validateBookingTime
};