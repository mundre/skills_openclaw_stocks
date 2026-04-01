# 新活素查房日采集反馈V2

查询新活素查房日采集反馈数据。

## 基本信息

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-sxk-report/xhsWardRoundsReportV2` |
| 请求方式     | POST                                                         |
| Content-Type | application/json                                             |

## Headers

- `appKey` (string): 应用密钥，从环境变量 `XG_BIZ_API_KEY` 或 `XG_APP_KEY` 获取

## 请求参数

| 参数名        | 类型   | 必填 | 说明            |
| ------------- | ------ | ---- | --------------- |
| zoneId        | string | 否   | 区划ID          |
| regionName    | string | 否   | 大区名称        |
| districName   | string | 否   | 区域名称        |
| areaName      | string | 否   | 地区名称        |
| territoryName | string | 否   | 辖区名称        |
| periodStart   | string | 否   | 期间开始日期    |
| periodEnd     | string | 否   | 期间结束日期    |
| page          | number | 否   | 页码，默认第1页 |

## 请求示例

```bash
curl -X POST "https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/xhsWardRoundsReportV2" \
  -H "appKey: YOUR_APP_KEY" \
  -H "Content-Type: application/json" \
  -d '{"periodStart": "2025-01-01", "periodEnd": "2025-01-31", "page": 1}'
```

## 响应参数

`data` 为数组，数组元素包含以下字段：

| 参数名                                 | 类型   | 说明                        |
| -------------------------------------- | ------ | --------------------------- |
| zoneId                                 | string | 区域ID                      |
| areaName                               | string | 一级区域名称（大区）        |
| districtName                           | string | 二级区域名称（地区）        |
| regionName                             | string | 三级区域名称（子区域）      |
| territoryName                          | string | 辖区名称                    |
| submitName                             | string | 提交人昵称                  |
| hcoName                                | string | 医疗机构名称                |
| hcoDepartment                          | string | 医疗机构科室                |
| cycle                                  | string | 周期                        |
| medicatedPatientCount                  | number | 用药患者数量                |
| acuteHeartFailureLowDoseCount          | number | 急性心衰低剂量患者数量      |
| acuteHeartFailureShortCourseCount      | number | 急性心衰短疗程患者数量      |
| selfPayAfterThreeDaysCount             | number | 三天后自费患者数量          |
| acuteHeartFailureCourseBelow3DaysCount | number | 急性心衰疗程低于3天患者数量 |
| selfPayAfter3DaysCount                 | number | 3天后自费患者数量           |
| medicalInsuranceRiskCaseCount          | number | 医保风险病例数量            |
| nonMedicatedPatientCount               | number | 非用药患者数量              |
| undiagnosedWithCommonSymptomsCount     | number | 有常见症状但未确诊患者数量  |
| potentialProductCandidatesCount1       | number | 潜在产品候选患者数量1       |
| potentialProductCandidatesCount2       | number | 潜在产品候选患者数量2       |
| undiagnosedWithMedicationHistoryCount  | number | 有用药史但未确诊患者数量    |
| currentDayFollowUpStatus               | object | 当日随访状态                |

## 响应示例

```json
{
  "resultCode": "0",
  "resultMsg": "success",
  "data": [
    {
      "zoneId": "ZONE001",
      "areaName": "华东大区",
      "districtName": "上海地区",
      "regionName": "上海子区域",
      "territoryName": "上海辖区",
      "submitName": "张三",
      "hcoName": "上海市第一人民医院",
      "hcoDepartment": "心内科",
      "cycle": "2025-W01",
      "medicatedPatientCount": 50,
      "acuteHeartFailureLowDoseCount": 10,
      "acuteHeartFailureShortCourseCount": 8,
      "selfPayAfterThreeDaysCount": 5,
      "acuteHeartFailureCourseBelow3DaysCount": 3,
      "selfPayAfter3DaysCount": 2,
      "medicalInsuranceRiskCaseCount": 1,
      "nonMedicatedPatientCount": 15,
      "undiagnosedWithCommonSymptomsCount": 5,
      "potentialProductCandidatesCount1": 3,
      "potentialProductCandidatesCount2": 2,
      "undiagnosedWithMedicationHistoryCount": 4,
      "currentDayFollowUpStatus": {}
    }
  ],
  "timestamp": 1704067200000,
  "success": true
}
```

## 查询总记录数

在接口地址后追加 `/count`：

```bash
curl -X POST "https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/xhsWardRoundsReportV2/count" \
  -H "appKey: YOUR_APP_KEY" \
  -H "Content-Type: application/json" \
  -d '{"periodStart": "2025-01-01", "periodEnd": "2025-01-31"}'
```

响应：

```json
{
  "resultCode": "0",
  "resultMsg": "success",
  "data": 100,
  "timestamp": 1704067200000,
  "success": true
}
```
