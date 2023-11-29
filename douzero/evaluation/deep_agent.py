import torch
import numpy as np
from douzero.env.env import test_get_obs
from douzero.env.move_generator import *

def _load_model(position, model_path):
    from douzero.dmc.models import model_dict, pre_model_dict
    middle_path = model_path.split('/')
    middle_path[1] = '/prediction_' + middle_path[1]
    pre_model_path = "".join(middle_path)
    model = model_dict[position]()
    model_state_dict = model.state_dict()
    pred_model = pre_model_dict[position]()
    pred_model_state_dict = pred_model.state_dict()
    if torch.cuda.is_available():
        pretrained = torch.load(model_path, map_location='cuda:0')
        pred_pretrained = torch.load(pre_model_path, map_location='cuda:0')
    else:
        pretrained = torch.load(model_path, map_location='cpu')
        pred_pretrained = torch.load(pre_model_path, map_location='cpu')
    pretrained = {k: v for k, v in pretrained.items() if k in model_state_dict}
    pred_pretrained = {k: v for k, v in pred_pretrained.items() if k in pred_model_state_dict}
    model_state_dict.update(pretrained)
    model.load_state_dict(model_state_dict)
    pred_model_state_dict.update(pred_pretrained)
    pred_model.load_state_dict(pred_model_state_dict)
    if torch.cuda.is_available():
        model.cuda()
        pred_model.cuda()
    model.eval()
    pred_model.eval()
    return model, pred_model

class DeepAgent:

    def __init__(self, position, model_path):
        self.model, self.pre_model = _load_model(position, model_path)

    def act(self, infoset):

        obs = test_get_obs(infoset)
        z_batch = torch.from_numpy(obs['z_batch']).float()
        x_batch = torch.from_numpy(obs['x_batch']).float()
        obs_z = torch.from_numpy(obs['z']).float()
        obs_x = torch.from_numpy(obs['x_no_action']).float()
        if len(obs_z.size()) == 2:
            obs_z = obs_z.unsqueeze(0)
        if len(obs_x.size()) == 1:
            obs_x = obs_x.unsqueeze(0)
        hand_legal = obs['hand_legal']
        if torch.cuda.is_available():
            z_batch, x_batch = z_batch.cuda(), x_batch.cuda()
            obs_z, obs_x = obs_z.cuda(), obs_x.cuda()
            hand_legal = hand_legal.cuda()
        _, pred_hand = self.pre_model.forward(obs_z, obs_x, hand_legal)
        prob = pred_hand.view(1, -1)
        predict_hand = prob.expand(x_batch.shape[0], -1)
        y_pred = self.model.forward(z_batch, x_batch, predict_hand, return_value=True)['values']

        y_pred = y_pred.detach().cpu().numpy()

        best_action_index = np.argmax(y_pred, axis=0)[0]
        best_action = infoset.legal_actions[best_action_index]
        best_action_confidence = y_pred[best_action_index]

        action_list = [(infoset.legal_actions[i], y_pred[i]) for i in range(len(infoset.legal_actions))]
        action_list.sort(key=lambda x: x[1], reverse=True)
        # for a in action_list:
        #     print(a[0],round(a[1].tolist()[0],2))
        return best_action,best_action_confidence

class InfoSet(object):
    def __init__(self,player_position):
        self.player_position = player_position
        self.player_hand_cards = None
        self.num_cards_left_dict = None
        self.three_landlord_cards = None
        self.card_play_action_seq = None
        self.other_hand_cards = None
        self.legal_actions = None
        self.last_move = None
        self.last_two_moves = None
        self.last_move_dict = None
        self.played_cards = None
        self.all_handcards = None
        self.last_pid = None
        self.bomb_num = None
        self.init_card = None

if __name__ == "__main__":
    ai_cards = [14, 14, 14, 12, 11, 11, 10, 9, 8, 8, 8, 8, 7, 3, 3, 3, 3]
    ms = MovesGener(ai_cards)
    position = 'landlord'
    #模型路径
    card_play_model_path_dict = {
        'landlord': "baselines/landlord.ckpt",
        'landlord_up': "baselines/landlord_up.ckpt",
        'landlord_down': "baselines/landlord_down.ckpt"
    }
    ai = DeepAgent(position,card_play_model_path_dict[position])

    Info = InfoSet(position)

    Info.player_hand_cards = ai_cards
    Info.num_cards_left_dict = {"landlord": 20,"landlord_up": 17,"landlord_down": 17}
    Info.three_landlord_cards = [14, 5, 7]
    Info.card_play_action_seq = []
    Info.other_hand_cards =[10, 20, 7, 10, 4, 30, 17, 6, 6, 17, 5, 4, 11, 13, 10, 9, 9, 9, 9, 6, 12, 13, 12, 11, 13, 12, 4, 4, 5, 13, 9, 6, 17, 17]
    Info.legal_actions = ms.gen_moves()   
    Info.last_move =[]
    Info.last_two_moves = []
    Info.last_move_dict = {"landlord": [],"landlord_up": [],"landlord_down": []}
    Info.played_cards = {
                            "landlord": [],
                            "landlord_up": [],
                            "landlord_down": []
                         }
    
    Info.all_handcards = {
                        "landlord": ai_cards,
                        "landlord_up": [10, 20, 7, 10, 4, 30, 17, 6, 6, 17, 5, 4, 11, 13, 10, 9, 9],
                        "landlord_down": [9, 9, 6, 12, 13, 12, 11, 13, 12, 4, 4, 5, 13, 9, 6, 17, 17]
                            }
    
    Info.last_pid = "landlord"
    Info.bomb_num = 0
    Info.init_card={
                "three_landlord_cards": [14, 5, 7],
                "landlord_up": [10, 20, 7, 10, 4, 30, 17, 6, 6, 17, 5, 4, 11, 13, 10, 9, 9],
                "landlord": ai_cards,
                "landlord_down": [9, 9, 6, 12, 13, 12, 11, 13, 12, 4, 4, 5, 13, 9, 6, 17, 17]
            }

    print(ai.act(Info))
