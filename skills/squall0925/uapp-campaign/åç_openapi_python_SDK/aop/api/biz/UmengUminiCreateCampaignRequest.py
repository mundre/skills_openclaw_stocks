# -*- coding: utf-8 -*-
from aop.api.base import BaseApi

class UmengUminiCreateCampaignRequest(BaseApi):
    """添加推广链接

    References
    ----------
    https://developer.umeng.com/open-api/docs/com.umeng.umini/umeng.umini.createCampaign/1

    """

    def __init__(self, domain=None):
        BaseApi.__init__(self, domain)
        self.dataSourceId = None
        self.campaignName = None
        self.channelName = None
        self.path = None

    def get_api_uri(self):
        return '1/com.umeng.umini/umeng.umini.createCampaign'

    def get_required_params(self):
        return ['dataSourceId', 'campaignName', 'channelName']

    def get_multipart_params(self):
        return []

    def need_sign(self):
        return True

    def need_timestamp(self):
        return False

    def need_auth(self):
        return True

    def is_inner_api(self):
        return False
