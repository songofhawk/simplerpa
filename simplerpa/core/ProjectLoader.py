import os
from types import CodeType

from simplerpa.core.data import Project
from simplerpa.core.data.Misc import State, Transition, To
from simplerpa.core.data.Project import Project
from simplerpa.core.data.ScreenRect import ScreenRect
from simplerpa.core.share.yaml import yaml
from simplerpa.objtyping import objtyping


class ProjectLoader:
    @classmethod
    def load(cls, project_file):
        path_root, file = os.path.split(project_file)
        with open(project_file, encoding='utf-8') as f:
            yaml_obj = yaml.load(f)
            project = objtyping.from_dict_list(yaml_obj, Project, reserved_classes=[ScreenRect])
            project.path_root = path_root
            cls.parse(project)
            return project

    @classmethod
    def parse(cls, project: Project):
        cls._traverse_set(project, project, 'project', reserved_classes=[ScreenRect])

    @classmethod
    def _traverse_set(cls, obj, root_node, ref_root_name, reserved_classes=[]):
        """
        递归处理，把项目配置对象中，每个子节点，都加上根节点的引用
        同时，生成一个包含所有state的字典，方便做跳转
        :param obj: 主对象
        :param root_node: 根节点
        :param ref_root_name: 根节点属性名
        :param reserved_classes: 保留的类（不解析，不赋值）
        :return:
        """
        if obj is None:
            return None
        if type(obj) in reserved_classes:
            return obj
        if objtyping.is_basic_type(obj):
            return obj

        all_states = root_node.all_states

        attributes = cls._get_all_children(obj)
        for attr in attributes:
            if attr is None:
                continue
            if objtyping.is_basic_type(attr):
                continue
            if type(attr) in reserved_classes:
                continue
            if isinstance(attr, State) and attr.id is not None:
                all_states[attr.id] = State
            if isinstance(attr, Transition) and attr.to is None:
                attr.to = To()
            cls._traverse_set(attr, root_node, ref_root_name, reserved_classes)

        if not obj == root_node and not isinstance(obj, list) and not isinstance(obj, dict) and not isinstance(obj, tuple) and not callable(obj) and not isinstance(obj, CodeType):
            setattr(obj, ref_root_name, root_node)

    @classmethod
    def _get_all_children(cls, obj):
        if isinstance(obj, list):
            return obj
        elif hasattr(obj, '__dict__'):
            return obj.__dict__.values()
        else:
            return []
