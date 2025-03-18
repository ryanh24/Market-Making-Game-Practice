import streamlit as st
import numpy as np
import random

#all the things that can change in session_state
if "setting_locked" not in st.session_state:
    st.session_state["setting_locked"] = False 

if "inputs_locked" not in st.session_state:
    st.session_state["inputs_locked"] = False

if st.session_state["inputs_locked"]:
    st.warning("Inputs are locked! Click 'Reset Game' to enable them.")

if "trade_count" not in st.session_state:
    st.session_state["trade_count"] = 0

if "net_position" not in st.session_state:
    st.session_state["net_position"] = 0

if "trade_history" not in st.session_state:
    st.session_state["trade_history"] = []

if "game_started" not in st.session_state:
    st.session_state["game_started"] = False

    st.session_state["pnl"] = 0

if "last_message" in st.session_state:
    st.info(st.session_state.last_message)

if "fermi" not in st.session_state:
    st.session_state["fermi"] = False

#question examples. Can change personally
def fermi():
    Fermi_Q = [
        {
            "things": ["balloons can fit", "tennis balls can fit", "popcorn pieces can fit", "basketballs can fit"],
            "places": ["a classroom", "a movie theater", "a cubicle"]
        },
        {
            "things": ["book stores are", "coffee stores are", "bicycles are", "gas stations are", "people are"],
            "places": ["London", "New York", "Amsterdam", "Tokyo"]
        }
            ]

    # Randomly choose a theme dict
    theme = random.choice(Fermi_Q)

    # Pick one 'thing' and one 'place'
    thing = random.choice(theme["things"])
    location = random.choice(theme["places"])
    return thing, location

def simulate_trade(bid, ask, target_value, current_position):
    diff_bid = abs(target_value - bid)
    diff_ask = abs(ask - target_value)
    if diff_bid < diff_ask: #so if the distance in bid length is not equal, 
            return "buy", bid #and closer to bid, then I buy
    elif diff_ask < diff_bid:
            return "sell", ask #closer to ask, then I sell
    elif diff_ask==diff_bid: #but if equidistant, then look at positions
        if current_position > 0:
            return "sell", ask #if I am long, as in i bought, then I sell
        elif current_position<0:
            return "buy", bid #and net short, so Ive been selling
        elif current_position==0:
            return "no trade", None #and if I am neutral AND the value is smackdab in the middle then the computer won't do anything

 
def calculate_max_loss(trade_history, V_min, V_max):
    total_buy = 0
    total_sell = 0
    num_buy = 0
    num_sell = 0
    for action, price in trade_history:
        if action == "buy":
            num_buy += 1
            total_buy += price
        elif action == "sell":
            num_sell += 1
            total_sell += price
    net_pos = num_buy - num_sell  # positive => net long, negative => net short

    # Worst-case underlying value:
    if net_pos > 0:
        worst_value = int(V_min)  # net long: worst-case is minimum value
    elif net_pos < 0:
        worst_value = int(V_max)  # net short: worst-case is maximum value
    elif net_pos == 0:
        max_loss = total_sell-total_buy
        return max_loss

    # Calculate total PNL given worst_value:
    # For each long: PNL = worst_value - buy_price
    # For each short: PNL = sell_price - worst_value
    total_pnl = net_pos * worst_value + (total_sell - total_buy)
    # If total_pnl is negative, that's your loss.
    max_loss = -total_pnl if total_pnl < 0 else 0
    return max_loss   

def start_game(game_type, trade_num, trade_type, number, type, computer_value, min_val, max_val):

    # Display the game question
    if game_type == "EV":
        if type == "fair 6-sided die":
            st.write(f"**EV Game:** We will take the product of {number} {type}.")
        else:
            st.write(f"**EV Game:** We will take the sum of {number} {type}.")     
        with st.expander("Computer value"):
                st.write(computer_value)
    else:
        thing, location = st.session_state["fermi_question"]
        st.write(f"**Fermi Game:** How many {thing} in {location}?")
        if "fermi_interval" not in st.session_state:
            st.write("Please provide your estimated interval based on your confidence interval.")
            min_val = st.number_input("Enter the lower bound", value=0, step=1, key="fermi_lower")
            max_val = st.number_input("Enter the upper bound", value=100, step=1, key="fermi_upper")
            if min_val >= max_val:
                st.error("Lower bound must be less than upper bound.")
                st.stop()
            if st.button("Submit Interval"):
                st.session_state["fermi_interval"] = (min_val, max_val)
                # Choose a computer value from the interval.
                computer_value = random.randint(round(min_val*1.1), round(max_val*0.9))
                st.session_state["computer_value"] = computer_value
                st.rerun()
            st.stop()
        else:
            st.write(f"**Fermi Game:** How many {thing} in {location}?")
            st.write(f"Your estimated interval: {st.session_state['fermi_interval']}")
            computer_value = st.session_state["computer_value"]
            with st.expander("Computer value"):
                st.write(computer_value)
            min_val, max_val = st.session_state["fermi_interval"]         

    st.write("---")
    if trade_type == "net position":
        st.write(f"**Current Net Position:** {st.session_state.net_position}")
    else:
        st.write(f"**Trade Count:** {st.session_state.trade_count} / {trade_num}")
    
    st.write("---")
    # If we haven't reached the total number of trades, show the next trade container
    if trade_type == "net position":
        continue_trading = abs(st.session_state.net_position) < trade_num
    else:
        continue_trading = st.session_state.trade_count < trade_num

    if continue_trading:
        with st.container():
            st.write("### Enter your Bid/Ask for the Next Trade")
            # Use keys that depend on the current trade count so the widgets don't clash.
            bid = st.number_input("Enter your bid", min_value=0.0, value=None, step=1.0, key=f"bid_{st.session_state.trade_count}")
            ask = st.number_input("Enter your ask", min_value=0.0, value=None, step=1.0, key=f"ask_{st.session_state.trade_count}")
            if st.button("Submit Trade", key=f"submit_{st.session_state.trade_count}") and not st.session_state.inputs_locked:
                trade_action, trade_price = simulate_trade(bid, ask, computer_value, (st.session_state.net_position))
                if trade_action == "sell":
                    st.session_state.last_message = f"Computer buys from you"
                    st.session_state.net_position -= 1  # You sell → short one contract.
                    st.session_state.trade_history.append(("sell", trade_price))
                elif trade_action == "buy":
                    st.session_state.last_message = f"Computer sells to you"
                    st.session_state.net_position += 1  # You buy → long one contract.
                    st.session_state.trade_history.append(("buy", trade_price))
                else:
                    st.session_state.last_message = ("No trade occurred.")
                st.session_state.trade_count += 1
                st.rerun()
    else:
        if trade_type ==  "net position":
            st.write(f"You have reached your maximum position, the value was {computer_value}")
        else:
            with st.container():
                st.write(f"**We are done trading, the value was {computer_value}. What was your net position?**")
                net_locked = st.session_state.get("net_locked", False)
                net_input = st.number_input("+1 for each long position, -1 for each short", value = None, key="net_input", disabled=net_locked)
                if st.button("Submit") and not net_locked:
                    st.session_state.net_locked = True
                    if net_input == st.session_state.net_position:
                        st.success("Correct!")
                    else:
                        st.error(f"Incorrect! Your position is {st.session_state.net_position}")
        with st.container():
            st.write("**What was your Max Loss possible??**")
            pnl_locked = st.session_state.get("pnl_locked", False)
            pnl_input = st.number_input("Enter your number: ", value = None, key="pnl_input", disabled=pnl_locked)
            if st.button("Submit PNL") and not pnl_locked:
                st.session_state.pnl_locked = True
                if pnl_input == calculate_max_loss(st.session_state.trade_history, min_val, max_val):
                    st.success("Correct!")
                else:
                    st.error(f"Incorrect! Your Max Loss is {calculate_max_loss(st.session_state.trade_history, min_val, max_val)}")
            
with st.sidebar:
    st.title('Settings')
    game_type = st.segmented_control("Select your gamemode", options = ["Fermi", "EV"], 
                                     default = "Fermi", disabled = st.session_state.setting_locked)
    num_obj, object_type, confidence_int, computer_value = None, None, None, None

    with st.container():
        if game_type == "Fermi":
            if "fermi_question" not in st.session_state:
                st.session_state["fermi_question"] = fermi()
            num_obj, object_type, min_val, max_val = None, None, None, None
        elif game_type == "EV":
            dice_card = st.segmented_control("Object", options = ["Dice", "Card"],
                                              default = "Dice", disabled = st.session_state.setting_locked)
            if dice_card == "Dice":
                num_obj = st.slider("Select the number of die:", min_value=0, max_value=5, 
                                                  value=3, disabled = st.session_state.setting_locked) 
                object_type = 'fair 6-sided die'
                min_val = 1
                max_val = int(6**num_obj)
                computer_value = random.randint(min_val, round(max_val*0.9))
                
            else:
                num_obj = st.slider("Select the number of cards:", min_value=0, max_value=5,
                                                  value=3, disabled = st.session_state.setting_locked)
                object_type = 'cards from a standard deck'
                min_val = num_obj
                max_val = int(13*num_obj)
                computer_value = random.randint(round(min_val*1.1), round(max_val*0.9))

    
    trades = st.segmented_control("Choose a number of trades:", options = ["Random", "Up to a +/- Position"], 
                                   default = "Random", disabled = st.session_state.setting_locked)
    with st.container():
        if trades == "Up to a +/- Position":
            trade_num = st.slider("Select a value:", min_value=0, max_value=8, 
                                   value=3, disabled = st.session_state.setting_locked)
            trade_type = 'net position'
        else:
            trade_num = random.randint(5,10) 
            trade_type = 'total trades'
    
    if st.button("Start Game"):
            st.session_state.setting_locked = True
            st.session_state.inputs_locked = False
            st.session_state.trade_count = 0
            st.session_state.net_position = 0
            st.session_state.trade_history = []
            st.session_state["game_started"] = True  # Set flag that game has started
        # Save the game settings in session_state so they can be used in main container
            st.session_state["game_settings"] = {
                "game_type": game_type,
                "trade_num": trade_num,
                "trade_type": trade_type,
                "number": num_obj,
                "type": object_type,
                "computer value": computer_value,
                "min val": min_val,
                "max val": max_val
            }
            st.rerun()

    if st.button("Reset Game"):
        st.session_state.clear()
        st.rerun()

# -------------------------------------
# Main Container: Display the Game
# -------------------------------------
st.title('Market Making Game')
st.subheader('By Ryan Har')

# Only call start_game if the game has started
if st.session_state.get("game_started", False):
    settings = st.session_state["game_settings"]
    start_game(
        settings["game_type"],
        settings["trade_num"],
        settings["trade_type"],
        settings["number"],
        settings["type"],
        settings['computer value'],
        settings['min val'],
        settings['max val']
    )
