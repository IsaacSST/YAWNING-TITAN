from datetime import datetime
import pytest
import os
import yaml
from typing import Dict,Any
from yaml import SafeLoader
from tests import TEST_CONFIG_PATH
from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy as PPOMlp
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor

from yawning_titan.envs.generic.core.blue_interface import BlueInterface
from yawning_titan.envs.generic.core.red_interface import RedInterface
from yawning_titan.envs.generic.generic_env import GenericNetworkEnv
from yawning_titan.envs.generic.helpers import network_creator
from yawning_titan.envs.generic.core.action_loops import ActionLoop
from yawning_titan.envs.generic.core.network_interface import NetworkInterface

@pytest.fixture
def temp_config_from_base(tmpdir_factory)->str:
    """
    Pytest fixture to create temporary config files derived from a base config yaml file.
    """
    def _temp_config_from_base(base_config_path:str,updated_settings:Dict[str,Dict[str,Any]]):
        try:
            with open(base_config_path) as f:
                new_settings:Dict[str,Dict[str,Any]] = yaml.load(f, Loader=SafeLoader)
        except FileNotFoundError as e:
            msg = f"Configuration file does not exist: {base_config_path}"
            print(msg)  # TODO: Remove once proper logging is setup
            raise e

        for key,val in updated_settings.items():
            new_settings[key].update(val)

        temp_config_filename = "tmp_config" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".yaml"
        temp_config_path = os.path.join(tmpdir_factory.mktemp("tmp_config"),temp_config_filename)
        
        with open(temp_config_path, 'w') as file:
            yaml.dump(new_settings, file)

        return temp_config_path
    return _temp_config_from_base

@pytest.fixture
def basic_2_agent_loop(request,temp_config_from_base)->ActionLoop:
    """
    Use parameterized settings to return a configured ActionLoop
    """
    matrix, node_positions = network_creator.create_18_node_network()

    entry_nodes = None
    settings_path = None
    high_value_nodes = None
    num_episodes = 1

    if "settings_file" in request.param:
        settings_path = os.path.join(TEST_CONFIG_PATH, request.param["settings_file"])
        if "custom_settings" in request.param:
            settings_path = temp_config_from_base(settings_path,request.param["custom_settings"])
      
    if "entry_nodes" in request.param:
        entry_nodes = request.param["entry_nodes"]

    if "episodes" in request.param:
        num_episodes = request.param["episodes"]    

    if "high_value_target" in request.param:
        high_value_nodes = request.param["high_value_nodes"]

    network_interface = NetworkInterface(matrix, node_positions, entry_nodes=entry_nodes, high_value_nodes=high_value_nodes,settings_path=settings_path)

    red = RedInterface(network_interface)
    blue = BlueInterface(network_interface)

    env = GenericNetworkEnv(red, blue, network_interface)

    check_env(env, warn=True)

    _ = env.reset()

    eval_callback = EvalCallback(
            Monitor(env), eval_freq=1000, deterministic=False, render=False
        )

    agent = PPO(PPOMlp, env, verbose=1, seed=network_interface.SEED) #TODO: allow PPO to inherit environment seed. Monkey patch additional feature?

    agent.learn(
            total_timesteps=1000, n_eval_episodes=100, callback=eval_callback
    )

    return ActionLoop(env,agent,episode_count=num_episodes)