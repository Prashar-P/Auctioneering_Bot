import random
import numpy as np 
from enum import Enum


class Priority(Enum):
    HIGH =  0.9
    MEDIUM = 0.6
    LOW = 0.3  

class Bot(object):
    def __init__(self):
        self.name = (
            "username"  # Put your id number her. String or integer will both work
        )
        self.num_of_items = 8 # Total Number of items to be collected (3+3+1+1)
        self.price_for_items = {} # winning bid prices for each artists paintings
        self.average_price_for_items = {} # average winning bid prices for each last 3 artists paintings
        self.last_item = None # last item won          

    def only_bid_for_higher_priority(self,bid,priority):
        """Update bids to only bid for high/medium priority items when there are less than n items left
            Parameters:
                bid(int): 			The current bid value
                priority(float): 	Priority of the item (How important it is for us to get the item)
                num_of_items(int):  Number of items left to get
            
            Returns:
                int:Your bid. Set to 0 if low priority.
        """
        if(self.num_of_items < 4 and priority == Priority['LOW'].value):
            bid = 0
        return bid
    
    def find_average_for_previous_items(self,bid,current_painting,current_round,amounts_paid,priority):
        """Updates bid if current bid is too high compared to the average price of the item
            Parameters:
                bid(int): 			The current bid value
                current_painting(str):			The artist of the current painting that is being bid on
                current_round(int): 			The current round of the auction game
                amounts_paid(list int):			List of amounts paid for paintings in the rounds played so far
            Returns:
                int:Your bid. Set to 0 if low priority.
        """
        if(current_round > 0):
            if(self.last_item in self.price_for_items.keys()):
                self.price_for_items[self.last_item].append(amounts_paid[-1])
            else:
                self.price_for_items[self.last_item] = [amounts_paid[-1]]
        self.last_item = current_painting

        if(current_painting in self.price_for_items.keys()):
            self.average_price_for_items[current_painting] = np.mean(self.price_for_items[current_painting][-3:])
            if(bid >= self.average_price_for_items[current_painting] ):
                bid =  self.average_price_for_items[current_painting]
        return bid
        
    def check_upcoming_items(self,priority,current_painting,painting_order,current_round):
        """Updates bid if current bid is too high compared to the average price of the item
            Parameters:
                priority(float): 	Priority of the item (How important it is for us to get the item)
                current_painting(str):			The artist of the current painting that is being bid on
                painting_order(list str):		A list of the full painting order
                current_round(int): 			The current round of the auction game
            Returns:
                float:priority set based on upcoming items.
        """
        if(painting_order[current_round:].count(current_painting)) < 5:
            priority =  Priority['HIGH'].value
        return priority

    def check_priority_items(self,current_painting,my_paintings,priority,target_collection):
        """Updates priority of items
            Parameters:
                priority(float): Priority of the item (How important it is for us to get the item)
                current_painting(str): The artist of the current painting that is being bid on
                my_paintings(dict):	A dict of the paintings won so far by this bot
                target_collection(arr): Array containing information on what painings are to be collected
            Returns:
                float:priority based on the paintings collected so far compared to the target.
        """
        sorted_paintings =  np.array(sorted(my_paintings.items(), key=lambda x:x[1], reverse=True))
        if(my_paintings[current_painting] == 0):
            priority = Priority['HIGH'].value
        else:
            unique_values = np.sort(np.unique(sorted_paintings[:, 1]))[::-1]
            highest_value =  unique_values[0]
            paintings_with_highest_vals = [x for x in sorted_paintings if x[1] == highest_value]

            if(len(unique_values)>1):
                second_highest_value =  unique_values[1]
                paintings_with_second_highest_vals = [y for y in sorted_paintings if y[1] == second_highest_value]
            else:
                second_highest_value =  0
                paintings_with_second_highest_vals = []

            if(int(highest_value) < target_collection[0]):
                if(any(current_painting == a[0] for a in paintings_with_highest_vals)):
                        priority = Priority['HIGH'].value
                else:
                        priority = Priority['LOW'].value
            elif(int(second_highest_value) < target_collection[1]):
                    if(any(current_painting == b[0] for b in paintings_with_second_highest_vals)):
                        priority = Priority['HIGH'].value
                    else:
                        priority = Priority['LOW'].value
            else:
                priority = Priority['MEDIUM'].value    
        return priority      
    
    def  check_other_player_items(self,current_painting,bots,priority,target_collection):
        """If another player also needs at item, increase the priority
            Parameters:
                bots(dict): 		A dictionary holding the details of all of the bots in the auction
                priority(float): 	Priority of the item (How important it is for us to get the item)
                current_painting(str): The artist of the current painting that is being bid on
                my_bot_name(str):	Name of my current bot
            Returns:
                float:priority based on whether other players also need the item.
        """
        for bot in bots:
            highest_priority = priority
            if(bot['bot_name'] == self.name):
                continue
            else:
                player_priority = self.check_priority_items(current_painting,bot['paintings'],priority,target_collection)
                if((player_priority > Priority['LOW'].value) and (priority >= Priority['MEDIUM'].value)):
                    if(player_priority < highest_priority):
                        priority = Priority['HIGH'].value
        return priority   
    
    def get_bid(
        self,
        current_round,
        bots,
        winner_pays,
        artists_and_values,
        round_limit,
        starting_budget,
        painting_order,
        target_collection,
        my_bot_details,
        current_painting,
        winner_ids,
        amounts_paid,
    ):
        """Strategy for collection type games.

        Parameters:
        current_round(int): 			The current round of the auction game
        bots(dict): 					A dictionary holding the details of all of the bots in the auction
                                                                        For each bot, you are given these details:
                                                                        bot_name(str):		The bot's name
                                                                        bot_unique_id(str):	A unique id for this bot
                                                                        paintings(dict):	A dict of the paintings won so far by this bot
                                                                        budget(int):		How much budget this bot has left
                                                                        score(int):			Current value of paintings (for value game)
        winner_pays(int):				Rank of bid that winner plays. 1 is 1st price auction. 2 is 2nd price auction.
        artists_and_values(dict):		A dictionary of the artist names and the painting value to the score (for value games)
        round_limit(int):				Total number of rounds in the game - will always be 200
        starting_budget(int):			How much budget each bot started with - will always be 1001
        painting_order(list str):		A list of the full painting order
        target_collection(list int):	A list of the type of collection required to win, for collection games - will always be [3,2,1]
                                                                        [5] means that you need 5 of any one type of painting
                                                                        [4,2] means you need 4 of one type of painting and 2 of another
                                                                        [3,2,1] means you need 3 of one type of painting, 2 of another, and 1 of another
        my_bot_details(dict):			Your bot details. Same as in the bots dict, but just your bot.
                                                                        Includes your current paintings, current score and current budget
        current_painting(str):			The artist of the current painting that is being bid on
        winner_ids(list str):			A list of the ids of the winners of each round so far
        amounts_paid(list int):			List of amounts paid for paintings in the rounds played so far

        Returns:
        int:Your bid. Return your bid for this round.
        """

        # WRITE YOUR STRATEGY HERE FOR COLLECTION TYPE GAMES - FIRST TO COMPLETE A FULL COLLECTION
        
        # As we have a budge of 1001 we allocate approximately 165 per item (1000/6)
        # As we collect items we reconsider the strategy we are playing ie collect all 5, collect 4,2 or collect 3,2,1
        
        my_budget = my_bot_details["budget"]
        priority = Priority['LOW'].value
        my_budget = my_bot_details["budget"]
        my_paintings = my_bot_details["paintings"]
        my_id = my_bot_details["bot_unique_id"]

        # Update priority value based on the current painting and the number of paintings collected so far
        priority = self.check_priority_items(current_painting,my_paintings,priority,target_collection)
        # Update priority to bid higher if other players needs current painting and my bot also needs painting
        priority = self.check_other_player_items(current_painting,bots,priority,target_collection)
        # Update priority to bid high if there are only less than x of the paintings we need in the upcoming paintings
        priority = self.check_upcoming_items(priority,current_painting,painting_order,current_round)
        
        if winner_ids and winner_ids[-1] == my_id:
            if self.num_of_items > 2:
                self.num_of_items = self.num_of_items - 1
        
        my_budget = my_bot_details["budget"]
        budget_per_item  = abs(my_budget//self.num_of_items)
        bid = budget_per_item * priority

        # If we are bidding too high for the average price of the item then reduce the bid
        bid = self.find_average_for_previous_items(bid,current_painting,current_round,amounts_paid,priority) 

        # Only bid for high priority items when there are only <4 items left
        bid = self.only_bid_for_higher_priority(bid,priority)

        return bid
