# -*- coding: utf-8 -*-

"""
    qqbot.utils
    -----------

    Implements various utils

    :copyright: © 2018 by the leetao.
    :license: GPL3.0,see LICENSE for more details
"""

import configparser

import os


class Error(Exception):
    """
        配置相关异常的基类
    """

    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__


class ConfigNotFoundError(Error):
    """
        当配置不存在时抛出异常
    """

    def __init__(self, path=''):
        Error.__init__(self, "配置文件 %r 不存在" % (path,))
        self.path = path
        self.args = (path,)


class ConfigParamTypeError(Error):
    """
        参数类型错时抛出异常
    """

    def __init__(self, params, param_type):
        msg = ["参数类型错误: ", repr(params), " 不是 ", repr(param_type)]
        Error.__init__(self, "".join(msg))
        self.params = params
        self.param_type = param_type
        self.args = (params, param_type)


class NoOptionError(Error):
    """
        文件中不存在相关配置抛出异常
    """

    def __init__(self, option, section):
        Error.__init__(self, "%r 中不存在 %r 的配置" % (section, option))
        self.option = option
        self.section = section
        self.args = (option, section)


class NoSectionError(Error):
    """
        文件中不存在相关部分的时候抛出异常
    """

    def __init__(self, section):
        Error.__init__(self, "不存在有关 %r 的配置" % (section))
        self.section = section
        self.args = (section,)


def _get_config(path, config_dict):
    """
        根据配置文件路径以及配置列表返回相关配置

        :return dict
    """

    config_value_dict = {}

    cp = configparser.ConfigParser()

    if os.path.exists(path):
        cp.read(path)
        if isinstance(config_dict, dict):
            for key, value in config_dict.items():
                if isinstance(value, list):
                    try:
                        for item in value:
                            config_value_dict[item] = cp.get(key, item)
                    except configparser.NoSectionError as e:
                        raise NoSectionError(key)
                    except configparser.NoOptionError as e:
                        raise NoOptionError(key, item)
                elif isinstance(value, str):
                    config_value_dict[value] = cp.get(key, value)
                else:
                    raise ConfigParamTypeError(value, 'str or list')
        else:
            raise ConfigParamTypeError(config_dict, dict)
    else:
        raise ConfigNotFoundError(path)
    return config_value_dict


def get_qqbot_config(path):
    """
        获取配置文件的所有配置

        获取 DEFAULT 配置
        获取 PERSONAL 配置如果有的话
        获取 CHATBOT 配置如果有的话
    """
    config_dict = {"DEFAULT": ["chat_enabled", "share_enabled", "remember_enabled"],
                   "PERSONAL": ["account", "password"], "CHATBOT": ["bot_name", "need_train", "train_data"]}
    return _get_config(path, config_dict)


def generate_qqbot_config(path=None):
    """
        生成默认配置文件
        如果没有指定路径则在当前目录生成 qqbot.cfg 文件
    """
    cp = configparser.ConfigParser()

    # 添加 DEFAULT 部分
    cp.set("DEFAULT", "chat_enabled", "True")
    cp.set("DEFAULT", "share_enabled", "False")
    cp.set("DEFAULT", "remember_enabled", "True")

    # 添加 PERSONAL 部分
    cp.add_section("PERSONAL")
    cp.set("PERSONAL", "account", "*")
    cp.set("PERSONAL", "password", "*")

    # 添加 PERSONAL 部分
    cp.add_section("CHATBOT")
    cp.set("CHATBOT", "bot_name", "mtdhb")
    cp.set("CHATBOT", "need_train", "False")
    cp.set("CHATBOT", "train_data", "*")

    if path is None:
        config_path = "qqbot.cfg"
    else:
        config_path = os.path.join(path, "qqbot.cfg")

    with open(config_path, "w+") as f:
        cp.write(f)