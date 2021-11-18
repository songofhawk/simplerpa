import time

from simplerpa.core.Variable import Variable
from simplerpa.core.data.Action import Action
from simplerpa.core.action.ActionScreen import ActionScreen
from simplerpa.core.const import STATE
from simplerpa.core.data.Misc import ForEach
from simplerpa.core.data.Project import Project
from simplerpa.core.extractor.Extractor import Extractor


class Env(object):
    @classmethod
    def adjust_resolution(cls, screen_width, screen_height):
        ActionScreen.change_resolution((screen_width, screen_height))


class Executor:
    project: Project = None
    variables: Variable = Variable()

    def __init__(self, project: Project):
        self.project = project
        project.executor = self
        self._current_state = None
        self._current_index = None
        self._current_states = None

        # 用列表实现栈
        self._currents = []

    def run(self):
        if self.project is None:
            return

        self._load_env()
        states = self.project.states
        if states is None or len(states) == 0:
            return
        self._current_states = states
        init_state = states[0]
        self._current_index = 0
        self._current_state = init_state
        while self._current_state is not None:
            self._one_state(self._current_state)

    def _load_env(self):
        if self.project.screen_width is not None and \
                self.project.screen_height is not None:
            Env.adjust_resolution(self.project.screen_width, self.project.screen_height)

    # def _run_from_state(self, init_state):
    #     self._one_state(init_state)

    def _one_state(self, the_state):
        print('enter state "{}"-{}'.format(the_state.name, the_state.id))
        Action.save_call_env({STATE: the_state})

        # check中如果触发了影响流程的fail_action，那么就退出当前状态，直接按照该action指定的状态迁移
        if not self._do_find(the_state.check):
            fail_trans = the_state.check.fail
            self._do_transition(fail_trans)
            return

        # monitor
        if not self._do_monitor(the_state.monitor):
            raise RuntimeError('monitor failed in state "{}"'.format(the_state.name))

        Action.call(the_state.action)

        # 暂时find先不执行影响流程的fail_action（is_flow_control==True)
        found = self._do_find(the_state.find)
        if found:
            transition = the_state.transition
            form = the_state.form
            if isinstance(form, Extractor):
                if form.do() is None:
                    fail_trans = form.fail
                    self._do_transition(fail_trans)
                    return
            foreach = the_state.foreach
            if isinstance(foreach, ForEach):
                foreach.do()
        else:
            transition = the_state.find.fail

        self._do_transition(transition)

    def _do_transition(self, transition):
        '''从这里开始，处理transition模块'''
        if transition is None:
            # 改成transition为空的话，什么也不做
            return
        if transition.reach_max_time():
            print('reach max time({}) of transition, terminate!'.format(transition.max_time))
            self._current_state = None
            self._current_index = None
            return

        if transition.wait_before is not None:
            time.sleep(transition.wait_before)

        # 首先调用触发transition的动作
        Action.call(transition.action)

        if transition.wait is not None:
            time.sleep(transition.wait)

        # 如果有子状态集，进入首选子状态
        # sub_states = transition.sub_states
        # if sub_states is not None and len(sub_states) > 0:
        #     self.drill_into_substates(sub_states)

        # 迁移到下一个状态
        transition.count()
        trans_to = transition.to
        next_state, next_index = self._get_next_state(trans_to)
        if next_state is None:
            self._current_state = None
            self._current_index = None
            return

        self._current_index = next_index
        self._current_state = next_state

    def drill_into_substates(self, sub_states):
        self.push_currents()

        self._current_index = 0
        sub_init_state = sub_states[0]
        self._current_states = sub_states
        self._current_state = sub_init_state
        while self._current_state is not None:
            self._one_state(self._current_state)

        self.pop_currents()

    def _get_next_state(self, trans_to):
        if trans_to.is_next:
            if self._current_index < len(self._current_states) - 1:
                next_index = self._current_index + 1
                next_state = self._current_states[next_index]
            else:
                next_state = None
                next_index = None
        elif trans_to.id is not None:
            next_state, next_index = self._find_state_by_id(self._current_states, trans_to.id)
        else:
            next_state = None
            next_index = None
        return next_state, next_index

    @staticmethod
    def _find_state_by_id(current_states, state_id):
        for i, state in enumerate(current_states):
            if state.id == state_id:
                return state, i
        return None, None

    def push_currents(self):
        self._currents.append((self._current_state, self._current_index, self._current_states))

    def pop_currents(self):
        (self._current_state, self._current_index, self._current_states) = self._currents.pop()

    @staticmethod
    def _do_find(find):
        """
        check的目标是检查页面是否中的处于当前状态，所以只要有一条不符，就失败。此时如果fail_action是locate_state，就会从当前状态组中逐一检查处于哪个状态，并且直接跳转到对应的状态执行
        :param find:
        :return:
        """
        if find is None:
            return True

        results = find.do()
        if len(results) > 0:
            return True

        return False

    @staticmethod
    def _do_monitor(monitor):
        if monitor is None:
            return True

        change = monitor.do()
        if change is None:
            return False
        else:
            return True

    def _locate_state(self):
        # 执行定位状态
        print("即将定位当前界面处于那个状态...")
        for one_state in self._current_states[::-1]:
            # 逆序遍历状态列表,也可以用reversed方法
            print("-- 测试是否属于状态'{}'".format(one_state.name))
            locate_check = one_state.check
            if locate_check is None:
                continue
            check_pass, _ = self._get_find_result(locate_check, False)
            if check_pass:
                print("---- 找到了,就是这个状态!")
                self._current_state = one_state
                self._current_index = one_state.id
                return False
        self._current_state = None
        self._current_index = None
        return False
