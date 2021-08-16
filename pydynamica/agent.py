from terrain import Resources
import random

class Agent():
    def __init__(self, 
            id,
            pos = [0,0],
            speed=10, 
            consume_rate=0.1,
            money = 10,
            max_trades_per_step=10,
            collection_rate=2):

        self.age = 0
        self.id = id

        self.position = pos 
        self.speed = speed
        self.consume_rate = consume_rate
        self.max_trades_per_step = max_trades_per_step
        self.collection_rate = collection_rate

        self.wealth_food= 0
        self.wealth_minerals = 0

        self.internal_food_value = random.random() * 5
        self.internal_mineral_value = random.random() * 10

        self.unsold_discount_rate = 0.2

        # risk level determines how much an agent is willing to sell its stockpile at any given trade
        self.risk = random.uniform(0.1, 0.5)

        self.food_want_to_sell = self.wealth_food * self.risk
        self.mineral_want_to_sell = self.wealth_minerals * self.risk
        
        self.food_sold_last_round = 0
        self.mineral_sold_last_round = 0
        
        self.prev_food = self.wealth_food
        self.prev_minerals = self.wealth_minerals
        
        self.money = money

    def purchase(self, other) -> bool:
        self.food_want_to_sell = self.wealth_food * self.risk
        self.mineral_want_to_sell = self.wealth_minerals * self.risk

        purchased = False

        # it makes logical sense that the agent would consider food before he considers minerals as one is more vital than the other
        if other.internal_food_value < self.internal_food_value:
            # minimum between the total amount (in dollar value) the other agent is willing to sell vs how much money I'm willing to spend
            amount_to_purchase = min(other.internal_food_value * other.wealth_food * other.risk, 
                    self.money * self.risk)
            amount_in_units = amount_to_purchase / other.internal_food_value

            other.wealth_food -= amount_in_units
            self.wealth_food += amount_in_units
            self.food_sold_last_round = amount_in_units

            self.money -= amount_to_purchase
            other.money += amount_to_purchase
            purchased = True
        else:
            self.food_sold_last_round = 0
        
        if other.internal_mineral_value < self.internal_mineral_value:
            amount_to_purchase = min(other.internal_mineral_value * other.wealth_minerals * other.risk, 
                    self.money * self.risk)
            amount_in_units = amount_to_purchase / other.internal_food_value

            other.wealth_minerals -= amount_in_units
            self.wealth_minerals += amount_in_units
            self.mineral_sold_last_round = amount_in_units

            self.money -= amount_to_purchase
            other.money += amount_to_purchase
            purchased = True
        else:
            self.mineral_sold_last_round = 0

        return purchased
            
    def adjust_internal_value(self):
        score = self.calc_utility()
        if self.mineral_sold_last_round < self.mineral_want_to_sell:
            self.internal_mineral_value *= 1.0 - self.unsold_discount_rate
        if self.food_sold_last_round < self.food_want_to_sell:
            self.internal_food_value *= 1.0 - self.unsold_discount_rate

        # if the utility score is negative (which means that more food was consumed than earned)
        # then simply increase the internal value of food (since the agent needs it more)
        if score <= 0:
            # since minerals also increase chance of survival, its internal value is also increased
            self.internal_mineral_value *= 1.0 + self.unsold_discount_rate
            self.internal_food_value *= 1.0 + self.unsold_discount_rate

    def calc_utility(self):
        utility = (self.wealth_food - self.prev_food) - self.consume_rate
        self.prev_food = self.wealth_food
        self.prev_minerals = self.wealth_minerals
        return utility

    def check_death(self, danger):
        # if you run out of food you're dead
        if self.wealth_food <= 0:
            return True
        # minerals can save you from external danger through random chance
        if self.wealth_minerals < random.random() * danger:
            return True
        return False

    def move(self, bounds):
        xdir = round(random.random() * 2 - 1)
        ydir = round(random.random() * 2 - 1)
        
        new_x = self.position[0] + xdir * self.speed
        new_y = self.position[1] + ydir * self.speed
        if new_x < bounds[0] and new_x > 0:
            self.position[0] = new_x
        if new_y < bounds[1] and new_y > 0:
            self.position[1] = new_y

    def consume(self):
        self.wealth_food -= self.consume_rate
        self.wealth_minerals -= self.consume_rate

    def collect(self, tile):
        if tile == Resources.food:
            self.wealth_food += self.collection_rate
        if tile == Resources.mineral:
            self.wealth_minerals += self.collection_rate


    def step(self, neighbors:list, tile:Resources, bounds:list):
        # move on the map
        self.move(bounds)

        # randomly search up to 10 neighbors until a search can be made
        for _ in range(self.max_trades_per_step):
            neighbor = random.choice(neighbors)
            if self.purchase(neighbor):
                break

        self.check_death(2)
        self.collect(tile)
        self.consume()
        self.adjust_internal_value()