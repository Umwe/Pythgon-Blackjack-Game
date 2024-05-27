import requests
import cv2 as cv
import os
import matplotlib.pyplot as plt
import numpy as np
import random

card_images = []
cards = []
players = []
marks = ['Hearts', 'Spades', 'Diamonds', 'Clubs']
display_names = ['Ace', '2', '3', '4', '5', '6',
                 '7', '8', '9', '10', 'Jack', 'Queen', 'King']
numbers = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]

coins = 500  # Initial number of coins


def load_image():
    image_name = 'cards.jpg'
    vsplit_number = 4
    hsplit_number = 13

    if not os.path.isfile(image_name):
        response = requests.get(
            'http://3156.bz/techgym/cards.jpg', allow_redirects=False)
        with open(image_name, 'wb') as image:
            image.write(response.content)

    img = cv.imread('./'+image_name)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    h, w = img.shape[:2]
    crop_img = img[:h // vsplit_number * vsplit_number,
                   :w // hsplit_number * hsplit_number]

    card_images.clear()
    for h_image in np.vsplit(crop_img, vsplit_number):
        for v_image in np.hsplit(h_image, hsplit_number):
            card_images.append(v_image)


class Card:
    def __init__(self, mark, display_name, number, image):
        self.mark = mark
        self.display_name = display_name
        self.number = number
        self.image = image
        self.is_dealt = False

class Player:
    def __init__(self, name):
        self.name = name
        self.cards = []
        self.total_number = 0

class Human(Player):
    def __init__(self):
        super().__init__('You')

class Computer(Player):
    def __init__(self):
        super().__init__('Computer')

def create_cards():
    cards.clear()

    for i, mark in enumerate(marks):
        for j, number in enumerate(numbers):
            cards.append(
                Card(mark, display_names[j], number, card_images[i*len(numbers)+j]))

def show_cards(cards):
    for i, card in enumerate(cards):
        print(f"{card.display_name} of {card.mark}")
        plt.subplot(1, len(cards), i + 1)
        plt.axis('off')
        plt.imshow(card.image)
    plt.show()

def bet_coins():
    global coins
    while True:
        try:
            bet = int(input("How many coins to bet (10-100): "))
            if 10 <= bet <= 100:
                coins -= bet
                return bet
            else:
                print("Please enter a valid bet between 10 and 100.")
        except ValueError:
            print("Please enter a valid number.")

def deal_card(player):
    tmp_cards = list(filter(lambda n: n.is_dealt == False, cards))
    assert (len(tmp_cards) != 0), "No cards left"

    tmp_card = random.choice(tmp_cards)
    tmp_card.is_dealt = True

    player.cards.append(tmp_card)
    player.total_number += tmp_card.number
    calc_ace(player)
    
def calc_ace(player):
    for card in player.cards:
        if player.total_number >= 22:
            if card.number == 11:
                player.total_number -= 10
                card.number = 1


def win(bet):
    global coins
    coins += bet * 2
    show_result('win')
    print(f"You won {bet * 2} coins! Total coins: {coins}")

def lose(bet):
    global coins
    coins -= bet
    show_result('lose')
    print(f"You lost {bet} coins. Total coins: {coins}")

def choice():
    message = 'Hit[1] or stand[2]'
    choice_key = input(message)
    while not enable_choice(choice_key):
        choice_key = input(message)
    return int(choice_key)

def enable_choice(string):
    if string.isdigit():
        number = int(string)
        if number >= 1 and number <= 2:
            return True
        else:
            return False
    else:
        return False

def play_once():
    bet = bet_coins()
    deal_card(players[0])
    deal_card(players[1])
    deal_card(players[0])
    show_cards(players[0].cards)
    if is_blackjack():
        win(bet)
    else:
        choice_key = choice()
        if choice_key == 1:
            hit(bet)
        elif choice_key == 2:
            stand(bet)


def is_blackjack():
    if (players[0].total_number == 21):
        return True
    else:
        return False

def is_bust(player):
    if (player.total_number >= 22):
        return True
    else:
        return False

def hit(bet):
    deal_card(players[0])
    show_cards(players[0].cards)
    if is_blackjack():
        win(bet)
    elif is_bust(players[0]):
        lose(bet)  # Pass the bet parameter to the lose function
    else:
        choice_key = choice()
        if choice_key == 1:
            hit(bet)
        elif choice_key == 2:
            stand(bet)


def stand(bet):
    while players[1].total_number < 17:
        deal_card(players[1])

    if is_bust(players[1]):
        win(bet)
    else:
        result = judge()
        if result == 'win':
            win(bet)
        elif result == 'lose':
            lose(bet)
        else:
            show_result(result)



def judge():
    diff = players[0].total_number - players[1].total_number
    if diff == 0:
        result = 'draw'
    elif diff >= 1:
        result = 'win'
    else:
        result = 'lose'
    return result

def show_result(result):
    for player in players:
        print(f"Cards of {player.name}:")
        show_cards(player.cards)

    if result == 'draw':
        print('Draw')
    elif result == 'win':
        print(f"{players[0].name} won")
    else:
        print(f"{players[1].name} won")

def play():
    load_image()
    create_cards()
    players.append(Human())
    players.append(Computer())

    while coins >= 10:
        play_once()
        if coins < 10:
            print("You don't have enough coins to continue. Game over.")
            break

play()
