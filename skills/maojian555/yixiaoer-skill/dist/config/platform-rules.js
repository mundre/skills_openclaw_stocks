export const PLATFORM_RULES = {
    AI_DouBao: { code: 'AI_DouBao', name: '豆包', supportedTypes: ['article'], platformFields: ['title', 'desc', 'content', 'tags', 'category', 'subCategory'] },
    DouYin: { code: 'DouYin', name: '抖音', supportedTypes: ['video', 'imageText', 'article'], platformFields: ['title', 'desc', 'covers', 'video', 'images', 'createType', 'category', 'subCategory', 'tags', 'location', 'music', 'shopping_cart', 'group_shopping', 'mini_app', 'challenge', 'hot_event', 'film', 'game', 'collection', 'sub_collection', 'cooperation_info', 'sync_apps', 'visibleType', 'allow_save', 'allow_download', 'allow_same_frame', 'nearby_show', 'prePubTime', 'statement', 'password', 'pubType', 'short_title', 'horizontalCover', 'pk_cover', 'bind_live_info', 'group', 'activity'] },
    KuaiShou: { code: 'KuaiShou', name: '快手', supportedTypes: ['video', 'imageText'], platformFields: ['title', 'desc', 'covers', 'video', 'images', 'createType', 'category', 'subCategory', 'tags', 'location', 'music', 'shopping_cart', 'group_shopping', 'mini_app', 'visibleType', 'allow_save', 'allow_download', 'allow_same_frame', 'nearby_show', 'prePubTime', 'statement', 'pubType', 'short_title', 'horizontalCover'] },
    ShiPinHao: { code: 'ShiPinHao', name: '视频号', supportedTypes: ['video', 'imageText'], platformFields: ['title', 'desc', 'covers', 'video', 'images', 'createType', 'category', 'subCategory', 'tags', 'location', 'music', 'shopping_cart', 'group_shopping', 'mini_app', 'visibleType', 'allow_save', 'allow_download', 'prePubTime', 'statement', 'pubType', 'short_title', 'horizontalCover', 'activity'] },
    XiaoHongShu: { code: 'XiaoHongShu', name: '小红书', supportedTypes: ['video', 'imageText'], platformFields: ['title', 'desc', 'covers', 'images', 'video', 'createType', 'category', 'subCategory', 'tags', 'location', 'music', 'shopping_cart', 'visibleType', 'allow_save', 'prePubTime', 'statement', 'pubType', 'horizontalCover'] },
    BiLiBiLi: { code: 'BiLiBiLi', name: '哔哩哔哩', supportedTypes: ['video', 'article'], platformFields: ['title', 'desc', 'covers', 'video', 'category', 'subCategory', 'tags', 'content', 'location', 'prePubTime', 'statement', 'contentSourceUrl', 'pubType', 'isFirst', 'advertisement'] },
    ZhiHu: { code: 'ZhiHu', name: '知乎', supportedTypes: ['video', 'imageText', 'article'], platformFields: ['title', 'desc', 'covers', 'images', 'video', 'category', 'subCategory', 'tags', 'topics', 'content', 'location', 'visibleType', 'prePubTime', 'statement', 'contentSourceUrl', 'pubType'] },
    QiEHao: { code: 'QiEHao', name: '企鹅号', supportedTypes: ['video', 'article'], platformFields: ['title', 'desc', 'covers', 'video', 'category', 'subCategory', 'tags', 'content', 'location', 'visibleType', 'prePubTime', 'statement', 'contentSourceUrl', 'pubType'] },
    YiDianHao: { code: 'YiDianHao', name: '一点号', supportedTypes: ['video', 'article'], platformFields: ['title', 'desc', 'covers', 'video', 'category', 'subCategory', 'tags', 'content', 'location', 'visibleType', 'prePubTime', 'statement', 'contentSourceUrl', 'pubType'] },
    WangYiHao: { code: 'WangYiHao', name: '网易号', supportedTypes: ['video', 'article'], platformFields: ['title', 'desc', 'covers', 'video', 'category', 'subCategory', 'tags', 'content', 'location', 'visibleType', 'prePubTime', 'statement', 'contentSourceUrl', 'pubType'] },
    AiQiYi: { code: 'AiQiYi', name: '爱奇艺', supportedTypes: ['video', 'article'], platformFields: ['title', 'desc', 'covers', 'video', 'category', 'subCategory', 'tags', 'content', 'location', 'visibleType', 'prePubTime', 'statement', 'contentSourceUrl', 'pubType'] },
    TengXunWeiShi: { code: 'TengXunWeiShi', name: '腾讯微视', supportedTypes: ['video'], platformFields: ['desc', 'covers', 'video', 'visibleType', 'prePubTime', 'statement'] },
    PiPiXia: { code: 'PiPiXia', name: '皮皮虾', supportedTypes: ['video'], platformFields: ['desc', 'covers', 'video', 'prePubTime', 'statement'] },
    TengXunShiPin: { code: 'TengXunShiPin', name: '腾讯视频', supportedTypes: ['video'], platformFields: ['title', 'desc', 'covers', 'video', 'tags', 'category', 'subCategory', 'prePubTime', 'statement', 'pubType'] },
    DuoDuoShiPin: { code: 'DuoDuoShiPin', name: '多多视频', supportedTypes: ['video'], platformFields: ['title', 'desc', 'covers', 'video', 'prePubTime', 'statement', 'pubType'] },
    MeiPai: { code: 'MeiPai', name: '美拍', supportedTypes: ['video'], platformFields: ['title', 'desc', 'covers', 'video', 'category', 'subCategory', 'prePubTime', 'statement'] },
    AcFun: { code: 'AcFun', name: 'AcFun', supportedTypes: ['video', 'article'], platformFields: ['title', 'desc', 'covers', 'video', 'category', 'subCategory', 'tags', 'content', 'visibleType', 'prePubTime', 'statement', 'pubType'] },
    DeWu: { code: 'DeWu', name: '得物', supportedTypes: ['video'], platformFields: ['title', 'desc', 'covers', 'video', 'visibleType', 'prePubTime', 'statement'] },
    CheJiaHao: { code: 'CheJiaHao', name: '车家号', supportedTypes: ['video', 'article'], platformFields: ['title', 'desc', 'covers', 'video', 'content', 'category', 'subCategory', 'visibleType', 'prePubTime', 'statement', 'pubType'] },
    YiCheHao: { code: 'YiCheHao', name: '易车号', supportedTypes: ['video', 'article'], platformFields: ['title', 'desc', 'covers', 'video', 'content', 'category', 'subCategory', 'visibleType', 'prePubTime', 'statement', 'pubType'] },
    TouTiaoHao: { code: 'TouTiaoHao', name: '头条号', supportedTypes: ['video', 'article'], platformFields: ['title', 'desc', 'covers', 'video', 'category', 'subCategory', 'tags', 'content', 'location', 'visibleType', 'prePubTime', 'statement', 'contentSourceUrl', 'pubType', 'isFirst'] },
    BaiJiaHao: { code: 'BaiJiaHao', name: '百家号', supportedTypes: ['video', 'imageText', 'article'], platformFields: ['title', 'desc', 'covers', 'images', 'video', 'category', 'subCategory', 'tags', 'content', 'location', 'visibleType', 'prePubTime', 'statement', 'contentSourceUrl', 'pubType', 'isFirst', 'advertisement'] },
    SouHuHao: { code: 'SouHuHao', name: '搜狐号', supportedTypes: ['video', 'article'], platformFields: ['title', 'desc', 'covers', 'video', 'category', 'subCategory', 'content', 'location', 'visibleType', 'prePubTime', 'statement', 'contentSourceUrl', 'pubType'] },
    DaYuHao: { code: 'DaYuHao', name: '大鱼号', supportedTypes: ['video', 'article'], platformFields: ['title', 'desc', 'covers', 'video', 'category', 'subCategory', 'content', 'location', 'visibleType', 'prePubTime', 'statement', 'contentSourceUrl', 'pubType'] },
    SouHuShiPin: { code: 'SouHuShiPin', name: '搜狐视频', supportedTypes: ['video'], platformFields: ['title', 'desc', 'covers', 'video', 'prePubTime', 'statement'] },
    XiaoHongShuShangJiaHao: { code: 'XiaoHongShuShangJiaHao', name: '小红书商家号', supportedTypes: ['video'], platformFields: ['title', 'desc', 'covers', 'video', 'createType', 'category', 'tags', 'location', 'visibleType', 'prePubTime', 'statement'] },
    FengWang: { code: 'FengWang', name: '蜂网', supportedTypes: ['video'], platformFields: ['title', 'desc', 'covers', 'video', 'prePubTime'] },
    MeiYou: { code: 'MeiYou', name: '美柚', supportedTypes: ['video'], platformFields: ['title', 'desc', 'covers', 'video', 'prePubTime'] },
    KuaiChuanHao: { code: 'KuaiChuanHao', name: '快传号', supportedTypes: ['article'], platformFields: ['title', 'desc', 'covers', 'content', 'category', 'subCategory', 'location', 'visibleType', 'prePubTime', 'statement'] },
    XueQiuHao: { code: 'XueQiuHao', name: '雪球号', supportedTypes: ['article'], platformFields: ['title', 'desc', 'covers', 'content', 'category', 'subCategory', 'location', 'visibleType', 'prePubTime', 'statement'] },
    XinLangWeiBo: { code: 'XinLangWeiBo', name: '新浪微博', supportedTypes: ['video', 'imageText', 'article'], platformFields: ['title', 'desc', 'covers', 'images', 'video', 'category', 'subCategory', 'tags', 'content', 'location', 'visibleType', 'prePubTime', 'statement', 'contentSourceUrl', 'pubType'] },
    DouBan: { code: 'DouBan', name: '豆瓣', supportedTypes: ['article'], platformFields: ['title', 'desc', 'covers', 'content', 'category', 'location', 'visibleType', 'prePubTime', 'statement'] },
    CSDN: { code: 'CSDN', name: 'CSDN', supportedTypes: ['article'], platformFields: ['title', 'desc', 'covers', 'content', 'category', 'subCategory', 'tags', 'location', 'visibleType', 'prePubTime', 'statement', 'contentSourceUrl'] },
    JianShu: { code: 'JianShu', name: '简书', supportedTypes: ['article'], platformFields: ['title', 'desc', 'covers', 'content', 'location', 'visibleType', 'prePubTime', 'statement'] },
    WiFiWanNengYaoShi: { code: 'WiFiWanNengYaoShi', name: 'wifi万能钥匙', supportedTypes: ['article'], platformFields: ['title', 'desc', 'covers', 'content', 'category', 'location', 'visibleType', 'prePubTime', 'statement'] },
    WeiXinGongZhongHao: { code: 'WeiXinGongZhongHao', name: '微信公众号', supportedTypes: ['article'], platformFields: ['title', 'desc', 'covers', 'content', 'contentList', 'headImage', 'category', 'subCategory', 'authorName', 'createType', 'contentSourceUrl', 'allowAbstract', 'allowForward', 'notifySubscribers', 'province', 'city', 'sex', 'location'] },
    XiGuaShiPin: { code: 'XiGuaShiPin', name: '西瓜视频', supportedTypes: ['video'], platformFields: ['title', 'desc', 'covers', 'video', 'tags', 'category', 'subCategory', 'prePubTime', 'statement', 'pubType'] },
};
export var TimeUnit;
(function (TimeUnit) {
    TimeUnit["Day"] = "day";
    TimeUnit["Minute"] = "minute";
})(TimeUnit || (TimeUnit = {}));
export var FormType;
(function (FormType) {
    FormType["Platform"] = "platform";
    FormType["Task"] = "task";
})(FormType || (FormType = {}));
export var PublishChannel;
(function (PublishChannel) {
    PublishChannel["Cloud"] = "cloud";
    PublishChannel["Local"] = "local";
})(PublishChannel || (PublishChannel = {}));
export var PublishType;
(function (PublishType) {
    PublishType["Article"] = "article";
    PublishType["ImageText"] = "imageText";
    PublishType["Video"] = "video";
})(PublishType || (PublishType = {}));
export function getPlatformRule(platformCode) {
    return PLATFORM_RULES[platformCode];
}
export function getAllPlatforms() {
    return Object.values(PLATFORM_RULES);
}
export function buildContentPublishForm(publishType, params) {
    const form = {
        formType: 'task',
        covers: [],
    };
    if (publishType === 'video') {
        form.title = params.title || '';
        form.description = params.description || '';
        form.declaration = 0;
        form.tagType = '位置';
        form.visibleType = 0;
        form.allow_save = 1;
    }
    else if (publishType === 'imageText') {
        form.title = params.title || '';
        form.description = params.description || '';
        form.declaration = 0;
        form.type = 0;
        form.visibleType = 0;
    }
    else if (publishType === 'article') {
        form.title = params.title || '';
        form.description = params.description || '';
        form.type = 0;
        form.visibleType = 0;
        form.verticalCovers = [];
        if (typeof params.createType === 'number')
            form.createType = params.createType;
        if (typeof params.pubType === 'number')
            form.pubType = params.pubType;
    }
    if (params.tags && params.tags.length > 0) {
        form.tags = params.tags;
    }
    return form;
}
export function buildPlatformPublishForm(publishType, platformCode, params) {
    const rule = getPlatformRule(platformCode);
    if (!rule)
        return {};
    return buildContentPublishForm(publishType, params);
}
export function validatePublishParams(platformCode, publishType) {
    const rule = getPlatformRule(platformCode);
    if (!rule) {
        return { valid: false, errors: [`不支持的平台: ${platformCode}`] };
    }
    if (!rule.supportedTypes.includes(publishType)) {
        return { valid: false, errors: [`${rule.name}不支持${publishType}类型`] };
    }
    return { valid: true, errors: [] };
}
//# sourceMappingURL=platform-rules.js.map