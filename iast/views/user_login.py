#!/usr/local/env python
# -*- coding: utf-8 -*-
import logging

from captcha.models import CaptchaStore
from django.contrib.auth import authenticate, login

from base import R
from iast.base.user import UserEndPoint

logger = logging.getLogger("dongtai-webapi")


class UserLogin(UserEndPoint):
    """
    用户登录
    """
    permission_classes = []
    authentication_classes = []
    name = "user_views_login"
    description = "用户登录"

    def post(self, request):
        if self.is_sso(request) or self.verified_captcha(request):
            if self.do_login(request):
                return R.success(msg='登录成功')
            else:
                return R.failure(status=202, msg='登录失败')
        else:
            return R.failure(status=203, msg='验证码不正确')

    @staticmethod
    def do_login(request):
        try:
            username = request.data["username"]
            password = request.data["password"]
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                return True
        except Exception as e:
            logger.error(f'login failed, reason: {e}')
            pass
        return False

    @staticmethod
    def verified_captcha(request):
        try:
            hash_key = request.data["captcha_hash_key"]
            captcha = request.data["captcha"]
            if hash_key and captcha:
                get_captcha = CaptchaStore.objects.get(hashkey=hash_key)
                # 如果验证码匹配
                if get_captcha.response == captcha.lower():
                    return True
        except Exception as e:
            pass
        return False

    @staticmethod
    def is_sso(request):
        try:
            mode = request.data.get("mode")
            return mode == 'sso'
        except:
            return False
